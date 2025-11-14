# Text Streaming Guide

## How LLM Streaming Works

When you use OpenAI's streaming API (lines 160-172 in `chat.py`):
- **Chunks are token-based**, not fixed size
- Each chunk (`delta.content`) can be:
  - 1 character: `"h"`
  - Part of a word: `"ell"`
  - A complete word: `"hello"`
  - Multiple words: `"hello world"`
- Typically **1-5 tokens per chunk**
- Tokens are linguistic units (~1-4 characters on average)
- Sent immediately as the model generates them

## Using the Stream Utility

### Basic Usage

```python
from src.utils.stream_utils import stream_text, stream_text_smart

# Example 1: Character by character (smooth but slow)
def generate_char():
    text = "Hello, this is a response from the server!"
    for chunk in stream_text(text, chunk_mode="char"):
        yield chunk

# Example 2: Word by word (natural reading experience)
def generate_word():
    text = "Hello, this is a response from the server!"
    for chunk in stream_text(text, chunk_mode="word"):
        yield chunk

# Example 3: Token-like (mimics LLM behavior) ⭐ RECOMMENDED
def generate_token_like():
    text = "Hello, this is a response from the server!"
    for chunk in stream_text(text, chunk_mode="token_like", delay_ms=20):
        yield chunk

# Example 4: Smart streaming (auto-adjusts, most realistic) ⭐ BEST
def generate_smart():
    text = "Hello, this is a response from the server!"
    for chunk in stream_text_smart(text, delay_ms=20):
        yield chunk
```

### Integration Example

Here's how to add a test endpoint to your chat routes:

```python
@chat_bp.post("/test-stream")
def test_stream():
    """Test endpoint for streaming text"""
    from src.utils.stream_utils import stream_text_smart

    test_text = """
    Based on the provided documents, here is the answer to your question.

    This is a test of the streaming functionality. It should appear
    smoothly on the frontend, character by character, just like an
    LLM response would appear.
    """

    def generate():
        for chunk in stream_text_smart(test_text.strip(), delay_ms=20):
            yield chunk

    return Response(generate(), mimetype="text/plain")
```

## Chunk Size Recommendations

| Mode | Chunk Size | Speed | Use Case |
|------|-----------|-------|----------|
| `char` (1) | 1 char | Slow | Demo/dramatic effect |
| `word` (1) | 1 word | Medium | Natural reading |
| `token_like` | 1-3 chars | Fast | Mimic LLM |
| `stream_text_smart` | 1-5 chars | Fast | **Recommended** |

## Frontend Consumption

Your frontend should handle the stream the same way it handles LLM responses:

```javascript
// Assuming you're using fetch API
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ messages: [...] })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  // Append chunk to UI
  displayMessage(chunk);
}
```

## Performance Notes

- **No delay** (`delay_ms=0`): Fastest, good for network-bound applications
- **20ms delay**: Smooth visual effect without being too slow (recommended)
- **50ms delay**: Slower, more dramatic typing effect
- **Backend streaming**: No delay needed if network latency provides natural pacing
- **Local/testing**: Add small delay (20-50ms) for visual effect

## Why Different Chunk Sizes?

1. **LLMs stream in tokens** (linguistic units), not fixed characters
2. **Variable chunk sizes feel more natural** than rigid character-by-character
3. **Word boundaries matter** for readability
4. The `stream_text_smart()` function balances all these factors

## Answer to Your Question

> "How big is each chunk? Each word, each char, or what?"

**LLM chunks are not fixed size!** They're based on:
- Token boundaries (1-4 characters typically)
- Generated in batches of 1-5 tokens usually
- Variable length strings

For your own streaming function, I recommend:
- **`stream_text_smart()`** - Best for mimicking LLM behavior
- **`chunk_mode="word"`** - If you want clean word-by-word streaming
- **`chunk_mode="char"`** - If you want the smoothest visual effect (but slower)
