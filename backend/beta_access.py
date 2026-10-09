"""Temporary two-tester beta sessions with explicit server-side logout.

Only enable behind HTTPS in a supervised beta. Sessions and rate limits are
process-local, intentionally non-persistent, and not production identity.
"""
from collections import defaultdict, deque
from html import escape
import os
import secrets
import threading
import time
from urllib.parse import parse_qs

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

_lock = threading.Lock()
_sessions = {}
_tutor_requests = defaultdict(deque)
_total_tutor_requests = deque()
SESSION_SECONDS = 4 * 3600
WINDOW_SECONDS = 3600
PER_TESTER_TUTOR_LIMIT = 12
GLOBAL_TUTOR_LIMIT = 24
COOKIE_NAME = "naijacyber_beta_session"

def beta_enabled():
    return os.getenv("BETA_MODE", "").strip() == "1"

def _credentials():
    return {
        "tester1": os.getenv("BETA_TESTER_1_PASSWORD", ""),
        "tester2": os.getenv("BETA_TESTER_2_PASSWORD", ""),
    }

def _configured():
    p = _credentials()
    return all(len(v) >= 16 for v in p.values()) and p["tester1"] != p["tester2"]

def _verify(username, password):
    valid = False
    for label, value in _credentials().items():
        match = secrets.compare_digest(username, label) and secrets.compare_digest(password, value)
        valid = valid or match
    return valid

def _lookup(token):
    if not token:
        return None
    with _lock:
        record = _sessions.get(token)
        if not record:
            return None
        username, expires = record
        if expires <= time.monotonic():
            _sessions.pop(token, None)
            return None
        return username

def _new_session(username):
    token = secrets.token_urlsafe(32)
    with _lock:
        _sessions[token] = (username, time.monotonic() + SESSION_SECONDS)
    return token

def _end_session(token):
    with _lock:
        _sessions.pop(token, None)

def _tutor_allowed(username):
    now = time.monotonic()
    with _lock:
        own = _tutor_requests[username]
        for queue in (own, _total_tutor_requests):
            while queue and queue[0] <= now - WINDOW_SECONDS:
                queue.popleft()
        if len(own) >= PER_TESTER_TUTOR_LIMIT or len(_total_tutor_requests) >= GLOBAL_TUTOR_LIMIT:
            return False
        own.append(now)
        _total_tutor_requests.append(now)
        return True

def _login_page(message=""):
    notice = '<p role="alert" style="color:#ffb4b4">' + escape(message) + '</p>' if message else ""
    return HTMLResponse("""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NaijaCyber AI — Beta sign in</title></head>
<body style="background:#080f1e;color:#e8eef8;font:16px system-ui;min-height:100vh;display:grid;place-items:center">
<main style="background:#121f34;padding:28px;border-radius:14px;max-width:380px;width:90%">
<h1>NaijaCyber AI</h1><p>Supervised beta tester sign in</p>""" + notice + """
<form action="/beta/login" method="post">
<label for="username">Username</label><input id="username" name="username" autocomplete="username"
required maxlength="40" style="display:block;width:100%;padding:10px;margin:8px 0 16px;box-sizing:border-box">
<label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password"
required style="display:block;width:100%;padding:10px;margin:8px 0 16px;box-sizing:border-box">
<button type="submit" style="padding:12px 18px;background:#38dfbd;border:0;border-radius:8px">Sign in</button>
</form><p style="font-size:13px;color:#aab9cf">Experimental learning app. Never enter real banking credentials or OTPs.</p>
</main></body></html>""", headers={"Cache-Control": "no-store"})

def _set_cookie(response, token, request):
    # Secure cookies for public HTTPS tunnels; localhost HTTP remains testable.
    host = request.url.hostname or ""
    secure = host not in ("localhost", "127.0.0.1", "testserver")
    response.set_cookie(
        COOKIE_NAME, token, max_age=SESSION_SECONDS, httponly=True,
        secure=secure, samesite="strict", path="/",
    )
    return response

def _same_origin(request):
    # Reject cross-origin browser form submissions; missing Origin/Referer
    # can occur in browser navigations and are not an authentication mechanism.
    origin = request.headers.get("origin")
    if not origin:
        return True
    try:
        from urllib.parse import urlsplit
        observed = urlsplit(origin)
        return observed.scheme in ("http", "https") and observed.netloc == request.url.netloc
    except ValueError:
        return False

class BetaAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not beta_enabled():
            return await call_next(request)
        if not _configured():
            return JSONResponse({"detail": "Beta access configuration is incomplete."}, status_code=503)
        path = request.url.path
        method = request.method
        token = request.cookies.get(COOKIE_NAME, "")
        username = _lookup(token)
        if path == "/beta/session" and method == "GET":
            return JSONResponse({"beta_mode": True, "authenticated": bool(username)},
                                headers={"Cache-Control": "no-store"})
        if path == "/beta/login" and method == "GET":
            if username:
                return RedirectResponse("/app/", status_code=303)
            return _login_page()
        if path == "/beta/login" and method == "POST":
            if not _same_origin(request):
                return JSONResponse({"detail": "Origin mismatch."}, status_code=403)
            body = await request.body()
            if len(body) > 4096:
                return _login_page("Request too large.")
            fields = parse_qs(body.decode("utf-8", errors="replace"), keep_blank_values=True)
            login_name = fields.get("username", [""])[0]
            password = fields.get("password", [""])[0]
            if not _verify(login_name, password):
                return _login_page("Incorrect username or password.")
            response = RedirectResponse("/app/", status_code=303)
            return _set_cookie(response, _new_session(login_name), request)
        if path == "/beta/logout" and method == "POST":
            if not _same_origin(request):
                return JSONResponse({"detail": "Origin mismatch."}, status_code=403)
            _end_session(token)
            response = RedirectResponse("/beta/login", status_code=303)
            response.delete_cookie(COOKIE_NAME, path="/")
            response.headers["Cache-Control"] = "no-store"
            return response
        if username is None:
            # Redirect browser navigation, reject API calls without leaking details.
            if method == "GET" and (path == "/" or path.startswith("/app")):
                return RedirectResponse("/beta/login", status_code=303)
            return JSONResponse({"detail": "Beta session required."}, status_code=401,
                                headers={"Cache-Control": "no-store"})
        if method in ("POST", "PUT", "PATCH", "DELETE") and not _same_origin(request):
            return JSONResponse({"detail": "Origin mismatch."}, status_code=403)
        if path == "/tutor" and method == "POST" and not _tutor_allowed(username):
            return JSONResponse(
                {"detail": "Beta tutor request limit reached. Contact the test coordinator."},
                status_code=429, headers={"Retry-After": "3600"},
            )
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response
