from fastapi import APIRouter, HTTPException
from app.schemas import QuizRequest, QuizResponse
from app.services.retrieval_service import retrieve
from app.services.llm_service import quiz, LLMError

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

@router.post("/generate", response_model=QuizResponse)
def generate(body: QuizRequest):
    try:
        sources = retrieve(body.topic, subject=body.subject, unit=body.unit)
        questions = quiz(body.topic, sources, body.count, body.difficulty)
        safe_sources = [{k:s[k] for k in ("source_id","filename","page","preview","document_id")} for s in sources]
        return QuizResponse(questions=questions, sources=safe_sources)
    except LLMError as exc: raise HTTPException(503, str(exc)) from exc
    except Exception as exc: raise HTTPException(503, "Quiz generation is unavailable. Check local embeddings and your model configuration.") from exc
