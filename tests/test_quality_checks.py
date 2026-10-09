"""Guardrails for focused multilingual retesting and conservative quality flags."""
from tools.evaluate_focused import CASES
from tools.quality_checks import review_flags, attach_flags, KNOWN_CONCEPT_ERRORS

def test_six_focused_cases():
    assert len(CASES) == 6
    assert len(set(CASES)) == 6
    assert set(CASES) == {(language, topic)
                           for language in ("Igbo", "Yoruba")
                           for topic in ("phishing", "otp", "mfa")}

def test_token_limit_and_incomplete_ending():
    row = {"topic": "mfa", "response": "The phone verification was cut",
           "completion_tokens": 320}
    assert review_flags(row) == ["possible_token_limit", "possibly_incomplete_ending"]

def test_known_errors_flagged():
    assert "otp_typo" in review_flags({
        "topic": "otp", "response": "This is an Ote Time Password."})
    assert "three_factor_label" in review_flags({
        "topic": "mfa", "response": "Three-factor authentication uses passwords."})
    assert "phone_number_factor" in review_flags({
        "topic": "mfa", "response": "Your phone number is a possession factor."})
    assert "two_knowledge_factors" in review_flags({
        "topic": "mfa", "response": "A password plus a security question counts as MFA."})

def test_flags_do_not_claim_automatic_validation():
    row = attach_flags({"topic": "otp", "response": "Never share an OTP.",
                        "completion_tokens": 60})
    assert row["review_flags"] == []
    assert row["requires_human_review"] is True

def test_empty_response():
    assert review_flags({"response": None}) == ["empty_response"]
