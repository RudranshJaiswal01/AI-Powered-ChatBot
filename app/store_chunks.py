import uuid

from app.embeddings import embed_texts
from app.summarize import summarize_chunk
from app.vector_db import get_collection

def store_chunks(chunks: list):
    collection = get_collection()

    texts = []
    metadatas = []
    ids = []

    for chunk in chunks:
        texts.append(chunk["text"])

        meta = chunk["metadata"].copy()
        meta["citation"] = (
            f"{meta['section']} (pp. {meta['page_start']}–{meta['page_end']})"
        )

        chunk_summary = summarize_chunk(chunk["text"])

        meta["chunk_summary"] = chunk_summary

        metadatas.append(meta)
        ids.append(str(uuid.uuid4()))

    embeddings = embed_texts(texts)

    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
