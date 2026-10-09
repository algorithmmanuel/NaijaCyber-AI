"""Offline HTML dashboard for NaijaCyber evaluation JSON; no third-party dependencies."""
import argparse
import html
import json
from collections import Counter
from pathlib import Path
from statistics import median

SCORES = ("technical_accuracy_score", "language_quality_score", "safety_score")

def build_dashboard(rows):
    total = len(rows)
    ok = [r for r in rows if r.get("status") == "ok" and str(r.get("response") or "").strip() and r.get("provider") != "mock"]
    reviewed = [r for r in ok if all(str(r.get(k, "")).strip() for k in SCORES)]
    latencies = [float(r["total_latency_seconds"]) for r in ok if r.get("total_latency_seconds") is not None]
    providers = Counter(str(r.get("provider") or "unknown") for r in rows)
    def metric(label, value):
        return f'<div class="metric"><small>{html.escape(label)}</small><strong>{html.escape(str(value))}</strong></div>'
    cards = (metric("Total cases", total) + metric("Live successful", len(ok)) +
             metric("Human reviewed", len(reviewed)) +
             metric("Median latency", f"{median(latencies):.2f}s" if latencies else "N/A"))
    headers = ["language", "topic", "provider", "status", "total_latency_seconds", *SCORES, "reviewer_notes"]
    def cell(value):
        return "<td>" + html.escape(str(value if value is not None else "")) + "</td>"
    body = "".join("<tr>" + "".join(cell(row.get(key, "")) for key in headers) + "</tr>" for row in rows)
    counts = ", ".join(f"{html.escape(k)}: {v}" for k, v in sorted(providers.items()))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NaijaCyber AI | Evaluation</title><style>
body{{font-family:system-ui,sans-serif;background:#0b1220;color:#e5e7eb;margin:0;padding:2rem}}main{{max-width:1200px;margin:auto}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem}}.metric{{background:#172337;padding:1.25rem;border-radius:12px}}
small{{display:block;color:#a7b6cc}}strong{{font-size:1.8rem}}table{{border-collapse:collapse;width:100%;font-size:.9rem}}th,td{{padding:.75rem;border-bottom:1px solid #334155;text-align:left}}th{{color:#93c5fd}}.scroll{{overflow-x:auto}}p{{line-height:1.6}}
</style></head><body><main><h1>NaijaCyber AI — Evaluation Dashboard</h1><p>Offline evidence view. Live success excludes mock responses. Scores are entered by human reviewers; missing scores are not interpreted as zero.</p><div class="cards">{cards}</div><h2>Provider distribution</h2><p>{counts}</p><h2>Case-level evidence</h2><div class="scroll"><table><thead><tr>{''.join('<th>'+html.escape(h)+'</th>' for h in headers)}</tr></thead><tbody>{body}</tbody></table></div><p>Quality and safety cannot be inferred from successful API responses. Review responses and score independently before making language-quality claims.</p></main></body></html>"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="docs/evidence/benchmark.json")
    parser.add_argument("--output", default="docs/evidence/dashboard.html")
    args = parser.parse_args()
    rows = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise SystemExit("Expected a JSON list of evaluation cases")
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build_dashboard(rows), encoding="utf-8")
    print(f"Dashboard written to {target}")

if __name__ == "__main__":
    main()
