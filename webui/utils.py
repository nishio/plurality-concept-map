import re, json, unicodedata

def normalize_label(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[^\w\s\-]+","",s)
    s = re.sub(r"\s+"," ",s).strip()
    return s

def slugify_id(s: str) -> str:
    s = normalize_label(s)
    s = s.replace(" ","_")
    # Allow Japanese characters, alphanumeric, underscore, and hyphen
    s = re.sub(r"[^\w\-]","",s, flags=re.UNICODE)
    return s[:48] if s else ""

def extract_json_block(text: str):
    """Extract first top-level JSON object or array from text."""
    if not text:
        return None
    stack = []
    start = None
    for i, ch in enumerate(text):
        if ch in "{[":
            if not stack:
                start = i
            stack.append(ch)
        elif ch in "}]":
            if not stack: 
                continue
            opener = stack.pop()
            if not stack and start is not None:
                block = text[start:i+1]
                try:
                    return json.loads(block)
                except Exception:
                    continue
    return None
