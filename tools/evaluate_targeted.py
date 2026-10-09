"""Small retest of Igbo/Yoruba OTP and MFA, retaining previous evidence."""
import argparse
import csv
import json
from pathlib import Path
from tools.evaluate import run_case
from tools.quality_checks import attach_flags

CASES = (("Igbo", "otp"), ("Igbo", "mfa"), ("Yoruba", "otp"), ("Yoruba", "mfa"))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=float, default=150)
    parser.add_argument("--out", default="docs/evidence/targeted_v4")
    args = parser.parse_args()
    prefix = Path(args.out)
    outputs = (prefix.with_suffix(".json"), prefix.with_suffix(".csv"))
    if any(path.exists() for path in outputs):
        parser.error("Output already exists; use another --out prefix.")
    rows = [attach_flags(run_case(args.base_url, language, topic, args.timeout))
            for language, topic in CASES]
    prefix.parent.mkdir(parents=True, exist_ok=True)
    outputs[0].write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    with outputs[1].open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    success = sum(row["status"] == "ok" for row in rows)
    flagged = sum(bool(row["review_flags"] or row.get("provider_review_warnings")) for row in rows)
    print(f"Targeted v4 live responses: {success}/{len(rows)}; flagged for review: {flagged}; saved {outputs[0]}")
    if success != len(rows):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
