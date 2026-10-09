"""Tests for the existing application; no external model or tunnel required."""

from fastapi.testclient import TestClient

from backend.main import app, natlas


client = TestClient(app)


def test_health_and_missions():
    assert client.get("/").status_code == 200
    response = client.get("/missions")
    assert response.status_code == 200
    assert len(response.json()["missions"]) == 3


def test_quiz_does_not_reveal_answer():
    response = client.get("/quiz/1")
    assert response.status_code == 200
    quiz = response.json()
    assert "correct_index" not in quiz
    assert len(quiz["options"]) == 3


def test_quiz_scoring():
    correct = client.post("/quiz/1/submit", json={"selected_index": 2})
    assert correct.status_code == 200
    assert correct.json()["score"] == 100

    wrong = client.post("/quiz/1/submit", json={"selected_index": 0})
    assert wrong.status_code == 200
    assert wrong.json()["score"] == 0

    assert client.post("/quiz/1/submit", json={"selected_index": 999}).status_code == 422
    assert client.get("/quiz/999").status_code == 404


def test_tutor_mock_mode(monkeypatch):
    # Force mock mode for reproducibility without a Colab runtime.
    monkeypatch.setattr(natlas, "endpoint", "")
    response = client.post("/tutor", json={"question": "What is phishing?"})
    assert response.status_code == 200
    assert response.json()["provider"] == "mock"
    assert response.json()["model_verified"] is False


def test_tutor_configured_provider(monkeypatch):
    async def fake_generate(question):
        return {
            "answer": "Never share an OTP.",
            "provider": "natlas-configured",
            "model": "NCAIR1/N-ATLaS",
            "model_verified": False,
        }

    monkeypatch.setattr(natlas, "endpoint", "https://example.invalid/v1/chat/completions")
    monkeypatch.setattr(natlas, "generate", fake_generate)
    response = client.post("/tutor", json={"question": "What is an OTP?"})
    assert response.status_code == 200
    assert response.json()["answer"] == "Never share an OTP."


def test_frontend_is_served():
    response = client.get("/app/")
    assert response.status_code == 200
    assert "NaijaCyber AI" in response.text
