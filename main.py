"""
AI Travel Planner — FastAPI backend.

Endpoints:
  POST /api/plan        -> destinations, day-wise itinerary, budget estimate, packing checklist
  POST /api/flashcards  -> interactive flashcards about a destination
  POST /api/quiz        -> interactive multiple-choice quiz about a destination
  GET  /healthz         -> health check (used by Cloud Run)
  GET  /                -> serves the frontend
"""

import json
import os
import re
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import anthropic

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

app = FastAPI(title="AI Travel Planner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def call_claude_json(system: str, user: str, max_tokens: int = 2000) -> dict:
    """Call Claude and parse a strict-JSON response, tolerating code fences."""
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {e}")

    text = "".join(block.text for block in resp.content if block.type == "text")
    cleaned = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", cleaned, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        raise HTTPException(status_code=502, detail="Could not parse model response as JSON")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PlanRequest(BaseModel):
    origin: Optional[str] = None
    region_preference: str            # e.g. "Southeast Asia", "anywhere"
    trip_length_days: int
    budget_level: str                 # "shoestring" | "moderate" | "luxury"
    currency: str = "USD"
    interests: List[str] = []         # e.g. ["food", "hiking", "museums"]
    travel_month: Optional[str] = None
    party: str = "solo"               # "solo" | "couple" | "family" | "friends"
    known_destination: Optional[str] = None  # if set, skip suggestion step


class FlashcardRequest(BaseModel):
    destination: str
    count: int = 10


class QuizRequest(BaseModel):
    destination: str
    count: int = 8


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/api/plan")
def create_plan(req: PlanRequest):
    system = (
        "You are an expert travel planner. Always reply with STRICT JSON only, "
        "no prose, no markdown fences, matching exactly the schema you are given."
    )

    user = f"""Build a travel plan as JSON with this exact schema:

{{
  "destinations": [
    {{"name": "", "country": "", "why_it_fits": "", "best_for": ""}}
  ],
  "chosen_destination": "",
  "itinerary": [
    {{"day": 1, "title": "", "morning": "", "afternoon": "", "evening": "", "local_tip": ""}}
  ],
  "budget_estimate": {{
    "currency": "{req.currency}",
    "total_low": 0,
    "total_high": 0,
    "breakdown": {{
      "flights": "",
      "accommodation": "",
      "food": "",
      "local_transport": "",
      "activities": "",
      "misc_buffer": ""
    }}
  }},
  "packing_checklist": [
    {{"category": "", "items": ["", ""]}}
  ]
}}

Rules:
- Suggest exactly 3 candidate destinations that match the preferences below, each with a short reason.
- Pick the single best one as "chosen_destination" and build the rest of the plan (itinerary, budget, packing) around it.
- The itinerary must have exactly {req.trip_length_days} day entries, realistic and geographically sensible (don't zig-zag).
- Budget numbers must be realistic for a {req.budget_level} traveler in {req.currency}, for the whole trip (not per day), for a {req.party} traveling.
- Packing checklist should have 4-6 categories (e.g. Documents, Clothing, Electronics, Health & Toiletries, Destination-specific gear) tailored to the destination and season.

Traveler preferences:
- Departing from: {req.origin or "not specified"}
- Region preference: {req.region_preference}
- Trip length: {req.trip_length_days} days
- Budget level: {req.budget_level}
- Interests: {", ".join(req.interests) if req.interests else "general sightseeing"}
- Travel month: {req.travel_month or "flexible"}
- Traveling as: {req.party}
- Already decided destination (use this instead of suggesting alternatives, but still fill "destinations" with it as the only entry): {req.known_destination or "none, please suggest"}
"""
    return call_claude_json(system, user, max_tokens=3000)


@app.post("/api/flashcards")
def create_flashcards(req: FlashcardRequest):
    system = (
        "You are a knowledgeable local travel guide creating study flashcards. "
        "Always reply with STRICT JSON only, no prose, no markdown fences."
    )
    user = f"""Create exactly {req.count} travel flashcards about {req.destination} as a JSON array with this schema:

[
  {{"category": "Culture|Language|History|Food|Practical", "front": "short prompt or question", "back": "concise, informative answer (1-3 sentences)"}}
]

Cover a mix of: useful local phrases, etiquette/customs, food to try, key historical/cultural facts, and practical survival tips (safety, money, transport). Make each card genuinely useful for a first-time visitor, not generic trivia."""
    return call_claude_json(system, user, max_tokens=2000)


@app.post("/api/quiz")
def create_quiz(req: QuizRequest):
    system = (
        "You are a travel educator creating a multiple-choice quiz. "
        "Always reply with STRICT JSON only, no prose, no markdown fences."
    )
    user = f"""Create exactly {req.count} multiple-choice quiz questions about {req.destination} as a JSON array with this schema:

[
  {{
    "question": "",
    "options": ["", "", "", ""],
    "correct_index": 0,
    "explanation": "short explanation of the correct answer"
  }}
]

Mix question difficulty and topics: geography, culture, food, history, and practical travel know-how (e.g. currency, customs, best season). Exactly 4 options per question, only one correct."""
    return call_claude_json(system, user, max_tokens=2500)


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
