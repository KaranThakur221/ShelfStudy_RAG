import pytest
from pydantic import ValidationError
from app.services.chunking_service import split_text
from app.services.pdf_service import extract_pdf
from app.schemas import QuizQuestion, ExamRequest
from app.services.llm_service import answer, LLMError


def synthetic_pdf():
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Dijkstra's algorithm finds shortest paths from a source vertex in a graph with non-negative edge weights.")
    page = doc.new_page()
    page.insert_text((72, 72), "An AVL tree is a self-balancing binary search tree.")
    data = doc.tobytes()
    doc.close()
    return data


def test_pdf_extraction_preserves_page_numbers():
    pages = extract_pdf(synthetic_pdf())
    assert [p.page for p in pages] == [1, 2]
    assert "Dijkstra" in pages[0].text
    assert "AVL" in pages[1].text


def test_pdf_invalid_and_empty_errors():
    with pytest.raises(ValueError, match="valid PDF"):
        extract_pdf(b"nope")
    doc = __import__('fitz').open()
    doc.new_page()
    data = doc.tobytes()
    doc.close()
    with pytest.raises(ValueError, match="No selectable text"):
        extract_pdf(data)


def test_chunking_overlap_and_empty():
    chunks = split_text("one two three four five six", 3, 1)
    assert chunks == ["one two three", "three four five", "five six"]
    assert split_text("  ", 10, 2) == []


def test_quiz_schema_requires_four_options_and_valid_index():
    base = dict(question="What is AVL?", options=["A", "B", "C", "D"], correct_index=0,
                explanation="Because the note says so.", source_id="S1")
    assert QuizQuestion(**base).correct_index == 0
    with pytest.raises(ValidationError): QuizQuestion(**{**base, "options":["A", "B"]})
    with pytest.raises(ValidationError): QuizQuestion(**{**base, "correct_index":4})


def test_exam_request_validates_mark_values():
    assert ExamRequest(question="Explain AVL trees", marks=10).marks == 10
    with pytest.raises(ValidationError): ExamRequest(question="Explain AVL trees", marks=3)


def test_answer_rejects_unknown_citation_ids(monkeypatch):
    monkeypatch.setattr("app.services.llm_service._completion", lambda *_, **__: "It does this [S99, p. 800] and that [S1, p. 2].")
    sources = [{"source_id":"S1", "filename":"notes.pdf", "page":2, "preview":"AVL trees balance subtrees.", "document_id":"doc"}]
    text, returned = answer("Explain AVL", sources)
    assert "S99" not in text
    assert "[S1]" in text
    assert "p. 2" not in text
    assert returned == sources


def test_insufficient_sources_does_not_call_llm(monkeypatch):
    monkeypatch.setattr("app.services.llm_service._completion", lambda *_, **__: pytest.fail("LLM should not be called"))
    text, sources = answer("anything", [])
    assert "do not provide enough information" in text
    assert sources == []
