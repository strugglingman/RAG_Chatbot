"""Chat routes"""
from flask import Blueprint, request, jsonify, Response, g
from collections import defaultdict, deque
from openai import OpenAI
import json
import os

from src.middleware.auth import require_identity
from src.utils.sanitizer import sanitize_text
from src.services.retrieval import retrieve, build_where, build_prompt
from src.config.settings import Config
from safety import looks_like_injection, scrub_context

chat_bp = Blueprint('chat', __name__)

# Configuration
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
USE_HYBRID = os.getenv("USE_HYBRID", "false").lower() in {"1", "true", "yes", "on"}
USE_RERANKER = os.getenv("USE_RERANKER", "false").lower() in {"1", "true", "yes", "on"}
TOP_K = 5
MAX_HISTORY = 3
CHAT_MAX_TOKENS = 200

# OpenAI client
openai_client = OpenAI(api_key=OPENAI_KEY)

# Session storage
SESSIONS = defaultdict(lambda: deque(maxlen=2 * MAX_HISTORY))


def get_session_history(sid: str, n: int = 20):
    """Get sanitized session history"""
    if sid not in SESSIONS:
        return []
    
    sanitized_history = []
    for h in list(SESSIONS[sid])[-n:]:
        sanitized_msg = {
            "role": h["role"],
            "content": sanitize_text(h["content"], max_length=5000)
        }
        sanitized_history.append(sanitized_msg)
    
    return sanitized_history


