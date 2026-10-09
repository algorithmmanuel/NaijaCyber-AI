"""Deterministic N-ATLaS provider tests using HTTPX's mock transport."""
import json

import httpx
import pytest

from backend.natlas_provider import NatlasError, NatlasProvider


def configured(monkeypatch):
    monkeypatch.setenv("NATLAS_CHAT_URL", "https://example.invalid/v1/chat/completions")
    monkeypatch.setenv("NATLAS_API_KEY", "x" * 40)
    return NatlasProvider()


def install_mock(monkeypatch, handler):
    original = httpx.AsyncClient
    def client_factory(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return original(*args, **kwargs)
    monkeypatch.setattr("backend.natlas_provider.httpx.AsyncClient", client_factory)


@pytest.mark.asyncio
async def test_provider_success(monkeypatch):
    provider = configured(monkeypatch)
    def handler(request):
        assert request.headers["authorization"] == "Bearer " + "x" * 40
        assert request.headers["x-request-id"]
        return httpx.Response(200, json={
            "model": provider.model, "choices": [{"message": {"content": "Protect your OTP."}}],
            "usage": {"completion_tokens": 5}
        })
    install_mock(monkeypatch, handler)
    answer = await provider.generate("What is an OTP?")
    assert answer["answer"] == "Protect your OTP."
    assert answer["completion_tokens"] == 5
    assert answer["model_verified"] is False


@pytest.mark.asyncio
async def test_transient_retry_then_success(monkeypatch):
    provider = configured(monkeypatch)
    status = [503, 429, 200]
    def handler(request):
        current = status.pop(0)
        return httpx.Response(current, json={
            "model": provider.model, "choices": [{"message": {"content": "Safe advice"}}]
        })
    install_mock(monkeypatch, handler)
    async def no_wait(_):
        return None
    monkeypatch.setattr("backend.natlas_provider.asyncio.sleep", no_wait)
    assert (await provider.generate("Explain MFA"))["answer"] == "Safe advice"
    assert not status


@pytest.mark.asyncio
async def test_auth_error_never_retried_or_leaked(monkeypatch):
    provider = configured(monkeypatch)
    calls = []
    def handler(request):
        calls.append(1)
        return httpx.Response(401, text="sensitive downstream body")
    install_mock(monkeypatch, handler)
    with pytest.raises(NatlasError) as exc:
        await provider.generate("Explain MFA")
    assert len(calls) == 1
    assert "401" in str(exc.value)
    assert "sensitive" not in str(exc.value)
    assert "x" * 40 not in str(exc.value)


@pytest.mark.asyncio
async def test_rejects_wrong_model(monkeypatch):
    provider = configured(monkeypatch)
    install_mock(monkeypatch, lambda request: httpx.Response(200, json={
        "model": "other-model", "choices": [{"message": {"content": "hi"}}]
    }))
    with pytest.raises(NatlasError, match="Unexpected model identity"):
        await provider.generate("Hi")


@pytest.mark.asyncio
async def test_rejects_empty_result(monkeypatch):
    provider = configured(monkeypatch)
    install_mock(monkeypatch, lambda request: httpx.Response(200, json={
        "model": provider.model, "choices": [{"message": {"content": "  "}}]
    }))
    with pytest.raises(NatlasError, match="empty response"):
        await provider.generate("Hi")
