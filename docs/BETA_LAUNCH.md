# Supervised two-person beta: launch and evidence

This is an **experimental, time-limited demonstration**, not a public production deployment.

## Prerequisites

- Pull `feature/naic-developer-readiness` and verify GitHub Actions is green.
- Run the authenticated N-ATLaS inference app on Google Colab port 8001; verify the Colab ngrok tunnel forwards to 8001.
- Set the existing `NATLAS_CHAT_URL` and `NATLAS_API_KEY` in your private local `.env`. **Never share them with testers**.
- You must have **two independent testers** who consent to the test and agree not to enter real banking/customer data.

## Protect the demo

Set `BETA_MODE=1` in your local `.env`. Generate two distinct random passwords of at least 16 characters, one for each tester, and save them as `BETA_TESTER_1_PASSWORD` and `BETA_TESTER_2_PASSWORD`. Do **not** commit or share the `.env`.

On Windows PowerShell, you can generate a password using:

```powershell
$bytes = New-Object byte[] 24
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
$rng.Dispose()
[Convert]::ToBase64String($bytes)
```

Run this **twice**, replacing the two password values. The sign-in usernames are exactly `tester1` and `tester2`. Do not paste passwords into chat, screenshots or GitHub.

When beta mode is on, all application routes require HTTP Basic sign-in; each account is permitted at most 12 tutor calls/hour (24 total/hour across both). The limit applies per running process and resets when the app restarts. This is suitable for a **supervised short beta only**, not production security. Browsers may cache Basic credentials until the browser session ends. Use an InPrivate/Incognito session for each tester; testers should not share accounts.

## Start the application

In the repository directory, restart FastAPI after editing `.env`:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Test in your own browser: `http://127.0.0.1:8000/app/`. It should request a username/password and display the learner UI after authentication. Check one tutor question and confirm the provider says `natlas-configured`. `/ai/status` only indicates configuration, not live health.

## Provide a temporary HTTPS access route

Use a **separate** HTTPS tunnel from the existing Colab→8001 tunnel. Install and authenticate the ngrok CLI locally using ngrok's official instructions. In a second PowerShell terminal run:

```powershell
ngrok http 8000
```

Confirm the output forwards the generated `https://...ngrok-free.app` or `.dev` URL to `http://localhost:8000`. Open `https://<your-new-url>/app/` in a private window and confirm that it asks for credentials. **Never** give a tester the Colab inference URL, model bearer token, notebook, repository access or local `.env`. Send the application HTTPS URL and their individual test password separately and privately. Be aware that the HTTPS URL itself is publicly reachable, although the app is protected by its password gate. Basic authentication must never be used via a public HTTP URL.

**Do not change your existing `NATLAS_CHAT_URL` to the new local-app tunnel**. It must continue pointing to the Colab model URL.

The laptop, FastAPI, ngrok CLI, Colab and Colab inference tunnel must remain running for the testing session. Stop the application tunnel once both testers have completed their tasks.

## Tester steps and evidence

Ask each tester to use a different browser session/device; consent to the test; complete the three missions; deliberately try at least one incorrect quiz option; refresh and check that completed missions remain completed; submit one synthetic tutor question in English and optionally one in a language they speak; record any factual or language mistakes and the waiting time. Progress is stored in that browser's `localStorage`, not centrally or across devices.

Use `docs/BETA_TEST_PLAN.md` for an anonymised record for each person. Capture screenshots only with their permission, redacting URLs, credentials, personally identifying information and API tokens. Do **not** declare the multilingual model validated because the API works. Report test failures and remaining model limitations.

When finished, terminate the local ngrok process, stop FastAPI, and change `BETA_MODE=0` for development. Laptop shutdown does not affect remote GitHub commits or PR #1.
