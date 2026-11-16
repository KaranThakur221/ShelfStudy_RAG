from functools import lru_cache
import chromadb
from app.config import settings

@lru_cache(maxsize=1)
def collection():
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(settings.chroma_path))
    return client.get_or_create_collection("studyshelf", metadata={"hnsw:space": "cosine"})

def upsert(ids, documents, metadatas, embeddings):
    collection().upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

def delete_document(document_id: str):
    collection().delete(where={"document_id": document_id})

def update_document_metadata(document_id: str, updates: dict):
    coll = collection()
    found = coll.get(where={"document_id": document_id}, include=["metadatas"])
    if found["ids"]:
        metadatas = []
        for meta in found["metadatas"]:
            updated = dict(meta)
            for key, value in updates.items():
                if value is not None:
                    updated[key] = value
                else:
                    updated.pop(key, None)
            metadatas.append(updated)
        coll.update(ids=found["ids"], metadatas=metadatas)

def search(query_embedding, limit: int, subject=None, unit=None):
    filters = []
    if subject:
        filters.append({"subject": subject})
    if unit:
        filters.append({"unit": unit})
    where = filters[0] if len(filters) == 1 else ({"$and": filters} if filters else None)
    return collection().query(query_embeddings=[query_embedding], n_results=limit,
                              where=where, include=["documents", "metadatas", "distances"])
