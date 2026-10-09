"""Authenticated N-ATLaS inference adapter with bounded transient-error retries."""
import asyncio
import logging
import os
import time
import uuid

import httpx

from backend.terminology import detect_topic, reference_for_question, response_warnings

MODEL_ID = "NCAIR1/N-ATLaS"
RETRYABLE_STATUS = {429, 502, 503, 504}
MAX_ATTEMPTS = 3
TOTAL_BUDGET_SECONDS = 120.0
PER_ATTEMPT_SECONDS = 40.0
logger = logging.getLogger(__name__)


class NatlasError(Exception):
    """Safe public-facing N-ATLaS provider failure."""


class NatlasProvider:
    def __init__(self):
        self.endpoint = os.getenv("NATLAS_CHAT_URL", "").strip()
        self.api_key = os.getenv("NATLAS_API_KEY", "").strip()
        self.model = os.getenv("NATLAS_MODEL_ID", MODEL_ID).strip()
        if self.endpoint and (
            not self.endpoint.startswith("https://")
            or not self.api_key
            or len(self.api_key) < 32
        ):
            raise NatlasError(
                "N-ATLaS requires an HTTPS endpoint and an API key of at least 32 characters."
            )

    @property
    def available(self):
        return bool(self.endpoint)

    async def generate(self, question: str):
        if not self.available:
            raise NatlasError("N-ATLaS inference endpoint is not configured.")

        request_id = uuid.uuid4().hex
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Request-ID": request_id,
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are NaijaCyber AI, a careful cybersecurity tutor for "
                        "Nigerian beginners. Reply in the language requested. "
                        "Use two to three short complete sentences: explain the concept, "
                        "why it matters, and one safe practical action. "
                        "Never ask users to disclose passwords, PINs or OTPs. "
                        "Do not invent definitions or claim absolute protection. "
                        + reference_for_question(question)
                    ),
                },
                {"role": "user", "content": question},
            ],
            "temperature": 0.0,
            "max_tokens": 320,
        }
        started = time.monotonic()
        async with httpx.AsyncClient(
            timeout=PER_ATTEMPT_SECONDS,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            for attempt in range(MAX_ATTEMPTS):
                remaining = TOTAL_BUDGET_SECONDS - (time.monotonic() - started)
                if remaining <= 0:
                    break
                try:
                    response = await client.post(
                        self.endpoint,
                        headers=headers,
                        json=payload,
                        timeout=min(PER_ATTEMPT_SECONDS, remaining),
                    )
                    # Retry only known transient statuses; authentication and request errors fail fast.
                    if response.status_code in RETRYABLE_STATUS:
                        if attempt + 1 == MAX_ATTEMPTS:
                            raise NatlasError(
                                f"N-ATLaS temporarily unavailable (HTTP {response.status_code}). "
                                f"Request ID: {request_id}"
                            )
                        delay = min(2 ** attempt, 4.0)
                        if delay >= TOTAL_BUDGET_SECONDS - (time.monotonic() - started):
                            break
                        logger.warning(
                            "N-ATLaS transient HTTP %s; retry %s; request_id=%s",
                            response.status_code, attempt + 1, request_id,
                        )
                        await asyncio.sleep(delay)
                        continue
                    response.raise_for_status()
                    try:
                        result = response.json()
                        if not isinstance(result, dict):
                            raise ValueError("non-object result")
                        if result.get("model") != self.model:
                            raise NatlasError(
                                f"Unexpected model identity in response. Request ID: {request_id}"
                            )
                        content = result["choices"][0]["message"]["content"]
                        if not isinstance(content, str) or not content.strip():
                            raise NatlasError(
                                f"Model returned an empty response. Request ID: {request_id}"
                            )
                        usage = result.get("usage") or {}
                        if not isinstance(usage, dict):
                            usage = {}
                    except (ValueError, KeyError, IndexError, TypeError) as exc:
                        raise NatlasError(
                            f"N-ATLaS returned an unexpected response format. Request ID: {request_id}"
                        ) from exc
                    elapsed_ms = round((time.monotonic() - started) * 1000, 2)
                    logger.info("N-ATLaS success request_id=%s latency_ms=%s", request_id, elapsed_ms)
                    return {
                        "answer": content.strip(),
                        "provider": "natlas-configured",
                        "model": self.model,
                        "latency_ms": elapsed_ms,
                        "model_verified": False,
                        "inference_seconds": result.get("inference_seconds"),
                        "completion_tokens": usage.get("completion_tokens"),
                        "request_id": request_id,
                        "topic": detect_topic(question),
                        "review_warnings": response_warnings(
                            content, detect_topic(question), usage.get("completion_tokens")
                        ),
                    }
                except httpx.HTTPStatusError as exc:
                    raise NatlasError(
                        f"N-ATLaS server returned HTTP {exc.response.status_code}. "
                        f"Request ID: {request_id}"
                    ) from exc
                except httpx.TimeoutException as exc:
                    raise NatlasError(
                        f"N-ATLaS inference timed out. Request ID: {request_id}"
                    ) from exc
                except httpx.RequestError as exc:
                    raise NatlasError(
                        f"Cannot connect to N-ATLaS. Request ID: {request_id}"
                    ) from exc
        raise NatlasError(f"N-ATLaS inference time budget exhausted. Request ID: {request_id}")
