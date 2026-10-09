# NaijaCyber AI — External Beta Test Evidence and Submission Readiness

**Date:** 9 October 2026  
**Prototype:** NaijaCyber AI — beginner cybersecurity missions and multilingual N-ATLaS tutor  
**Repository:** `algorithmmanuel/NaijaCyber-AI`  
**Development branch / draft PR:** `feature/naic-developer-readiness` / PR #1  
**Test scope:** Supervised remote functional and exploratory language testing, two external beta participants

## Executive summary

Two independent beta participants accessed the prototype through temporary HTTPS access and provided screenshots of its browser-based learning experience and live N-ATLaS tutor. Tester BT-01, a Yoruba speaker, provided positive subjective feedback on a Yoruba phishing explanation and supplied screenshots demonstrating all three mission completions. Tester BT-02, an Igbo speaker, supplied mobile screenshots showing quiz interactions (including correct and incorrect responses) and an Igbo phishing tutor response, and described the first paragraph as understandable but expressed reservations about the second. This is **preliminary usability and exploratory multilingual feedback**, not validation of translation quality, model safety, or production readiness.

## Architecture and verification

- FastAPI backend and responsive HTML/JavaScript learner interface.
- Three beginner learning missions: phishing awareness, password security, and social engineering.
- N-ATLaS model served through an authenticated temporary Google Colab inference endpoint.
- Temporary HTTPS application tunnel; separate authentication and limits for two supervised testers.
- The tutor displays a configured model identity and a live inference result; configuration or displayed identifier alone is **not independent provenance verification**.
- Offline CI/regression tests and versioned synthetic evaluation runs have previously been undertaken; the V4 assessment demonstrated four successful requests, **but identified multilingual conceptual errors and an incomplete Yoruba MFA answer**.

## Observed results

| Evidence point | BT-01: Yoruba | BT-02: Igbo |
|---|---|---|
| Device / interaction | Desktop browser screenshots | Android mobile browser screenshots |
| External application use | Shown | Shown |
| Mission 1: phishing | Completed, screenshot | Correct quiz answer, screenshot |
| Mission 2: password | Completed, screenshot | Incorrect answer and 0/100 feedback shown; completion unverified |
| Mission 3: social engineering | Completed, screenshot | Correct answer and replay/completed state shown |
| Progress after browser refresh | Not specifically evidenced | Not specifically evidenced |
| Live AI tutor | Yoruba phishing answer shown | Igbo phishing answer shown |
| User feedback | Positive subjective judgment | First paragraph understood; concern with second paragraph |
| Qualified language accuracy scoring | Not provided | Not provided |

**Evidence limitations:** Screenshots demonstrate interactions but not formal identity verification, representative sampling, or sustained availability. BT-02's screenshots do not establish completion of all three missions. Browser-persisted progress after refresh is not proven by the supplied screenshots. Do not report either as verified.

## Verbatim beta participant feedback

**BT-01 (Yoruba, regarding Ask Your Tutor):**
> it is very okay ohh, well explained in my own opinion ohh

**BT-02 (Igbo, regarding Ask Your Tutor):**
> The first paragraph, yes.  
> The second paragraph, not so much. Although it might be because it's technical and requires domain knowledge.

No formal numeric ratings were collected. These are participant impressions rather than expert reviews, and the comments should not be converted into numerical scores.

## What the screenshots actually show

**BT-01:** Temporary ngrok visitor warning and protected sign-in, browser learner interface, three mission cards shown as completed and a 3/3 progress indicator, quiz result explanations, and Yoruba phishing tutor question/answer. The tutor screenshot reports **320 generated tokens and ~21.44 seconds elapsed**, with the visible answer ending incompletely; this is a truncation concern even though the participant described the content positively.

**BT-02:** Mobile learner interface (initial 0/3 indicator), phishing quiz selection and correct feedback, password quiz incorrect feedback (0/100), social-engineering correct feedback and completed/replay state, and an Igbo phishing tutor question/answer. The tutor screenshot shows **~14.66 seconds elapsed** and includes cybersecurity guidance that warrants a technically qualified review, particularly in the second paragraph. The tester's uncertainty is preserved rather than characterized as a verified translation failure.

## Findings and action disposition

