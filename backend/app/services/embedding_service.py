from functools import lru_cache
from app.config import settings

@lru_cache(maxsize=1)
def model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.embedding_model, device="cpu")

def embed(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    values = model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return values.tolist()
