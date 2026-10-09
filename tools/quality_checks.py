"""Conservative heuristic flags for human review, NOT automated quality scores."""
import re

MAX_TOKENS = 320
# Patterns are limited to recognizable English strings; translated equivalents
# require fluent reviewers and are deliberately not declared machine-validated.
KNOWN_CONCEPT_ERRORS = {
    "three_factor_label": re.compile(r"three[- ]factor authentication|three factors are (always |necessarily )?required", re.I),
    "otp_typo": re.compile(r"ote time password", re.I),
    "username_only": re.compile(r"(?:username|user name) alone (?:is|can be) (?:enough|sufficient)", re.I),
    "phone_number_factor": re.compile(r"phone number (?:alone )?(?:is|counts as) (?:a |the )?(?:possession|second) factor", re.I),
    "two_knowledge_factors": re.compile(r"(?:password (?:and|plus) (?:a )?security question).{0,55}(?:mfa|multi.factor)", re.I),
}

def review_flags(row):
    response = row.get("response")
    if not isinstance(response, str) or not response.strip():
        return ["empty_response"]
    text = response.strip()
    flags = []
    if row.get("completion_tokens") == MAX_TOKENS or row.get("at_token_limit") is True:
        flags.append("possible_token_limit")
    # Only signal likely cut-off: never assert that punctuation guarantees completeness.
    if text[-1] not in ".!?。！？":
        flags.append("possibly_incomplete_ending")
    if row.get("topic") == "mfa":
        names = ("three_factor_label", "username_only", "phone_number_factor",
                 "two_knowledge_factors")
    elif row.get("topic") == "otp":
        names = ("otp_typo",)
    else:
        names = ()
    flags.extend(name for name in names if KNOWN_CONCEPT_ERRORS[name].search(text))
    return flags

def attach_flags(row):
    return {**row, "review_flags": review_flags(row),
            "requires_human_review": True}
