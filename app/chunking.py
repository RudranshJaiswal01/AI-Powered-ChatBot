import tiktoken

encoder = tiktoken.get_encoding("cl100k_base")

def is_section_heading(line: str) -> bool:
    line = line.strip()

    if not line:
        return False

    if len(line) > 200:
        return False

    if line.isupper():
        return True

    if line.endswith(":"):
        return True

    if line[0].isdigit():
        return True

    return False


def chunk_text(
    text: str,
    max_tokens: int = 200,
    overlap: int = 10,
    tokens_per_page: int = 500
):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    chunks = []
    current_section = "General"
    buffer = []
    buffer_tokens = 0

    total_tokens_seen = 0
    chunk_start_tokens = 0

    for line in lines:
        if is_section_heading(line):
            print("Detected heading:", line)
            current_section = line
            continue

        tokens = len(encoder.encode(line))

        if buffer_tokens + tokens > max_tokens:
            page_start = (chunk_start_tokens // tokens_per_page) + 1
            page_end = ((chunk_start_tokens + buffer_tokens) // tokens_per_page) + 1

            chunks.append({
                "text": f"{current_section}\n" + " ".join(buffer),
                "metadata": {
                    "section": current_section,
                    "page_start": page_start,
                    "page_end": page_end
                }
            })

            # overlap
            buffer = buffer[-overlap:] if overlap else []
            buffer_tokens = len(encoder.encode(" ".join(buffer)))

            chunk_start_tokens = total_tokens_seen - buffer_tokens

        buffer.append(line)
        buffer_tokens += tokens
        total_tokens_seen += tokens

    if buffer:
        page_start = (chunk_start_tokens // tokens_per_page) + 1
        page_end = ((chunk_start_tokens + buffer_tokens) // tokens_per_page) + 1

        chunks.append({
            "text": f"{current_section}\n" + " ".join(buffer),
            "metadata": {
                "section": current_section,
                "page_start": page_start,
                "page_end": page_end
            }
        })

    return chunks
