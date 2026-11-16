from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def path_setting(name: str, default: str) -> Path:
    value = Path(os.getenv(name, default))
    return value if value.is_absolute() else (ROOT / value).resolve()

class Settings:
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    openai_model = os.getenv("OPENAI_MODEL", "nvidia/nemotron-3.5-super-vl:free")
    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    chroma_path = path_setting("CHROMA_PATH", "../data/chroma")
    upload_dir = path_setting("UPLOAD_DIR", "../data/uploads")
    top_k = max(1, min(20, int(os.getenv("TOP_K", "5"))))
    chunk_size = max(200, int(os.getenv("CHUNK_SIZE", "900")))
    chunk_overlap = max(0, min(chunk_size - 1, int(os.getenv("CHUNK_OVERLAP", "140"))))
    max_upload_mb = max(1, int(os.getenv("MAX_UPLOAD_MB", "25")))

settings = Settings()
