# Terminology-grounded focused V4 assessment

The implementation uses a small **English concept-reference layer**, not a translated dictionary. The authoritative concepts are:

- **MFA:** two or more *different* factor categories (knowledge, possession, inherence). Two knowledge factors do not count as MFA. A phone number alone is not a possession factor.
- **OTP:** a short-lived one-time verification code; never share it with a caller, even a purported bank representative.
- **Phishing:** deceptive messages or sites designed to steal information or manipulate users; verify independently via the official bank app or established contact details.

For Igbo and Yoruba, the prompt preserves **MFA** and **OTP** verbatim and asks the model to explain them naturally in the requested language. No local-language translations in this repository are claimed as independently validated.

Response warnings are returned as `review_warnings`, with the detected `topic`. They identify potential truncation and certain recognizable English or observed Igbo/Yoruba phrases. Warnings are non-blocking and **never** certify fluency, accuracy or safety.

## Small retest: four cases only

Keep Colab's authenticated N-ATLaS server running and verify a single `/tutor` request. Pull the feature branch, restart the **local** FastAPI process, then run:

```powershell
python -m tools.evaluate_targeted --out docs/evidence/targeted_v4
python tools/dashboard.py --input docs/evidence/targeted_v4.json --output docs/evidence/dashboard_targeted_v4.html
Start-Process "docs/evidence/dashboard_targeted_v4.html"
```

This retests Igbo and Yoruba **OTP and MFA** only, the cases with the most concerning terminology and factor-category failures. It preserves previous evaluation files and refuses existing output filenames. Evaluate every returned response against `focused_v3_retry.json` and have fluent reviewers judge the naturalness of the wording. If the quality remains inadequate, do not merge solely because CI passes.
