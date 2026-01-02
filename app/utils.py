import re

def extract_doc_id(doc_url: str) -> str:
    """
    Extracts the document ID from a Google Docs URL.

    Raises:
        ValueError: if the URL is invalid or ID not found.
    """
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", doc_url)
    if not match:
        raise ValueError("Invalid Google Docs URL")

    return match.group(1)

def is_summary_query(query: str) -> bool:
    triggers = [
        "summarize",
        "summary",
        "overview",
        "high level",
        "what is this document about",
        "entire document"
    ]
    q = query.lower()
    return any(t in q for t in triggers)
