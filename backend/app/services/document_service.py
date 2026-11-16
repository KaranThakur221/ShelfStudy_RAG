import hashlib, json, uuid
from datetime import datetime, timezone
from pathlib import Path
from app.config import settings
from app.services.pdf_service import extract_pdf
from app.services.chunking_service import split_text
from app.services.embedding_service import embed
from app.services import vector_store

MANIFEST = settings.upload_dir / "documents.json"

def _load():
    if not MANIFEST.exists(): return {}
    try: return json.loads(MANIFEST.read_text())
    except (json.JSONDecodeError, OSError): return {}

def _save(items):
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    temp = MANIFEST.with_suffix(".tmp")
    temp.write_text(json.dumps(items, indent=2))
    temp.replace(MANIFEST)

def list_documents():
    public_fields = {"id", "filename", "pages", "chunks", "subject", "semester", "unit", "document_type", "created_at"}
    return [{key: value for key, value in item.items() if key in public_fields} for item in _load().values()]
def get_document(document_id): return _load().get(document_id)

def index_pdf(filename: str, data: bytes, metadata: dict):
    if not data.startswith(b"%PDF-"):
        raise ValueError("Only valid PDF files are accepted.")
    pages = extract_pdf(data)
    combined = []
    for page in pages:
        for i, text in enumerate(split_text(page.text, settings.chunk_size, settings.chunk_overlap)):
            combined.append((page.page, text, i))
    if not combined: raise ValueError("No indexable text was found in this PDF.")
    digest = hashlib.sha256(data).hexdigest()
    items = _load()
    for old in items.values():
        if old.get("sha256") == digest:
            return old, True
    doc_id = str(uuid.uuid4())
    chunk_ids = [f"{doc_id}:{idx}" for idx in range(len(combined))]
    chunk_texts = [x[1] for x in combined]
    vectors = embed(chunk_texts)
    metas = [{"document_id": doc_id, "filename": filename, "page": page, "chunk": i,
              "subject": metadata.get("subject") or "", "semester": metadata.get("semester") or "",
              "unit": metadata.get("unit") or "", "document_type": metadata.get("document_type") or ""}
             for page, _, i in combined]
    # Vectors are committed before the manifest/file; a failed replacement leaves existing data intact.
    vector_store.upsert(chunk_ids, chunk_texts, metas, vectors)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = settings.upload_dir / f"{doc_id}.pdf"
    file_path.write_bytes(data)
    entry = {"id": doc_id, "filename": Path(filename).name, "pages": len(pages), "chunks": len(combined),
             "subject": metadata.get("subject"), "semester": metadata.get("semester"),
             "unit": metadata.get("unit"), "document_type": metadata.get("document_type"),
             "created_at": datetime.now(timezone.utc).isoformat(), "sha256": digest, "stored_name": file_path.name}
    items[doc_id] = entry
    _save(items)
    return entry, False

def update_metadata(document_id: str, updates: dict):
    items = _load()
    if document_id not in items: return None
    clean = {k: (v.strip() if isinstance(v, str) and v.strip() else None) for k,v in updates.items()}
    vector_store.update_document_metadata(document_id, clean)
    items[document_id].update(clean)
    _save(items)
    return items[document_id]

def remove_document(document_id: str):
    items = _load()
    item = items.get(document_id)
    if not item: return False
    vector_store.delete_document(document_id)
    (settings.upload_dir / item.get("stored_name", "")).unlink(missing_ok=True)
    del items[document_id]
    _save(items)
    return True

def open_pdf_path(document_id: str):
    item = get_document(document_id)
    if not item: return None
    return settings.upload_dir / item["stored_name"]
