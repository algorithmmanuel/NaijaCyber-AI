"""Temporary beta sign-in, sign-out, expiry and rate-limit regressions."""
from fastapi.testclient import TestClient
from backend.main import app, natlas
from backend import beta_access

def enable(monkeypatch):
    monkeypatch.setenv("BETA_MODE", "1")
    monkeypatch.setenv("BETA_TESTER_1_PASSWORD", "test_one_password_very_long")
    monkeypatch.setenv("BETA_TESTER_2_PASSWORD", "test_two_password_very_long")
    beta_access._tutor_requests.clear()
    beta_access._total_tutor_requests.clear()
    beta_access._sessions.clear()

def login(client, username="tester1", password="test_one_password_very_long"):
    return client.post("/beta/login", data={"username": username, "password": password},
                       follow_redirects=False)

def test_beta_login_logout_and_protected_routes(monkeypatch):
    enable(monkeypatch)
    with TestClient(app) as client:
        assert client.get("/app/", follow_redirects=False).status_code == 303
        assert client.get("/missions").status_code == 401
        assert client.get("/docs").status_code == 401
        assert client.get("/beta/login").status_code == 200
        assert client.get("/beta/session").json()["authenticated"] is False
        assert "Incorrect" in login(client, password="wrong").text
        response = login(client)
        assert response.status_code == 303
        assert response.headers["location"] == "/app/"
        assert beta_access.COOKIE_NAME in client.cookies
        assert client.get("/app/").status_code == 200
        assert 'id="beta-logout"' in client.get("/app/").text
        assert client.get("/missions").status_code == 200
        assert client.get("/beta/session").json()["authenticated"] is True
        out = client.post("/beta/logout", follow_redirects=False)
        assert out.status_code == 303
        assert out.headers["location"] == "/beta/login"
        assert client.get("/beta/session").json()["authenticated"] is False
        assert client.get("/missions").status_code == 401
        assert client.get("/app/", follow_redirects=False).status_code == 303

def test_second_tester_and_revoked_cookie(monkeypatch):
    enable(monkeypatch)
    with TestClient(app) as client:
        assert login(client, "tester2", "test_two_password_very_long").status_code == 303
        old = client.cookies[beta_access.COOKIE_NAME]
        assert client.get("/missions").status_code == 200
        client.post("/beta/logout")
        client.cookies.set(beta_access.COOKIE_NAME, old)
        assert client.get("/missions").status_code == 401

def test_beta_config_fail_closed(monkeypatch):
    monkeypatch.setenv("BETA_MODE", "1")
    monkeypatch.delenv("BETA_TESTER_1_PASSWORD", raising=False)
    monkeypatch.delenv("BETA_TESTER_2_PASSWORD", raising=False)
    with TestClient(app) as client:
        assert client.get("/app/").status_code == 503

def test_rate_limits_tutor_without_calling_model(monkeypatch):
    enable(monkeypatch)
    monkeypatch.setattr(natlas, "endpoint", "")
    with TestClient(app) as client:
        assert login(client).status_code == 303
        for _ in range(12):
            result = client.post("/tutor", json={"question": "What is OTP?"})
            assert result.status_code == 200
        assert client.post("/tutor", json={"question": "What is OTP?"}).status_code == 429
        assert login(client, "tester2", "test_two_password_very_long").status_code == 303
        assert client.post("/tutor", json={"question": "What is OTP?"}).status_code == 200

def test_expired_session_denied(monkeypatch):
    enable(monkeypatch)
    with TestClient(app) as client:
        login(client)
        token = client.cookies[beta_access.COOKIE_NAME]
        user, _ = beta_access._sessions[token]
        beta_access._sessions[token] = (user, 0)
        assert client.get("/missions").status_code == 401

def test_cross_origin_logout_rejected(monkeypatch):
    enable(monkeypatch)
    with TestClient(app) as client:
        login(client)
        response = client.post("/beta/logout", headers={"Origin": "https://evil.invalid"},
                               follow_redirects=False)
        assert response.status_code == 403
        assert client.get("/missions").status_code == 200

def test_beta_disabled_normal_local_usage(monkeypatch):
    monkeypatch.setenv("BETA_MODE", "0")
    with TestClient(app) as client:
        assert client.get("/app/").status_code == 200
