from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_does_not_expose_api_key(monkeypatch):
    monkeypatch.setattr("app.main.settings.openai_api_key", "super-secret-value")
    data = client.get("/api/health").json()
    assert data["llm_configured"] is True
    assert "super-secret-value" not in str(data)

def test_invalid_upload_is_rejected_without_indexing():
    response = client.post("/api/documents/upload", files={"file": ("notes.txt", b"not pdf", "text/plain")})
    assert response.status_code == 415
    assert "PDF" in response.json()["detail"]

def test_bad_exam_request_returns_validation_error():
    response = client.post("/api/exam-answer", json={"question":"Explain a concept", "marks":3})
    assert response.status_code == 422
