"""
Upload routes blueprint.
Handles file upload endpoint.
"""
import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from src.middleware.auth import require_identity
from src.utils.file_utils import (
    validate_filename,
    create_upload_dir,
    canonical_path
)
from src.services.ingestion import make_id
from src.config.settings import Config

upload_bp = Blueprint('upload', __name__)

UPLOAD_BASE = Config.UPLOAD_BASE
FOLDER_SHARED = Config.FOLDER_SHARED


@upload_bp.route('/upload', methods=['POST'])
@require_identity
def upload():
    """Upload a file and save metadata for ingestion."""
    if not request.files and not request.files.get("file"):
        return jsonify({"error": "No file part in the request"}), 400

    user_id = g.identity.get("user_id", "")
    dept_id = g.identity.get("dept_id", "")
    if not user_id or not dept_id:
        return jsonify({"error": "No user ID or organization ID provided"}), 400

    f = request.files["file"]
    filename = validate_filename(f)
    if not filename:
        return jsonify({"error": "File is not valid mime type or extension"}), 400

    file_for_user = request.form.get("file_for_user", "0")
    upload_dir = create_upload_dir(dept_id, FOLDER_SHARED)
    if file_for_user == "1":
        upload_dir = create_upload_dir(dept_id, user_id)
    if not upload_dir:
        return jsonify({"error": "Failed to create upload directory"}), 500
    file_path = canonical_path(upload_dir, filename)

    # Check if same file exists
    if os.path.exists(file_path):
        return jsonify({"error": "File with the same name already exists"}), 400

    f.save(file_path)

    # Save file meta info for further ingestion
    tags = request.form.get("tags", "")
    tags_raw = json.loads(tags) if tags else []
    tags_str = ""
    if tags_raw:
        tags_str = ",".join(tags_raw) if tags_raw else ""

    file_info = {
        "file_id": make_id(filename),
        "file_path": str(file_path),
        "filename": filename,
        "source": filename,
        "ext": filename.rsplit(".", 1)[1].lower(),
        "size_kb": round(os.path.getsize(str(file_path)) / 1024, 1),
        "tags": tags_str,
        "upload_at": datetime.now().isoformat(),
        "uploaded_at_ts": datetime.now().timestamp(),
        "user_id": user_id,
        "dept_id": dept_id,
        "file_for_user": True if file_for_user == "1" else False,
        "ingested": False,
    }
    fileinfo_path = canonical_path(upload_dir, f"{filename}.meta.json")
    with open(fileinfo_path, "w", encoding="utf-8") as info_f:
        json.dump(file_info, info_f, indent=2)

    return jsonify({"msg": "File uploaded successfully"}), 200
