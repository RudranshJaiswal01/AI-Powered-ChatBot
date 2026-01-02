# app/vector_db.py
import chromadb
from chromadb.config import Settings

PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "google_doc_chunks"

_client = chromadb.Client(
    Settings(
        persist_directory=PERSIST_DIR,
        anonymized_telemetry=False
    )
)

def get_collection():
    return _client.get_or_create_collection(COLLECTION_NAME)

def reset_collection():
    try:
        _client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