@chat_bp.post('/chat')
@require_identity
def chat(collection):
    """Chat endpoint with RAG retrieval."""
    dept_id = g.identity.get('dept_id', '')
    user_id = g.identity.get('user_id', '')
    
    if not dept_id or not user_id:
        return jsonify({"error": "No organization ID or user ID provided"}), 400
    
    payload = request.get_json(force=True)
    msgs = payload.get('messages', [])
    
    sid = g.identity.get('sid', '')
    if sid not in SESSIONS:
        SESSIONS[sid] = deque(maxlen=2 * MAX_HISTORY)
    
    latest_user_msg = None
    if msgs and isinstance(msgs[-1], dict) and msgs[-1].get("role") == "user":
        latest_user_msg = msgs[-1]
    
    if not latest_user_msg:
        return jsonify({"error": "No user message found"}), 400
    if not latest_user_msg.get("content").strip():
        return jsonify({"error": "Empty user message"}), 400

    # Check for prompt injection
    injection_result, injection_error = looks_like_injection(
        latest_user_msg.get("content", "")
    )
    if injection_result:
        return jsonify({"error": f"Input rejected: {injection_error}"}), 400
    
    query = latest_user_msg.get("content").strip()
    
    try:
        # Build where clause
        where = build_where(request, dept_id, user_id)
        print(f"Where clause: {where}")
        
        # Retrieve relevant documents
        ctx, _ = retrieve(
            collection,
            query,
            dept_id=dept_id,
            user_id=user_id,
            top_k=TOP_K,
            where=where,
            use_hybrid=USE_HYBRID,
            use_reranker=USE_RERANKER,
        )

        if not ctx:
            # Append latest user message to session history even if no answer found
            if latest_user_msg:
                SESSIONS[sid].append(
                    {
                        "role": latest_user_msg.get("role"),
                        "content": latest_user_msg.get("content"),
                    }
                )
            no_answer = "Based on the provided documents, I don't have enough information to answer your question."
            SESSIONS[sid].append({"role": "assistant", "content": no_answer})
            return Response(no_answer, mimetype="text/plain")

        # Filter tags
        filters = payload.get("filters", [])
        tags_filter = next(
            (
                f.get("tags")
                for f in filters
                if "tags" in f and isinstance(f.get("tags"), list)
            ),
            None,
        )
        if tags_filter:
            ctx = [
                c
                for c in ctx
                if any(
                    tag in c.get("tags", "").lower().split(",") for tag in tags_filter
                )
            ]
        
        # Scrub context chunks before sending to LLM
        for c in ctx:
            c["chunk"] = scrub_context(c.get("chunk", ""))

        system, user = build_prompt(query, ctx, use_ctx=True)
        history = get_session_history(sid, MAX_HISTORY)
        messages = (
            [{"role": "system", "content": system}]
            + history
            + [{"role": "user", "content": user}]
        )
        messages = [
            m
            for m in messages
            if m.get("content") and m.get("role") in {"system", "user", "assistant"}
        ]

        def generate():
            answer = []
            try:
                resp = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.1,
                    max_tokens=CHAT_MAX_TOKENS,
                    stream=True,
                )

                for chunk in resp:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
                        answer.append(delta)
            except Exception as e:
                print(f"Error: {e}")
                yield f"\n[upstream_error] {type(e).__name__}: {e}"
            finally:
                # Update session history with latest query and assistant answer
                if latest_user_msg:
                    SESSIONS[sid].append(
                        {
                            "role": latest_user_msg.get("role"),
                            "content": latest_user_msg.get("content"),
                        }
                    )
                raw_answer = "".join(answer)

                if answer:
                    SESSIONS[sid].append({"role": "assistant", "content": raw_answer})

                yield f"\n__CONTEXT__:{json.dumps(ctx)}"

        return Response(generate(), mimetype="text/plain")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
    try:
        # Build where clause and retrieve context
        where = build_where_clause(dept_id, user_id, payload)
        ctx, err = retrieve_func(
            query,
            dept_id=dept_id,
            user_id=user_id,
            top_k=config.TOP_K,
            where=where,
            use_hybrid=config.USE_HYBRID,
            use_reranker=config.USE_RERANKER
        )
        
        if err:
            return jsonify({"error": err}), 500
        if not ctx:
            return jsonify({"error": "No relevant documents found"}), 404
        
        # Filter by tags
        filters = payload.get('filters', [])
        tags_filter = next((f.get("tags") for f in filters if "tags" in f and isinstance(f.get("tags"), list)), None)
        if tags_filter:
            ctx = [c for c in ctx if any(tag in c.get("tags", "").lower().split(",") for tag in tags_filter)]
        
        system, user = build_prompt_func(query, ctx, use_ctx=True)
        history = get_session_history(sid, config.MAX_HISTORY)
        messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": user}]
        messages = [m for m in messages if m.get("content") and m.get("role") in {"system", "user", "assistant"}]
        
        def generate():
            answer = []
            try:
                resp = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.1,
                    max_tokens=config.CHAT_MAX_TOKENS,
                    stream=True
                )
                
                for chunk in resp:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
                        answer.append(delta)
            except Exception as e:
                yield f"\n[upstream_error] {type(e).__name__}: {e}"
            finally:
                if latest_user_msg:
                    SESSIONS[sid].append({
                        "role": latest_user_msg.get("role"),
                        "content": latest_user_msg.get("content")
                    })
                if answer:
                    SESSIONS[sid].append({"role": "assistant", "content": ''.join(answer)})
                
                yield f"\n__CONTEXT__:{json.dumps(ctx)}"
        
        return Response(generate(), mimetype='text/plain')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def build_where_clause(dept_id: str, user_id: str, payload: dict):
    """Build where clause for vector search"""
    if not dept_id:
        raise ValueError("No organization ID provided")
    if not user_id:
        raise ValueError("No user ID provided")
    
    filters = payload.get('filters', [])
    exts = next((f.get("exts") for f in filters if "exts" in f and isinstance(f.get("exts"), list)), None)
    
    where_clauses = []
    
    if exts:
        if len(exts) == 1:
            where_clauses.append({"ext": exts[0]})
        elif len(exts) > 1:
            where_clauses.append({"$or": [{"ext": ext} for ext in exts]})
    
    where_clauses.append({"dept_id": dept_id})
    where_clauses.append({"$or": [
        {"file_for_user": False},
        {"user_id": user_id}
    ]})
    
    if len(where_clauses) > 1:
        return {"$and": where_clauses}
    elif len(where_clauses) == 1:
        return where_clauses[0]
    else:
        return None
