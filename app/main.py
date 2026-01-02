
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os

from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel
from googleapiclient.errors import HttpError

from app.ingest import fetch_google_doc
from app.utils import extract_doc_id, is_summary_query
from app.chunking import chunk_text
from app.store_chunks import store_chunks
from app.rewrite import rewrite_query
from app.retrieval import retrieve_chunks, retrieve_all_chunk_summaries
from app.generation import generate_answer, generate_document_summary
from app.embeddings import embed_texts


app = FastAPI(title="Google Doc RAG Chatbot")

# Serve legacy static and templates if needed
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Serve frontend static files (JS, CSS)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")

# ---------- Helpers ----------

def is_document_ingested() -> bool:
    from app.vector_db import collection
    data = collection.get(limit=1)
    return len(data["documents"]) > 0


# ---------- Models ----------

class ChatRequest(BaseModel):
    message: str
    history: list[str] = []

# ---------- Home Page ----------

@app.get("/", response_class=HTMLResponse)
def home():
    # Serve the frontend index.html directly
    index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/index.html"))
    return FileResponse(index_path, media_type="text/html")

# ---------- Ingest and Store Chunks ----------

@app.post("/ingest-and-store")
def ingest_and_store(doc_url: str = Query(..., description="Public Google Docs URL")):
    """
    Fetches Google Doc from user-provided link, chunks it,
    embeds it, and stores everything in ChromaDB.
    """

    try:
        doc_id = extract_doc_id(doc_url)

        text = fetch_google_doc(doc_id)

        chunks = chunk_text(text)

        if not chunks:
            raise ValueError("The document is empty")

        store_chunks(chunks)

        return {
            "status": "success",
            "total_chunks": len(chunks)
        }

    except HttpError as e:
        # Google API errors → private / permission issue
        return {
            "status": "error",
            "error_type": "PRIVATE_OR_UNREADABLE",
            "message": "The Google Doc could not be accessed. Please make sure the link is publicly shareable."
        }

    except ValueError as e:
        return {
            "status": "error",
            "error_type": "INVALID_OR_EMPTY",
            "message": str(e)
        }

    except Exception as e:
        return {
            "status": "error",
            "error_type": "UNKNOWN",
            "message": "Failed to ingest the document. Error: " + str(e)
        }

# ---------- Debug DB ----------

@app.get("/debug-db")
def debug_db():
    from app.vector_db import collection
    data = collection.get(limit=3)
    return {
        "count": len(data["documents"]),
        "sample_metadata": data["metadatas"]
    }

# ---------- Reset DB ----------

@app.post("/reset-db")
def reset_db():
    from app.vector_db import collection

    all_data = collection.get(include=[])
    ids = all_data["ids"]

    if ids:
        collection.delete(ids=ids)

    return {"status": "vector db cleared", "deleted": len(ids)}

# ---------- Chat Endpoint ----------

@app.post("/chat")
def chat(req: ChatRequest):
    """
    Full RAG chat endpoint with:
    - query rewriting
    - vector retrieval
    - similarity gating
    - strict citation-based generation
    """

    if not is_document_ingested():
        return {
            "answer": "No document has been ingested yet. Please provide a publicly shareable Google Doc link first."
        }

    # 1. Rewrite query using history
    rewritten_query = rewrite_query(req.message, req.history)

    if is_summary_query(rewritten_query):
        summaries = retrieve_all_chunk_summaries()

        if not summaries:
            return {"answer": "Could not generate a summary."}

        answer = generate_document_summary(summaries)
    else:
        # 2. Embed query (reuse HF embedding pipeline)
        query_embedding = embed_texts([rewritten_query])[0]

        # 3. Retrieve relevant chunks
        evidence = retrieve_chunks(query_embedding)

        # 4. Generate grounded answer
        answer = generate_answer(rewritten_query, evidence)

    return {"answer": answer}