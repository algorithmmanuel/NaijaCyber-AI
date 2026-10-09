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

When beta mode is on, all application routes require a dedicated beta sign-in page and server-side session cookie; each account is permitted at most 12 tutor calls/hour (24 total/hour across both). The limit applies per running process and resets when the app restarts. This is suitable for a **supervised short beta only**, not production security. A **Log out** button revokes the current session and clears its cookie; sessions also expire after four hours or an app restart. Use an InPrivate/Incognito session for each tester; testers should not share accounts.

## Start the application

In the repository directory, restart FastAPI after editing `.env`:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Test in your own browser: `http://127.0.0.1:8000/app/`. It should redirect to `/beta/login` (a dedicated sign-in page), then display the learner UI after authentication. Confirm the **Log out** button redirects to the sign-in page and that the old session can no longer reach `/app/` without signing in again. Check one tutor question and confirm the provider says `natlas-configured`. `/ai/status` only indicates configuration, not live health.

## Provide a temporary HTTPS access route

Use a **separate** HTTPS tunnel from the existing Colab→8001 tunnel. Install and authenticate the ngrok CLI locally using ngrok's official instructions. In a second PowerShell terminal run:

```powershell
ngrok http 8000
```

Confirm the output forwards the generated `https://...ngrok-free.app` or `.dev` URL to `http://localhost:8000`. Open `https://<your-new-url>/app/` in a private window and confirm that it redirects to the beta sign-in page. Sign in, use a mission, click **Log out**, and confirm you cannot re-enter via browser Back without signing in again. **Never** give a tester the Colab inference URL, model bearer token, notebook, repository access or local `.env`. Send the application HTTPS URL and their individual test password separately and privately. Be aware that the HTTPS URL itself is publicly reachable, although the app is protected by its password gate. Basic authentication must never be used via a public HTTP URL.

**Do not change your existing `NATLAS_CHAT_URL` to the new local-app tunnel**. It must continue pointing to the Colab model URL.

The laptop, FastAPI, ngrok CLI, Colab and Colab inference tunnel must remain running for the testing session. Stop the application tunnel once both testers have completed their tasks.

## Tester steps and evidence

Ask each tester to use a different browser session/device; consent to the test; complete the three missions; deliberately try at least one incorrect quiz option; refresh and check that completed missions remain completed; submit one synthetic tutor question in English and optionally one in a language they speak; record any factual or language mistakes and the waiting time. Progress is stored in that browser's `localStorage`, not centrally or across devices.

Use `docs/BETA_TEST_PLAN.md` for an anonymised record for each person. Capture screenshots only with their permission, redacting URLs, credentials, personally identifying information and API tokens. Do **not** declare the multilingual model validated because the API works. Report test failures and remaining model limitations.

When finished, terminate the local ngrok process, stop FastAPI, and change `BETA_MODE=0` for development. Laptop shutdown does not affect remote GitHub commits or PR #1.

## Closing the tester-requested logout finding

BT-02 observed that the first beta build allowed sign-in but not a clear sign-out because HTTP Basic credentials were retained by the browser. The beta access layer now provides a dedicated login page, a four-hour opaque server-side session with HttpOnly, SameSite cookie settings, an explicit **Log out** button, and server-side session revocation. This is a documented post-beta corrective change. The fix is covered by offline tests; a fresh, hands-on login/logout browser check is still required before claiming that real users verified it.

## Shutting down safely

1. Obtain consent for screenshot inclusion and maintain anonymised original evidence off the public repository until redacted.
2. Terminate the **laptop** ngrok tunnel, stop FastAPI, and disconnect Colab/its inference tunnel when no longer needed.
3. If using a temporary active inference token, rotate it before a future public demo.
4. Push/check all code and documentation commits in GitHub. PR #1 and GitHub Actions do not rely on your laptop remaining powered on.
5. The public application link **will stop working** after laptop shutdown. Use recorded/redacted screenshots and a demo video for judging unless reliable always-on hosting is arranged.
