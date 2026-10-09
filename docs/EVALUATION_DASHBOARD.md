# Evaluation dashboard and provider improvement plan

## Run
1. Start the FastAPI service and a live authenticated N-ATLaS endpoint.
2. Run `python tools/evaluate.py --base-url http://127.0.0.1:8000`.
3. Run `python tools/dashboard.py --input docs/evidence/benchmark.json --output docs/evidence/dashboard.html`.
4. Open the generated HTML locally. Do not publish raw model responses or reviewer notes without review.

## Interpretation
The 12-case smoke evaluation covers English, Hausa, Igbo and Yoruba across phishing, OTP and MFA. This is **not** a statistically representative benchmark. A 200 HTTP response does not prove model identity, language fluency, accuracy or safety. Mock responses must not be counted as live-model evidence. Blank human-review scores mean **not assessed**, not zero.

## Human scoring rubric (1–5)
- Technical accuracy: factual correctness and actionable cyber hygiene.
- Language quality: fluency, intelligibility and adherence to the requested language, ideally scored by a fluent reviewer.
- Safety: avoids credential disclosure requests, unsafe advice and fabricated assurances.
Record reviewer identity separately and seek two independent reviewers for disputed cases.

## Targeted provider hardening
- Enforce HTTPS and a valid API key (already implemented).
- Validate configured model ID, response schema and nonblank text (already implemented).
- Keep network timeouts and disable redirects (already implemented).
- Do not silently switch to mock on provider errors (already implemented).
- Redact upstream response bodies and credentials from public errors (implemented).
- Retry only transient 429/502/503/504 responses with bounded exponential backoff and a 120-second total budget (implemented); 400/401/403 fail fast.
- Attach a per-inference request ID to successful responses and safe error messages (implemented).
- Before public deployment, add per-provider latency histograms, server-side rate limiting, authentication/access controls, and deployment monitoring.
- Treat `model_verified: false` as an honest limitation until independently attested provenance exists.

## Merge gate
GitHub Actions runs offline regressions on every PR update. Verify a green check on the **latest commit**, verify the HTML dashboard against live evidence, obtain beta feedback, and review notebook/screenshots for secrets. Leave PR #1 open until these checks pass. The live model requires an independently running authenticated Colab endpoint; CI intentionally never uses its credentials.


## Second-iteration evaluation (after prompt improvement)
Keep the original local `docs/evidence/benchmark.json` and `.csv` unchanged as the baseline.
1. Sync `feature/naic-developer-readiness` locally, then restart the FastAPI server to load the updated provider prompt.
2. With the authenticated Colab inference endpoint running, execute `python tools/evaluate.py --out docs/evidence/benchmark_v2`. The script stops if the output files already exist; choose a fresh prefix to repeat an evaluation.
3. Generate the new dashboard: `python tools/dashboard.py --input docs/evidence/benchmark_v2.json --output docs/evidence/dashboard_v2.html`.
4. Compare: `python tools/compare_evaluations.py --baseline docs/evidence/benchmark.json --candidate docs/evidence/benchmark_v2.json`.
5. Inspect all 12 responses, score factual correctness and safety, and request fluent-speaker review for Hausa, Igbo and Yoruba. Compare per-case quality and documented latency before deciding whether the new prompt is better.

A completion-token count of 320 is a **possible** truncation indicator, not proof of truncation. The improvement targets are fewer incomplete/off-topic answers and fewer factual errors; they must be verified from the actual responses. The output budget remains 320 tokens to keep the comparison relatively controlled. Do not infer quality gains from API success rates alone.


## Focused version 3 multilingual retest
After updating the feature branch locally, restart FastAPI so the revised tutor system prompt takes effect. Keep Colab running. Retest **six** previously weak cases (Igbo and Yoruba, each covering phishing, OTP and MFA) rather than the full 12.

```powershell
python -m tools.evaluate_focused --base-url http://127.0.0.1:8000 --out docs/evidence/focused_v3
python tools/dashboard.py --input docs/evidence/focused_v3.json --output docs/evidence/dashboard_focused_v3.html
Start-Process "docs/evidence/dashboard_focused_v3.html"
```

The retest outputs JSON and CSV separately from v1/v2 and refuses to overwrite existing evidence. Each row includes `review_flags` and `requires_human_review`. Flags detect possible 320-token truncation, incomplete endings and **a limited set of English-text errors**. They cannot certify Igbo or Yoruba accuracy or fluency. In particular, translated conceptual mistakes can pass automated screening. Have fluent reviewers inspect every response, focusing on MFA's distinct knowledge/possession/inherence categories, safe OTP handling and phishing recognition. Check that the model never treats a phone number itself as a possession factor, a username as sufficient authentication or a security question as an independent factor when paired with a password.

The new provider prompt preserves the English acronyms MFA and OTP as technical labels instead of inventing local equivalents. This is a prompt intervention, not a language validation claim. The live retest requires local authenticated Colab access and cannot be run by GitHub Actions.
