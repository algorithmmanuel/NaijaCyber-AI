
# ============================================================
# NAIJACYBER AI
# FastAPI Backend - N-ATLaS Integration
# Version: 0.2.0
# ============================================================

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ------------------------------------------------------------
# 1. PROJECT CONFIGURATION
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load environment variables before initialising AI provider.
load_dotenv(
    dotenv_path=PROJECT_ROOT / ".env",
    override=True
)

from backend.natlas_provider import NatlasProvider, NatlasError
from backend.beta_access import BetaAccessMiddleware

natlas = NatlasProvider()

# ------------------------------------------------------------
# 2. INITIALISE FASTAPI
# ------------------------------------------------------------

app = FastAPI(
    title="NaijaCyber AI",
    description=(
        "Interactive cybersecurity education and "
        "multilingual AI powered by N-ATLaS"
    ),
    version="0.2.0"
)

app.add_middleware(BetaAccessMiddleware)

# ------------------------------------------------------------
# 3. CYBERSECURITY MISSIONS
# ------------------------------------------------------------

MISSIONS = [
    {
        "id": 1,
        "title": "Spot the Phishing Email",
        "difficulty": "Beginner",
        "description": "Learn to recognise suspicious emails."
    },
    {
        "id": 2,
        "title": "Protect Your Password",
        "difficulty": "Beginner",
        "description": "Discover password security and MFA."
    },
    {
        "id": 3,
        "title": "Defeat Social Engineering",
        "difficulty": "Beginner",
        "description": "Identify manipulation and impersonation."
    }
]


# ------------------------------------------------------------
# 4. REQUEST MODELS
# ------------------------------------------------------------

class TutorRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000
    )


class QuizAnswer(BaseModel):
    selected_index: int


# ------------------------------------------------------------
# 5. APPLICATION HEALTH CHECK
# ------------------------------------------------------------

@app.get("/")
def home():
    return {
        "application": "NaijaCyber AI",
        "status": "running",
        "version": "0.2.0",
        "ai_provider": (
            "natlas-configured"
            if natlas.available
            else "mock"
        ),
        "model_verified": False
    }


# ------------------------------------------------------------
# 6. AI PROVIDER STATUS
# ------------------------------------------------------------

@app.get("/ai/status")
def ai_status():
    return {
        "configured_model": natlas.model,
        "endpoint_configured": natlas.available,
        "mode": (
            "natlas-configured"
            if natlas.available
            else "mock"
        ),
        "model_verified": False,
        "note": (
            "Endpoint configuration alone does not "
            "verify model identity or availability."
        )
    }


# ------------------------------------------------------------
# 7. CYBERSECURITY MISSIONS
# ------------------------------------------------------------

@app.get("/missions")
def get_missions():
    return {"missions": MISSIONS}


# ------------------------------------------------------------
# 8. N-ATLaS AI TUTOR
# ------------------------------------------------------------

@app.post("/tutor")
async def ask_tutor(request: TutorRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty"
        )

    # Use actual N-ATLaS endpoint when configured.
    if natlas.available:

        try:
            result = await natlas.generate(question)
            return result

        except NatlasError as exc:
            # Do not silently fall back to mock responses.
            raise HTTPException(
                status_code=503,
                detail=str(exc)
            )

    # --------------------------------------------------------
    # Development-only mock provider
    # --------------------------------------------------------

    lowered = question.lower()

    if "phishing" in lowered:
        answer = (
            "Phishing is a deceptive attempt to obtain "
            "sensitive information through fraudulent "
            "messages or websites."
        )

    elif "password" in lowered:
        answer = (
            "Use long, unique passwords for each account "
            "and enable multi-factor authentication."
        )

    elif "mfa" in lowered:
        answer = (
            "Multi-factor authentication requires more "
            "than one factor to verify your identity."
        )

    else:
        answer = (
            "Welcome to NaijaCyber AI. This is a "
            "development-only mock response. Ask about "
            "phishing, passwords, or MFA."
        )

    return {
        "question": question,
        "answer": answer,
        "provider": "mock",
        "model": None,
        "latency_ms": None,
        "model_verified": False
    }


# ------------------------------------------------------------
# 9. INTERACTIVE CYBERSECURITY ASSESSMENTS
# ------------------------------------------------------------

QUIZZES = {
    1: {
        "title": "Spot the Phishing Email",
        "scenario": (
            "You receive an email claiming to be from "
            "your bank. It threatens to suspend your "
            "account in 30 minutes unless you click "
            "a link and enter your banking details."
        ),
        "options": [
            "Click the link immediately",
            "Reply with your account details",
            "Verify through the official banking app or contact channel"
        ],
        "correct_index": 2,
        "explanation": (
            "The message uses urgency and a threat "
            "to pressure you. Avoid the link and "
            "independently contact your bank."
        )
    },

    2: {
        "title": "Protect Your Password",
        "scenario": (
            "You are creating an account containing "
            "sensitive information. Which security "
            "approach is strongest?"
        ),
        "options": [
            "Reuse a familiar password",
            "Use a unique long password and enable MFA",
            "Use your birthday as the password"
        ],
        "correct_index": 1,
        "explanation": (
            "Unique, long passwords reduce credential "
            "reuse risks. MFA provides another layer "
            "of account protection."
        )
    },

    3: {
        "title": "Defeat Social Engineering",
        "scenario": (
            "Someone claiming to be IT support calls "
            "and requests your one-time login code "
            "to resolve an urgent problem."
        ),
        "options": [
            "Give them the code",
            "Ask them to call back and then give the code",
            "Refuse and verify the request through an official channel"
        ],
        "correct_index": 2,
        "explanation": (
            "Never disclose one-time authentication "
            "codes. Verify the identity and legitimacy "
            "of the request using trusted contact "
            "information."
        )
    }
}


# ------------------------------------------------------------
# 10. RETRIEVE QUIZ
# ------------------------------------------------------------

@app.get("/quiz/{mission_id}")
def get_quiz(mission_id: int):

    quiz = QUIZZES.get(mission_id)

    if quiz is None:
        raise HTTPException(
            status_code=404,
            detail="Mission not found"
        )

    return {
        "mission_id": mission_id,
        "title": quiz["title"],
        "scenario": quiz["scenario"],
        "options": quiz["options"]
    }


# ------------------------------------------------------------
# 11. SUBMIT QUIZ ANSWER
# ------------------------------------------------------------

@app.post("/quiz/{mission_id}/submit")
def submit_quiz(
    mission_id: int,
    answer: QuizAnswer
):

    quiz = QUIZZES.get(mission_id)

    if quiz is None:
        raise HTTPException(
            status_code=404,
            detail="Mission not found"
        )

    if not (
        0 <= answer.selected_index < len(quiz["options"])
    ):
        raise HTTPException(
            status_code=422,
            detail="Invalid answer selection"
        )

    correct = (
        answer.selected_index
        == quiz["correct_index"]
    )

    return {
        "mission_id": mission_id,
        "correct": correct,
        "score": 100 if correct else 0,
        "correct_index": quiz["correct_index"],
        "explanation": quiz["explanation"]
    }


# ------------------------------------------------------------
# 12. FRONTEND STATIC FILES
# ------------------------------------------------------------

app.mount(
    "/app",
    StaticFiles(
        directory=PROJECT_ROOT / "frontend",
        html=True
    ),
    name="frontend"
)
