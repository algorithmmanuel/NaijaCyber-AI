
# ============================================================
# NAIJACYBER AI - N-ATLaS PROVIDER
# Connects local FastAPI to the authenticated Colab model API
# ============================================================

import os
import time

import httpx


MODEL_ID = "NCAIR1/N-ATLaS"


class NatlasError(Exception):
    """Raised when N-ATLaS inference fails."""
    pass


class NatlasProvider:

    def __init__(self):

        self.endpoint = os.getenv(
            "NATLAS_CHAT_URL", ""
        ).strip()

        self.api_key = os.getenv(
            "NATLAS_API_KEY", ""
        ).strip()

        self.model = os.getenv(
            "NATLAS_MODEL_ID", MODEL_ID
        ).strip()

        if self.endpoint and (
            not self.endpoint.startswith("https://")
            or not self.api_key
            or len(self.api_key) < 32
        ):
            raise NatlasError(
                "N-ATLaS requires an HTTPS endpoint "
                "and an API key of at least 32 characters."
            )

    @property
    def available(self):
        """Indicates whether an inference endpoint is configured."""
        return bool(self.endpoint)

    async def generate(self, question: str):

        if not self.available:
            raise NatlasError(
                "N-ATLaS inference endpoint is not configured."
            )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are NaijaCyber AI, a cybersecurity "
                        "tutor for Nigerian beginners. "
                        "Explain concepts clearly and accurately. "
                        "Use the language requested by the user. "
                        "Never ask for passwords, PINs or OTPs. "
                        "Use safe cybersecurity examples."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            "temperature": 0.0,
            "max_tokens": 320
        }

        started = time.perf_counter()

        try:
            async with httpx.AsyncClient(
                timeout=120.0,
                follow_redirects=False,
                trust_env=False
            ) as client:

                response = await client.post(
                    self.endpoint,
                    headers=headers,
                    json=payload
                )

                response.raise_for_status()
                result = response.json()

            if result.get("model") != self.model:
                raise NatlasError(
                    "Unexpected model identity in response."
                )

            content = result["choices"][0]["message"]["content"]

            if not isinstance(content, str) or not content.strip():
                raise NatlasError(
                    "Model returned an empty response."
                )

            elapsed_ms = round(
                (time.perf_counter() - started) * 1000,
                2
            )

            return {
                "answer": content.strip(),
                "provider": "natlas-configured",
                "model": self.model,
                "latency_ms": elapsed_ms,
                "model_verified": False,
                "inference_seconds": result.get(
                    "inference_seconds"
                ),
                "completion_tokens": result.get(
                    "usage", {}
                ).get("completion_tokens")
            }

        except httpx.TimeoutException as exc:
            raise NatlasError(
                "N-ATLaS inference timed out. "
                "Check whether Colab is still connected."
            ) from exc

        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code

            raise NatlasError(
                f"N-ATLaS server returned HTTP {status}. "
                "Check authentication and server availability."
            ) from exc

        except httpx.RequestError as exc:
            raise NatlasError(
                "Cannot connect to N-ATLaS. "
                "Check the ngrok URL and Colab runtime."
            ) from exc

        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise NatlasError(
                "N-ATLaS returned an unexpected response format."
            ) from exc
