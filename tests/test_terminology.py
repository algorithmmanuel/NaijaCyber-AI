"""Grounding and observed-error regression tests; no live GPU required."""
import json
import httpx
import pytest
from backend.terminology import detect_topic, reference_for_question, response_warnings
from backend.natlas_provider import NatlasProvider

def test_topic_routing():
    assert detect_topic("Explain MFA in Yoruba") == "mfa"
    assert detect_topic("What is an OTP?") == "otp"
    assert detect_topic("Recognise a phishing message") == "phishing"
    assert detect_topic("How do I protect my laptop?") is None

def test_mfa_grounding():
    guidance = reference_for_question("Explain MFA in Igbo")
    for required in ("TWO DIFFERENT", "password plus security question", "telephone number", "OTP"):
        if required == "OTP":
            assert required in guidance
        else:
            assert required in guidance

def test_regression_flags_observed_terminology():
    assert "yoruba_three_factor_wording_review" in response_warnings(
        "Ìdánimọ̀ mẹta", "mfa", 120)
    assert "igbo_username_claim_review" in response_warnings(
        "naanị aha njirimara gị.", "mfa", 120)
    assert "otp_terminology_review" in response_warnings(
        "Owo-igba kan.", "otp", 120)
    assert "possibly_incomplete_ending" in response_warnings(
        "unfinished sentence", "mfa", 320)
    assert response_warnings("Never share an OTP.", "otp", 30) == []

@pytest.mark.asyncio
async def test_provider_injects_references_and_surfaces_warnings(monkeypatch):
    monkeypatch.setenv("NATLAS_CHAT_URL", "https://example.invalid/v1/chat/completions")
    monkeypatch.setenv("NATLAS_API_KEY", "x"*40)
    provider = NatlasProvider()
    original = httpx.AsyncClient
    captured = {}
    def handler(request):
        captured.update(json.loads(request.content))
        return httpx.Response(200, json={"model": provider.model,
            "choices":[{"message":{"content":"Ìdánimọ̀ mẹta"}}],
            "usage":{"completion_tokens":320}})
    def factory(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return original(*args, **kwargs)
    monkeypatch.setattr("backend.natlas_provider.httpx.AsyncClient", factory)
    result = await provider.generate("Explain MFA in Yoruba")
    assert result["topic"] == "mfa"
    assert "yoruba_three_factor_wording_review" in result["review_warnings"]
    assert "possible_token_limit" in result["review_warnings"]
    assert "TWO DIFFERENT" in captured["messages"][0]["content"]
    assert result["answer"] == "Ìdánimọ̀ mẹta"
