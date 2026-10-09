# Developer guide — NaijaCyber AI

## Scope
This repository retains the existing FastAPI backend, static HTML/JS frontend, and
`NatlasProvider` adapter. The development inference service is the real
`NCAIR1/N-ATLaS` model loaded in an authenticated Google Colab session.
Colab is temporary and is not suitable for persistent public hosting.

## Local setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `.env` with your **own** currently active HTTPS model endpoint and its
matching bearer key. Keep it local. To use development-only mock mode, leave
`NATLAS_CHAT_URL` blank.

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

- `http://127.0.0.1:8000/app/` — learner interface
- `http://127.0.0.1:8000/docs` — FastAPI interactive reference
- `GET /ai/status` — configured provider, **not** a live remote health check
- `POST /tutor` — JSON body `{"question":"Explain phishing in Hausa"}`
- `GET /missions`, `GET /quiz/{mission_id}`, `POST /quiz/{mission_id}/submit` — learning APIs

When configured, the adapter sends authenticated HTTPS chat-completions
requests to the Colab model service. Secrets are not exposed to the browser.
An unconfigured service returns mock responses; a failing configured
service returns an error rather than fabricating real model output.

## Evaluation
Run against a **working local** service while the Colab runtime and HTTPS
tunnel are active:
```powershell
.\.venv\Scripts\python.exe tools/evaluate.py
```
This executes 12 synthetic cases: 4 languages × 3 safety topics, and writes
`docs/evidence/benchmark.csv` and `benchmark.json`.
Results include prompts, responses, latency, token count, model identifier
and blank human-review fields. These runs are **not** proof of translation
quality or model safety.

Have reviewers independently grade technical accuracy, language quality
and safety (for example 1–5 each), note any harmful or incomplete advice,
and disclose limited sample sizes and reviewer qualifications.
Never send banking customer information or real credentials to the model.

## Evidence and security
Save dated screenshots and raw results under `docs/evidence/`. Remove
secrets, active private tunnel URLs, cookies, notebook token outputs and
customer details before committing. Use the model's required attribution
to Awarri Technologies and the Federal Ministry of Communications,
Innovation and Digital Economy, and check its use restrictions.

The currently committed model identifier alone is not independent
cryptographic proof of deployed model identity.
