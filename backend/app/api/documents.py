from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.config import settings
from app.schemas import MetadataUpdate
from app.services import document_service

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("")
def documents():
    return document_service.list_documents()

@router.post("/upload")
async def upload(file: UploadFile = File(...), subject: str | None = Form(None), semester: str | None = Form(None), unit: str | None = Form(None), document_type: str | None = Form(None)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(415, "Please upload a PDF file.")
    data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"PDF exceeds the {settings.max_upload_mb} MB upload limit.")
    try:
        doc, duplicate = document_service.index_pdf(file.filename, data, {"subject":subject,"semester":semester,"unit":unit,"document_type":document_type})
        public_fields = ("id", "filename", "pages", "chunks", "subject", "semester", "unit", "document_type", "created_at")
        return {**{key: doc.get(key) for key in public_fields}, "duplicate": duplicate}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        # Do not disclose paths, tokens, or implementation details.
        raise HTTPException(503, "Indexing failed. Check that the local embedding model is available, then try again.") from exc

@router.delete("/{document_id}")
def delete_document(document_id: str):
    if not document_service.remove_document(document_id): raise HTTPException(404, "Document not found.")
    return {"deleted": True}

@router.patch("/{document_id}/metadata")
def update_metadata(document_id: str, body: MetadataUpdate):
    item = document_service.update_metadata(document_id, body.model_dump(exclude_unset=True))
    if not item: raise HTTPException(404, "Document not found.")
    return item

@router.get("/{document_id}/file")
def pdf_file(document_id: str):
    path = document_service.open_pdf_path(document_id)
    if path is None or not path.is_file(): raise HTTPException(404, "Document file not found.")
    return FileResponse(path, media_type="application/pdf", filename=path.name, content_disposition_type="inline")
