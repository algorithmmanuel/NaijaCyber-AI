"""Temporary browser-compatible access gate for supervised two-tester beta.

Enable only when BETA_MODE=1. HTTP Basic must be used behind an HTTPS
tunnel: never send these passwords over an ordinary public HTTP connection.
The demo has process-local rate limiting, not production-grade identity.
"""
import base64
from collections import defaultdict, deque
import os
import secrets
import threading
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

_lock = threading.Lock()
_tutor_requests = defaultdict(deque)
_total_tutor_requests = deque()
WINDOW_SECONDS = 3600
PER_TESTER_TUTOR_LIMIT = 12
GLOBAL_TUTOR_LIMIT = 24

def beta_enabled():
    return os.getenv("BETA_MODE", "").strip() == "1"

def _credentials():
    return {
        "tester1": os.getenv("BETA_TESTER_1_PASSWORD", ""),
        "tester2": os.getenv("BETA_TESTER_2_PASSWORD", ""),
    }

def _login(request):
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Basic "):
        return None
    try:
        raw = base64.b64decode(auth[6:], validate=True).decode("utf-8")
        username, password = raw.split(":", 1)
    except (ValueError, UnicodeDecodeError):
        return None
    passwords = _credentials()
    valid = False
    for label, expected in passwords.items():
        # Verify both candidate credentials; do not allow blank passwords.
        match = secrets.compare_digest(username, label) and bool(expected) and (
            secrets.compare_digest(password, expected)
        )
        valid = match or valid
    return username if valid else None

def _tutor_allowed(username):
    now = time.monotonic()
    with _lock:
        own = _tutor_requests[username]
        for pending in (own, _total_tutor_requests):
            while pending and pending[0] <= now - WINDOW_SECONDS:
                pending.popleft()
        if len(own) >= PER_TESTER_TUTOR_LIMIT or len(_total_tutor_requests) >= GLOBAL_TUTOR_LIMIT:
            return False
        own.append(now)
        _total_tutor_requests.append(now)
        return True

class BetaAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not beta_enabled():
            return await call_next(request)
        passwords = _credentials()
        if not all(len(value) >= 16 for value in passwords.values()) or (
            passwords["tester1"] == passwords["tester2"]
        ):
            return JSONResponse({"detail": "Beta access configuration is incomplete."}, status_code=503)
        username = _login(request)
        if username is None:
            return Response(
                "Beta tester sign-in required.",
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="NaijaCyber Beta", charset="UTF-8"',
                         "Cache-Control": "no-store"},
            )
        if request.url.path == "/tutor" and request.method == "POST":
            if not _tutor_allowed(username):
                return JSONResponse(
                    {"detail": "Beta tutor request limit reached. Contact the test coordinator."},
                    status_code=429,
                    headers={"Retry-After": "3600"},
                )
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response
