CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def split_text(text: str) -> list[str]:
    if not text or not text.strip():
        return []
    return [c for c in _recursive_split(text.strip(), _SEPARATORS) if c.strip()]


def _recursive_split(text: str, separators: list[str]) -> list[str]:
    if len(text) <= CHUNK_SIZE:
        return [text]

    sep = ""
    new_separators: list[str] = []
    for i, s in enumerate(separators):
        if s == "" or s in text:
            sep = s
            new_separators = separators[i + 1:]
            break

    if sep == "":
        result = []
        start = 0
        while start < len(text):
            result.append(text[start : start + CHUNK_SIZE])
            start += CHUNK_SIZE - CHUNK_OVERLAP
        return result

    parts = text.split(sep)
    chunks: list[str] = []
    current = ""

    for part in parts:
        candidate = (current + sep + part) if current else part
        if len(candidate) <= CHUNK_SIZE:
            current = candidate
        else:
            if current:
                chunks.append(current)
                overlap_start = max(0, len(current) - CHUNK_OVERLAP)
                current = current[overlap_start:] + sep + part
                if len(current) > CHUNK_SIZE:
                    sub = _recursive_split(current, new_separators)
                    chunks.extend(sub[:-1])
                    current = sub[-1] if sub else ""
            else:
                sub = _recursive_split(part, new_separators)
                chunks.extend(sub[:-1])
                current = sub[-1] if sub else ""

    if current:
        chunks.append(current)

    return chunks
