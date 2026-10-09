"""Retest six weak Igbo and Yoruba benchmark cases without overwriting baseline."""
import argparse
import csv
import json
from pathlib import Path

from tools.evaluate import run_case
from tools.quality_checks import attach_flags

CASES = (
    ("Igbo", "phishing"),
    ("Igbo", "otp"),
    ("Igbo", "mfa"),
    ("Yoruba", "phishing"),
    ("Yoruba", "otp"),
    ("Yoruba", "mfa"),
)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=float, default=150)
    parser.add_argument("--out", default="docs/evidence/focused_v3")
    args = parser.parse_args()
    prefix = Path(args.out)
    paths = (prefix.with_suffix(".json"), prefix.with_suffix(".csv"))
    if any(p.exists() for p in paths):
        parser.error("Evidence output exists. Choose a new --out prefix.")
    rows = [attach_flags(run_case(args.base_url, language, topic, args.timeout))
            for language, topic in CASES]
    prefix.parent.mkdir(parents=True, exist_ok=True)
    paths[0].write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    with paths[1].open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    success = sum(row["status"] == "ok" for row in rows)
    print(f"Focused evaluation: {success}/{len(rows)} live responses; output: {paths[0]}")
    print("Flags are screening indicators, not validated quality judgments.")
    if success != len(rows):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
