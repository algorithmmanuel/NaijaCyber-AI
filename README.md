# NaijaCyber AI

**A multilingual cybersecurity education and N-ATLaS developer evaluation platform for Nigeria.**

NaijaCyber AI is a prototype cybersecurity learning platform that combines interactive security-awareness missions with an AI-powered tutor built around the N-ATLaS multilingual language model.

## Features

- Interactive cybersecurity learning missions covering phishing, password security and social engineering.
- Automated mission assessment and browser-based progress tracking.
- AI cybersecurity tutor supporting English, Hausa, Igbo and Yoruba.
- Integration with the NCAIR1/N-ATLaS language model through a reusable Python inference adapter.
- Inference latency and token-generation metrics.
- Reproducible multilingual evaluation notebooks and supporting evidence.

## Technology Stack

- **Backend:** Python, FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **AI Model:** NCAIR1/N-ATLaS (Llama 3 8B-based)
- **Development inference:** Google Colab GPU, 4-bit quantisation
- **API connectivity:** Authenticated HTTPS tunnel for temporary testing
- **Version control:** Git and GitHub

## Project Structure

- `backend/` — FastAPI application and N-ATLaS integration adapter
- `frontend/` — Interactive learner interface
- `notebooks/` — N-ATLaS inference and evaluation experiments
- `docs/evidence/` — Model evaluation results and demonstration evidence
- `tests/` — Automated testing resources

## Local Development

1. Create a Python virtual environment.
2. Install the required Python dependencies.
3. Configure an authorised N-ATLaS inference endpoint using environment variables.
4. Start the application:

```bash
python -m uvicorn backend.main:app --reload
```

5. Open `http://127.0.0.1:8000/app/`.

The tutor runs in mock mode when no model endpoint is configured. Real N-ATLaS inference requires a separately hosted model endpoint.

## Current Status

Working research prototype with real N-ATLaS inference demonstrated through a temporary Google Colab GPU service.

The platform is not yet production-ready. Model availability depends on the inference environment, and multilingual outputs require further accuracy and linguistic validation.

## Model Attribution

N-ATLaS was developed by Awarri Technologies and the Federal Ministry of Communications, Innovation and Digital Economy.

N-ATLaS model use is subject to its own licensing and acceptable-use terms. This repository does not redistribute model weights.

## Intended Application

National AI Innovation Challenge 2026 — Developer Infrastructure category.

## Security Notice

Do not commit credentials, access tokens, `.env` files, personal banking data or other confidential information to this repository.