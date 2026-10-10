# Developer Playground — Four-language inference validation

## Purpose and provenance
These are four manually initiated browser requests through the NaijaCyber AI Developer Dashboard (`/app/developer.html`) and existing FastAPI `POST /tutor` endpoint, using the configured inference provider. The original, unedited browser exports are retained in `docs/evidence/inference/`. These are **integration smoke tests**, not a controlled model-quality study, benchmark suite, or independent confirmation of the remote model's identity.

| Language | Test topic | Backend latency (ms) | Completion tokens | Review warnings | Evidence |
|---|---|---:|---:|---|---|
| English | Multi-factor authentication | 9819.55 | 125 | None | [english.json](inference/english.json) |
| Hausa | Multi-factor authentication | 21814.32 | 320 | Possible token limit; possibly incomplete ending | [hausa.json](inference/hausa.json) |
| Igbo | Strong passwords | 13541.35 | 194 | None | [igbo.json](inference/igbo.json) |
| Yoruba | Phishing | 28372.60 | 320 | Possible token limit; possibly incomplete ending | [yoruba.json](inference/yoruba.json) |

All four returned `provider: natlas-configured`, `model: NCAIR1/N-ATLaS`, nonempty answers, request IDs, and token counts. All four returned `model_verified: false`. This establishes successful responses from the **configured API path**; it does not independently authenticate the remote model's weights or deployment. Provider status alone is not a live health check.

## Interpretation and limitations
- **Four of four requests returned responses**, without a reported API error in these saved exports. This is a limited connectivity/integration observation, not a reliability or availability claim.
- Hausa and Yoruba responses each reached 320 completion tokens and include the provider's `possible_token_limit` and `possibly_incomplete_ending` review warnings. Treat these outputs as potentially truncated; inspect server-side finish reasons and consider adjusting generation limits before further evaluation.
- The prompts differ by language and topic, so the latency values **must not be used to rank languages or infer comparative language performance**. No independent native-speaker review, systematic accuracy scoring, or safety assessment is recorded here.
- The Igbo response recommends changing passwords periodically; this advice merits expert review against current risk-based password guidance. The Hausa response also has a potentially incomplete closing sentence. The Yoruba response's linguistic fluency and clarity require native-speaker review.
- The raw exports include prompts and generated text, not credentials or customer data. Avoid committing future exports containing sensitive inputs, secrets, cookies, or tunnel URLs.

## Reproduction
1. Start the authenticated Colab inference service and ensure the configured HTTPS endpoint is reachable.
2. Start the local FastAPI server: `python -m uvicorn backend.main:app --reload`.
3. Open `http://127.0.0.1:8000/app/developer.html` after beta authentication, select a language, enter a question and choose **Run inference**.
4. Inspect provider metadata and review warnings in the raw API response; click **Export JSON** to preserve the complete response.
5. Independently evaluate linguistic quality, factual correctness and security advice before asserting model quality.

## Competition evidence scope
These results support the **working artefact** and **N-ATLaS integration evidence** narratives. They do **not** on their own satisfy the distinct requirement for real-user validation, independent model verification, or production hosting. Separate beta-tester confirmations and any formal benchmark evidence should be documented in the submission.
