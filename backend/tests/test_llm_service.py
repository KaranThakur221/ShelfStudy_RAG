from app.services import llm_service


class FakeCompletions:
    def __init__(self, content):
        self.content = content
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return type(
            "Response",
            (),
            {"choices": [type("Choice", (), {"message": type("Message", (), {"content": self.content})()})()]},
        )()


class FakeClient:
    def __init__(self, content):
        self.chat = type("Chat", (), {"completions": FakeCompletions(content)})()


def test_answer_uses_chat_completions(monkeypatch):
    client = FakeClient("The answer is supported by [S1].")
    monkeypatch.setattr(llm_service, "_client", lambda: client)
    sources = [{"source_id": "S1", "filename": "notes.pdf", "page": 2, "preview": "Evidence"}]

    answer, _ = llm_service.answer("What is this?", sources)

    assert answer == "The answer is supported by [S1]."
    assert client.chat.completions.kwargs["messages"][0]["role"] == "system"
    assert client.chat.completions.kwargs["messages"][1]["role"] == "user"
    assert "instructions" not in client.chat.completions.kwargs


def test_quiz_accepts_json_code_fences_and_requests_json_object(monkeypatch):
    client = FakeClient(
        """```json
        {"questions": [{"question": "What?", "options": ["A", "B", "C", "D"],
        "correct_index": 1, "explanation": "Because.", "source_id": "S1"}]}
        ```"""
    )
    monkeypatch.setattr(llm_service, "_client", lambda: client)
    sources = [{"source_id": "S1", "filename": "notes.pdf", "page": 2, "preview": "Evidence"}]

    questions = llm_service.quiz("topic", sources, 1, "easy")

    assert questions[0].correct_index == 1
    assert client.chat.completions.kwargs["response_format"] == {"type": "json_object"}
