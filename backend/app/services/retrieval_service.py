from app.config import settings
from app.services.embedding_service import embed
from app.services import vector_store

def retrieve(query: str, top_k=None, subject=None, unit=None):
    result = vector_store.search(embed([query])[0], top_k or settings.top_k, subject, unit)
    sources = []
    if not result["ids"] or not result["ids"][0]: return sources
    for idx, (chunk_id, text, meta, distance) in enumerate(zip(result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]), 1):
        sources.append({"source_id": f"S{idx}", "filename": meta["filename"], "page": int(meta["page"]),
                        "preview": text, "document_id": meta["document_id"], "chunk_id": chunk_id,
                        "distance": distance})
    return sources
