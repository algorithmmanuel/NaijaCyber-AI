# Contributing to NaijaCyber AI

Thank you for helping improve multilingual, beginner-friendly cybersecurity education and reusable N-ATLaS integration.

## Getting started

1. Fork the repository and create a branch from `main`.
2. Use Python 3.11 or later and create a virtual environment: `python -m venv .venv`.
3. Activate it, then run `python -m pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`; set your own inference service URL and API key only if you need live inference. **Never commit `.env`, access tokens, tunnel credentials, or private tester information.**
5. Start the learner application with `python -m uvicorn backend.main:app --reload`; open `http://127.0.0.1:8000/app/`. Without a configured inference endpoint, the tutor uses a mock response.
6. Run `python -m pytest -q` before proposing changes.

See [Developer Guide](docs/DEVELOPER_GUIDE.md) for API setup, and [Beta Test Plan](docs/BETA_TEST_PLAN.md) for consent-aware evaluation.

## Suggested contributions

- Clearer beginner cybersecurity instruction and accessibility improvements
- Improvements to Python N-ATLaS inference integration, error handling, and documentation
- Automated tests, evaluation fixtures, and responsible performance measurement
- Nigerian-language translation and terminology review by qualified speakers

Do not represent machine-generated translations as linguistically verified. Preserve evidence limitations and disclose uncertainty.

## Pull requests

1. Open a focused issue or describe the problem and intended change in the pull request.
2. Keep pull requests narrow; include tests and documentation where behavior changes.
3. Explain how you tested the change, and provide anonymised screenshots only when necessary.
4. Do not add real credentials, unredacted beta-tester screenshots, identification documents, private conversations, or copyrighted model weights.
5. Ensure that new dependencies and datasets can legally be redistributed.

Maintainers review contributions for accuracy, security, accessibility, and reproducibility. A submitted pull request is not a guarantee of acceptance.

## Security reporting

**Do not open a public GitHub issue or pull request containing a vulnerability exploit, token, personal data, or unredacted logs.** Use GitHub's **Report a vulnerability** / private vulnerability reporting feature if it is enabled for this repository. If unavailable, contact the repository maintainer privately through their GitHub profile and request a secure reporting channel without sending exploit details publicly.

If you believe a secret was accidentally published, revoke/rotate it immediately; deleting a file from the latest commit alone does not remove it from Git history.

## Licensing and attribution

Original repository code and documentation are offered under the [MIT License](LICENSE), unless a file says otherwise. N-ATLaS model weights and other third-party tools, datasets and trademarks retain their respective owners' terms. This licence does not grant rights to redistribute third-party model weights or tester-provided materials.