| ID | Finding | Impact | Disposition at prototype submission |
|---|---|---|---|
| B-01 | External browser access, authentication, missions, feedback, and real tutor inference demonstrated | Supports functional proof of concept | Record as demonstrated in supervised beta |
| B-02 | Yoruba tester found explanation acceptable | Encouraging early feedback | Record as subjective feedback, not validated fluency |
| B-03 | Igbo tester was less confident about second tutor paragraph | Clarity/domain expertise concern | Retain as known limitation for later qualified review |
| B-04 | Yoruba tutor screenshot suggests completion-token truncation | Incomplete educational answer risk | Disclose; do not present as fully resolved |
| B-05 | Earlier V4 synthetic evaluations found MFA factor errors | Technical misinformation risk | Disclose; human verification required for critical guidance |
| B-06 | Tester 2 full mission completion and post-refresh persistence unverified | Coverage limitation | Mark unverified, not passed |
| B-07 | Model and public-access services are temporary | Availability and operational limitations | Supervised demo only; not production hosting |
| B-08 | BT-02 identified a missing logout mechanism under browser-cached Basic authentication | Users could not reliably end their browser session | **Implemented after feedback:** dedicated beta login page, revocable server-side sessions and logout button; offline CI regression tests included. Browser acceptance check pending |

## Quality assurance and development history

The repository contains separate versioned evaluation scripts and evidence for the original 12-case checks, subsequent prompt changes, focused Igbo/Yoruba checks, and V4 reference grounding. The testing cycle identified failures including incorrect MFA categorization, problematic technical translations and truncated responses. A curated English reference layer and conservative response warnings were introduced. **The V4 assessment still showed substantive multilingual errors.** No claim of a fully validated local-language cybersecurity model is made.

## Ethical treatment and reproducibility

- Collect only pseudonymous tester records, with consent for use of their submitted screenshots.
- Exclude real passwords, PINs, OTPs, bearer keys, active tunnel secrets and banking-customer information.
- Keep identifiable originals and access credentials private; publish only redacted supporting images with permission.
- Keep a frozen dated copy of this report and the test evidence. Temporary Colab/ngrok URLs may expire and should not be represented as permanent deployment URLs.
- Any further beta claims (mission persistence, all missions completed by both testers, language accuracy grading) require additional evidence.

## Submission-ready description

**NaijaCyber AI** is an experimental, browser-based cybersecurity learning prototype designed for Nigerian beginners. It combines three interactive awareness missions with an N-ATLaS-powered tutor supporting English and Nigerian-language interactions. The prototype uses a FastAPI service and a temporary authenticated inference deployment, and includes versioned evaluation scripts, offline regression tests, conservative quality-warning checks and documented supervised beta testing. Two external participants accessed the application: a Yoruba speaker reported a positive impression of a tutor response and demonstrated completion of all three learning missions, while an Igbo speaker exercised the mobile interface and quizzes and provided mixed feedback on the clarity of an Igbo tutor explanation. These findings provide evidence of functional operation and early user engagement while also identifying multilingual answer quality, potential response truncation and temporary hosting as limitations. The project is presented as a working research/development prototype, not a production-grade or independently validated educational system.

## Submission packaging checklist

- [x] Prototype source and development work preserved in GitHub PR #1.
- [x] Two distinct external-user screenshot sets supplied.
- [x] Two verbatim qualitative language feedback statements captured.
- [x] Functional evidence and limitations summarized conservatively.
- [x] Participants consented to including their answers and screenshots in the submission (reported by project owner on 9 October 2026).
- [ ] Remove browser identifiers, login details and secrets from public evidence.
- [ ] Check the competition's specific eligibility, repository, demonstration, date and licensing requirements against its official published rules.
- [ ] Ensure any submission links point to accessible, permitted materials (private GitHub PRs are not viewable by public judges without granted access).
- [ ] Decide whether a short recorded demo or static screenshot bundle is required when temporary inference hosting is offline.

**Engineering decision:** No source-code rewrite is needed to submit this as a prototype with candid limitations. Keep the beta findings on PR #1; merging or production deployment is a separate decision.

## Post-beta feedback resolution — sign-out (9 October 2026)

BT-02 also identified a practical usability/security issue: the original protected beta only allowed sign-in, because browser-managed HTTP Basic authentication provides no reliable application logout. The implementation was updated *after* the recorded participant testing to support a dedicated sign-in page and explicit logout. Session tokens are random, process-local, short-lived (four hours), issued via HttpOnly/SameSite cookies and deleted on server-side logout. This change is **engineering follow-up evidence, not a claim that the original two beta sessions already tested it**. Before declaring this fix accepted by end users, manually sign in, log out, try the browser Back button and access a protected URL again. No changes to the N-ATLaS model or core mission/tutor logic were needed.

The project owner confirmed both participants consent to the inclusion of their answers and screenshots. Screenshots must still be reviewed and redacted before publication; originals remain private until that check is complete.
