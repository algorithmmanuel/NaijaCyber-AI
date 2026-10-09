"""Compare two offline N-ATLaS evaluations without claiming human-reviewed quality."""
import argparse
import json
from pathlib import Path
from statistics import median

def summarize(rows):
    live = [r for r in rows if r.get("status") == "ok" and
            r.get("provider") == "natlas-configured" and
            isinstance(r.get("response"), str) and r["response"].strip()]
    latencies = [float(r["total_latency_seconds"]) for r in live
                 if isinstance(r.get("total_latency_seconds"), (float, int))]
    # Completion-token equality is a potential truncation signal, NOT proof of truncation.
    limit_hits = sum(r.get("completion_tokens") == 320 for r in live)
    return {"cases": len(rows), "live_successes": len(live),
            "median_latency_seconds": round(median(latencies), 3) if latencies else None,
            "possible_token_limit_hits": limit_hits,
            "human_reviewed": sum(
                all(str(r.get(k, "")).strip() for k in
                    ("technical_accuracy_score", "language_quality_score", "safety_score"))
                for r in live)}

def compare(baseline, candidate):
    a, b = summarize(baseline), summarize(candidate)
    baseline_cases = {(r.get("language"), r.get("topic")) for r in baseline}
    candidate_cases = {(r.get("language"), r.get("topic")) for r in candidate}
    return {"baseline": a, "candidate": b,
            "same_case_keys": baseline_cases == candidate_cases,
            "warning": "API success and token counts do not establish factual or language quality. Conduct human reviews."}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default="docs/evidence/benchmark.json")
    parser.add_argument("--candidate", default="docs/evidence/benchmark_v2.json")
    parser.add_argument("--output", default="docs/evidence/comparison_v2.json")
    args = parser.parse_args()
    before = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    after = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    if not isinstance(before, list) or not isinstance(after, list):
        parser.error("Both evaluation inputs must be JSON arrays")
    report = compare(before, after)
    path = Path(args.output)
    if path.exists():
        parser.error("Comparison output already exists; choose a new --output path")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
