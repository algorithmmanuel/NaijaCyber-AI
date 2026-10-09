"""Supervised-beta protection tests (offline, no live Colab required)."""
import base64

from fastapi.testclient import TestClient
from backend.main import app, natlas
from backend import beta_access

def _auth(username, password):
    raw = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": "Basic " + raw}

def _enable(monkeypatch):
    monkeypatch.setenv("BETA_MODE", "1")
    monkeypatch.setenv("BETA_TESTER_1_PASSWORD", "test_one_password_very_long")
    monkeypatch.setenv("BETA_TESTER_2_PASSWORD", "test_two_password_very_long")
    beta_access._tutor_requests.clear()
    beta_access._total_tutor_requests.clear()

def test_beta_requires_login_and_allows_both_testers(monkeypatch):
    _enable(monkeypatch)
    with TestClient(app) as client:
        unauthenticated = client.get("/app/")
        assert unauthenticated.status_code == 401
        assert "Basic " in unauthenticated.headers["www-authenticate"]
        assert client.get("/missions").status_code == 401
        assert client.get("/docs").status_code == 401
        assert client.get("/missions", headers=_auth("tester1", "wrong")).status_code == 401
        for user, password in (("tester1", "test_one_password_very_long"),
                               ("tester2", "test_two_password_very_long")):
            assert client.get("/missions", headers=_auth(user, password)).status_code == 200
            assert client.get("/app/", headers=_auth(user, password)).status_code == 200

def test_beta_config_fail_closed(monkeypatch):
    monkeypatch.setenv("BETA_MODE", "1")
    monkeypatch.delenv("BETA_TESTER_1_PASSWORD", raising=False)
    monkeypatch.delenv("BETA_TESTER_2_PASSWORD", raising=False)
    with TestClient(app) as client:
        assert client.get("/app/").status_code == 503

def test_rate_limits_tutor_without_calling_model(monkeypatch):
    _enable(monkeypatch)
    monkeypatch.setattr(natlas, "endpoint", "")
    with TestClient(app) as client:
        for _ in range(12):
            result = client.post("/tutor", headers=_auth("tester1", "test_one_password_very_long"),
                                 json={"question": "What is OTP?"})
            assert result.status_code == 200
        blocked = client.post("/tutor", headers=_auth("tester1", "test_one_password_very_long"),
                              json={"question": "What is OTP?"})
        assert blocked.status_code == 429
        assert client.post("/tutor", headers=_auth("tester2", "test_two_password_very_long"),
                           json={"question": "What is OTP?"}).status_code == 200

def test_beta_disabled_normal_local_usage(monkeypatch):
    monkeypatch.setenv("BETA_MODE", "0")
    with TestClient(app) as client:
        assert client.get("/app/").status_code == 200
