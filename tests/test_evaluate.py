"""Evaluation exporter must not claim mock output is live model evidence."""
import json
from unittest.mock import patch

from tools.evaluate import run_case


class FakeResponse:
    def __init__(self, result):
        self.result = result

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_mock_response_is_unverified():
    response = FakeResponse({"provider": "mock", "answer": "Mock text"})
    with patch("tools.evaluate.urlopen", return_value=response):
        with patch("tools.evaluate.json.load", return_value=response.result):
            row = run_case("http://127.0.0.1:8000", "English", "phishing", 5)
    assert row["status"] == "unverified"
    assert row["error"]


def test_natlas_response_is_successful():
    result = {"provider": "natlas-configured", "answer": "Safe lesson", "request_id": "abc"}
    with patch("tools.evaluate.urlopen", return_value=FakeResponse(result)):
        with patch("tools.evaluate.json.load", return_value=result):
            row = run_case("http://127.0.0.1:8000", "Hausa", "mfa", 5)
    assert row["status"] == "ok"
    assert row["request_id"] == "abc"
