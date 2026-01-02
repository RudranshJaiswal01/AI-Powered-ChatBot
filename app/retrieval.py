from app.vector_db import get_collection

TOP_K = 3
MAX_DISTANCE_THRESHOLD = 1.2


def retrieve_chunks(query_embedding: list[float]) -> list[dict]:
    collection = get_collection()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []

    if not results["documents"] or not results["documents"][0]:
        return []

    for i in range(len(results["documents"][0])):
        distance = results["distances"][0][i]

        if distance > MAX_DISTANCE_THRESHOLD:
            continue

        chunks.append({
            "text": results["documents"][0][i],
            "citation": results["metadatas"][0][i]["citation"],
            "distance": distance
        })

    return chunks

def retrieve_all_chunk_summaries():
    data = collection.get(include=["metadatas"])

    summaries = []
    for meta in data["metadatas"]:
        if "chunk_summary" in meta:
            summaries.append({
                "summary": meta["chunk_summary"],
                "section": meta.get("section", "Unknown"),
                "page": meta.get("page", "Unknown")
            })

    return summaries
