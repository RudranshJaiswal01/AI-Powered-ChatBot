from googleapiclient.discovery import build
from google.oauth2 import service_account
from app.config import CREDENTIALS_PATH

SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]


def fetch_google_doc(document_id: str) -> str:
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=SCOPES
    )

    service = build("docs", "v1", credentials=creds)

    document = service.documents().get(
        documentId=document_id
    ).execute()

    content = document.get("body", {}).get("content", [])

    text_chunks = []
    for element in content:
        if "paragraph" not in element:
            continue

        for run in element["paragraph"].get("elements", []):
            if "textRun" in run:
                text_chunks.append(run["textRun"]["content"])

    full_text = "".join(text_chunks).strip()

    if not full_text:
        raise ValueError("The document is empty or unreadable")

    return full_text
