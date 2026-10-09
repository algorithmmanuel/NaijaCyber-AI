"""Offline dashboard tests: no live model required."""
from tools.dashboard import build_dashboard

def test_empty_dashboard():
    page = build_dashboard([])
    assert "Total cases" in page and "N/A" in page

def test_escapes_untrusted_review_content():
    page = build_dashboard([{"language": "<script>alert(1)</script>", "status": "ok",
                             "provider": "mock", "response": "example", "reviewer_notes": "<img>"}])
    assert "<script>" not in page and "&lt;script&gt;" in page
    assert "&lt;img&gt;" in page
    assert "Live successful" in page

def test_live_count_excludes_blank_and_mock():
    rows = [{"status": "ok", "provider": "mock", "response": "mock"},
            {"status": "ok", "provider": "natlas-configured", "response": ""},
            {"status": "ok", "provider": "natlas-configured", "response": "safe",
             "total_latency_seconds": 2.5}]
    page = build_dashboard(rows)
    assert "2.50s" in page
