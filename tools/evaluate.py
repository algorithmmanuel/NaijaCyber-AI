"""Run a small, reproducible N-ATLaS cybersecurity evaluation via /tutor.

This CLI is a development tool, not a validated language-quality benchmark.
It sends only synthetic prompts and saves JSON/CSV for independent human review.
"""

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


TOPICS = {
    "phishing": "Explain how a banking customer should recognise a suspicious account-verification message.",
    "otp": "Explain why a banking customer must not disclose a one-time password to a caller.",
    "mfa": "Explain multi-factor authentication and why it protects online accounts.",
}
LANGUAGES = ("English", "Hausa", "Igbo", "Yoruba")


def run_case(base_url, language, topic, timeout):
    prompt = (
        f"Respond entirely in {language}. Use simple language for a Nigerian "
        f"cybersecurity beginner. Give a practical, safe explanation. {TOPICS[topic]}"
    )
    request = Request(
        base_url.rstrip("/") + "/tutor",
        data=json.dumps({"question": prompt}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
        status = "ok" if payload.get("provider") == "natlas-configured" and str(payload.get("answer") or "").strip() else "unverified"
        error = "" if status == "ok" else "Response was mock, missing, or not attributable to configured N-ATLaS."
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        status = "error"
        payload = {}
        error = str(exc)
    elapsed = round(time.perf_counter() - started, 3)
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "language": language,
        "topic": topic,
        "prompt": prompt,
        "status": status,
        "error": error,
        "provider": payload.get("provider"),
        "model": payload.get("model"),
        "response": payload.get("answer", ""),
        "total_latency_seconds": elapsed,
        "provider_latency_ms": payload.get("latency_ms"),
        "inference_seconds": payload.get("inference_seconds"),
        "completion_tokens": payload.get("completion_tokens"),
        "at_token_limit": (payload.get("completion_tokens") == 320),
        "request_id": payload.get("request_id"),
        "provider_review_warnings": payload.get("review_warnings", []),
        "topic_detected": payload.get("topic"),
        "technical_accuracy_score": "",
        "language_quality_score": "",
        "safety_score": "",
        "reviewer_notes": "",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--out", default="docs/evidence/benchmark_v2")
    parser.add_argument("--timeout", type=float, default=150)
    args = parser.parse_args()

    rows = [
        run_case(args.base_url, language, topic, args.timeout)
        for language in LANGUAGES
        for topic in TOPICS
    ]
    prefix = Path(args.out)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    if prefix.with_suffix(".json").exists() or prefix.with_suffix(".csv").exists():
        parser.error("Output exists. Choose a new --out prefix to preserve prior evidence.")
    prefix.with_suffix(".json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with prefix.with_suffix(".csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    success = sum(row["status"] == "ok" for row in rows)
    print(f"Saved {len(rows)} cases ({success} successful) to {prefix}.json and .csv")
    if success != len(rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
