"""Second-iteration evaluation and prompt regression checks."""
from backend.natlas_provider import NatlasProvider
from tools.compare_evaluations import compare, summarize

def test_comparison_avoids_quality_claims():
    a = [{"language": "English", "topic": "otp", "status": "ok",
          "provider": "natlas-configured", "response": "Use care.",
          "completion_tokens": 320, "total_latency_seconds": 22.0}]
    b = [{**a[0], "completion_tokens": 120, "total_latency_seconds": 12.0}]
    result = compare(a, b)
    assert result["same_case_keys"]
    assert result["baseline"]["possible_token_limit_hits"] == 1
    assert result["candidate"]["possible_token_limit_hits"] == 0
    assert result["baseline"]["human_reviewed"] == 0
    assert "human reviews" in result["warning"]

def test_mock_cannot_count_as_live():
    assert summarize([{"status": "ok", "provider": "mock", "response": "mock"}])["live_successes"] == 0

def test_system_prompt_preserves_multilingual_security_principles(monkeypatch):
    import httpx
    import pytest
    import asyncio
    monkeypatch.setenv("NATLAS_CHAT_URL", "https://example.invalid/v1/chat/completions")
    monkeypatch.setenv("NATLAS_API_KEY", "x" * 40)
    provider = NatlasProvider()
    original = httpx.AsyncClient
    seen = {}
    def handler(request):
        seen.update(__import__("json").loads(request.content))
        return httpx.Response(200, json={
            "model": provider.model, "choices": [{"message": {"content": "Never share an OTP."}}]})
    def factory(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return original(*args, **kwargs)
    monkeypatch.setattr("backend.natlas_provider.httpx.AsyncClient", factory)
    asyncio.run(provider.generate("Explain MFA in Yoruba"))
    prompt = seen["messages"][0]["content"]
    assert "Hausa" in prompt and "Igbo" in prompt and "Yoruba" in prompt
    assert "NOT MFA" in prompt and "OTP" in prompt
    assert seen["max_tokens"] == 320
