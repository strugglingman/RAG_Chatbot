"""Input sanitization utilities"""
import re


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """Sanitize text input to prevent prompt injection and XSS attacks."""
    if not text:
        return ""
    
    # Truncate to maximum length
    text = text[:max_length]
    
    # Remove or flag common prompt injection patterns
    injection_patterns = [
        (r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions?", "[FILTERED]"),
        (r"disregard\s+(all\s+)?(previous|above|prior)\s+instructions?", "[FILTERED]"),
        (r"forget\s+(all\s+)?(previous|above|prior)\s+instructions?", "[FILTERED]"),
        (r"you\s+are\s+now\s+(a|an)", "[FILTERED]"),
        (r"new\s+instructions?:", "[FILTERED]"),
        (r"system\s*:\s*you", "[FILTERED]"),
        (r"<\|im_start\|>", ""),
        (r"<\|im_end\|>", ""),
        (r"\[INST\]|\[/INST\]", ""),
    ]
    
    for pattern, replacement in injection_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Remove excessive newlines
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    
    return text.strip()


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and prompt injection."""
    if not text:
        return ''
    
    # Remove HTML tags and scripts
    sanitized = text
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'<[^>]+>', '', sanitized)
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
    
    # Limit length to prevent abuse
    if len(sanitized) > 10000:
        sanitized = sanitized[:10000]
    
    # Trim excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized
