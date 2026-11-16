from fastapi import APIRouter, HTTPException
from app.schemas import ChatRequest, ExamRequest, AnswerResponse
from app.services.retrieval_service import retrieve
from app.services.llm_service import answer, LLMError

router = APIRouter(prefix="/api", tags=["study"])

def _run(question, subject, unit, top_k, marks=None):
    try:
        sources = retrieve(question, top_k, subject, unit)
        text, sources = answer(question, sources, marks)
        return AnswerResponse(answer=text, sources=[{k:s[k] for k in ("source_id","filename","page","preview","document_id")} for s in sources])
    except LLMError as exc: raise HTTPException(503, str(exc)) from exc
    except Exception as exc: raise HTTPException(503, "Retrieval is unavailable. Check that local embeddings and the index are ready.") from exc

@router.post("/chat", response_model=AnswerResponse)
def chat(body: ChatRequest): return _run(body.question, body.subject, body.unit, body.top_k)

@router.post("/exam-answer", response_model=AnswerResponse)
def exam_answer(body: ExamRequest): return _run(body.question, body.subject, body.unit, body.top_k, body.marks)
