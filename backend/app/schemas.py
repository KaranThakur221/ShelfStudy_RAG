from typing import Literal
from pydantic import BaseModel, Field, field_validator

class DocumentOut(BaseModel):
    id: str
    filename: str
    pages: int
    chunks: int
    subject: str | None = None
    semester: str | None = None
    unit: str | None = None
    document_type: str | None = None
    created_at: str

class MetadataUpdate(BaseModel):
    subject: str | None = Field(default=None, max_length=120)
    semester: str | None = Field(default=None, max_length=80)
    unit: str | None = Field(default=None, max_length=120)
    document_type: str | None = Field(default=None, max_length=80)

class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    subject: str | None = None
    unit: str | None = None
    top_k: int | None = Field(default=None, ge=1, le=20)

class Source(BaseModel):
    source_id: str
    filename: str
    page: int
    preview: str
    document_id: str

class AnswerResponse(BaseModel):
    answer: str
    sources: list[Source]

class ExamRequest(ChatRequest):
    marks: Literal[2, 5, 10]

class QuizRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=300)
    subject: str | None = None
    unit: str | None = None
    count: int = Field(default=5, ge=1, le=15)
    difficulty: Literal["easy", "medium", "hard"] = "medium"

class QuizQuestion(BaseModel):
    question: str = Field(min_length=4)
    options: list[str]
    correct_index: int = Field(ge=0, le=3)
    explanation: str
    source_id: str

    @field_validator("options")
    @classmethod
    def four_options(cls, value):
        if len(value) != 4 or any(not x.strip() for x in value):
            raise ValueError("Each question must have exactly four non-empty options")
        return value

class QuizResponse(BaseModel):
    questions: list[QuizQuestion]
    sources: list[Source]
