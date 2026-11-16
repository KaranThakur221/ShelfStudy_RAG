from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import documents, chat, quizzes

app = FastAPI(title="StudyShelf API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"], allow_credentials=False, allow_methods=["GET","POST","PATCH","DELETE"], allow_headers=["Content-Type"])
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(quizzes.router)

@app.get("/api/health")
def health():
    return {"status":"ok", "llm_configured":bool(settings.openai_api_key), "model":settings.openai_model,
            "documents":len(__import__("app.services.document_service", fromlist=["list_documents"]).list_documents())}
