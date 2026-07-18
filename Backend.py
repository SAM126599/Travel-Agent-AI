import os
import json
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try importing Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai package not available. Running in Mock Mode.")

app = FastAPI(title="AI Travel Planner & Flashcard Assistant")

# Request Model
class TravelPlanRequest(BaseModel):
    destination: str
    duration: int = Field(ge=1, le=10, default=3)
    travel_style: str = Field(default="Balanced")
    budget_level: str = Field(default="Moderate")

# Response Schemas for Pydantic (used for validation & response_schema SDK support)
class Activity(BaseModel):
    title: str = Field(description="Title of the activity")
    description: str = Field(description="Detailed 2-3 sentence description of the activity and highlights")
    time_of_day: str = Field(description="Must be 'Morning', 'Afternoon', or 'Evening'")
    cost_estimate: str = Field(description="Estimated cost of the activity (e.g. Free, $15, $35)")

class DayPlan(BaseModel):
    day_number: int = Field(description="The day index, starting at 1")
    theme: str = Field(description="Overall theme of this day's exploration")
    activities: List[Activity] = Field(description="Exactly 3 activities for this day (Morning, Afternoon, Evening)")

class BudgetCategory(BaseModel):
    category: str = Field(description="e.g. Accommodation, Food, Transport, Activities, Miscellaneous")
    amount: float = Field(description="Estimated cost in USD")
    details: str = Field(description="Short description of what is included")

class BudgetEstimate(BaseModel):
    categories: List[BudgetCategory] = Field(description="List of budget categories with details")
    total_estimated_usd: float = Field(description="Sum of all category costs")
    saving_tips: List[str] = Field(description="At least 3 practical cost-saving tips for this destination")

class PackingItem(BaseModel):
    item: str = Field(description="Name of the item to pack")
    category: str = Field(description="Must be one of: Clothing, Electronics, Toiletries, Documents, Essentials")
    why_needed: str = Field(description="Brief reason based on destination details or travel style")

class Flashcard(BaseModel):
    front: str = Field(description="Topic/Word in English")
    back: str = Field(description="Local translation, etiquette rule, or fun fact answer")
    pronunciation: str = Field(description="Pronunciation guide for foreign phrases (or empty string for facts)")
    category: str = Field(description="Must be one of: Language, Etiquette, Fun Fact")

class TravelPlanResponse(BaseModel):
    destination: str = Field(description="Name of the destination and country")
    tagline: str = Field(description="Catchy tagline describing the trip vibe")
    description: str = Field(description="Overview paragraph of the customized trip matching the style and budget")
    best_time_to_visit: str = Field(description="Short sentence recommending when to visit")
    itinerary: List[DayPlan] = Field(description="Day-by-day plan")
    budget: BudgetEstimate = Field(description="Cost details and recommendations")
    packing_checklist: List[PackingItem] = Field(description="Custom packing checklist")
    flashcards: List[Flashcard] = Field(description="Useful learning cards for vocabulary, etiquette, or fun facts")

# Mock data generator in case Gemini API is not available or key is missing
def get_mock_travel_plan(destination: str, duration: int, travel_style: str, budget_level: str) -> TravelPlanResponse:
    dest = destination.strip().title() or "Paris"
    
    logger.info(f"Generating mock travel plan for {dest}")
    
    # Custom adjustments based on budget
    budget_multiplier = {"Low": 0.5, "Moderate": 1.0, "High": 2.2}.get(budget_level, 1.0)
    
    # Adjust description and theme based on style
    style_desc = {
        "Adventure": "thrilling outdoor excursions, hidden spots, and active exploring",
        "Relaxing": "leisurely strolls, scenic viewpoints, and peaceful retreats",
        "Cultural": "museums, historical monuments, local art, and deep heritage sites",
        "Foodie": "incredible culinary tours, street food markets, and fine dining highlights",
        "Balanced": "a perfect mix of key sightseeing, local experiences, and leisure time"
    }.get(travel_style, "a wonderful curated mix of top highlights and local secrets")

    days = []
    for day in range(1, duration + 1):
        if day == 1:
            theme = "Iconic Highlights & Arrival"
            act1 = Activity(title="Morning Arrival & Neighborhood Stroll", description=f"Check into your accommodation and explore the surrounding neighborhood in {dest}.", time_of_day="Morning", cost_estimate="Free")
            act2 = Activity(title="Main Landmark Visit", description=f"Visit the most famous landmark of {dest} and capture memorable photos.", time_of_day="Afternoon", cost_estimate=f"${int(20 * budget_multiplier)}")
            act3 = Activity(title="Welcome Dinner & Local Delicacy", description="Dine at a highly-recommended traditional eatery to taste the local specialty.", time_of_day="Evening", cost_estimate=f"${int(30 * budget_multiplier)}")
        elif day == duration:
            theme = "Scenic Views & Final Farewell"
            act1 = Activity(title="Morning Market Tour", description="Browse local artisan stalls and pick up souvenirs.", time_of_day="Morning", cost_estimate="Free")
            act2 = Activity(title="Panoramic Lookout Point", description="Head to a high point or tower to see the entire skyline.", time_of_day="Afternoon", cost_estimate=f"${int(15 * budget_multiplier)}")
            act3 = Activity(title="Sunset Dinner Cruise or Rooftop Lounge", description="Celebrate the final night with spectacular views and a delicious dinner.", time_of_day="Evening", cost_estimate=f"${int(45 * budget_multiplier)}")
        else:
            theme = f"Deep Dive into {travel_style} Culture"
            act1 = Activity(title="Off-the-beaten-path Discovery", description=f"Explore hidden parks, boutique alleys, or a local museum matching the {travel_style} vibe.", time_of_day="Morning", cost_estimate=f"${int(10 * budget_multiplier)}")
            act2 = Activity(title="Interactive Workshop or Cooking Class", description="Participate in an hands-on cultural workshop led by a local artisan.", time_of_day="Afternoon", cost_estimate=f"${int(40 * budget_multiplier)}")
            act3 = Activity(title="Night Walk & Street Food Crawl", description="Wander through active night streets, sample small bites, and observe local nightlife.", time_of_day="Evening", cost_estimate=f"${int(25 * budget_multiplier)}")
            
        days.append(DayPlan(day_number=day, theme=theme, activities=[act1, act2, act3]))

    # Categories
    categories = [
        BudgetCategory(category="Accommodation", amount=float(int(100 * duration * budget_multiplier)), details="Comfortable centrally-located stay"),
        BudgetCategory(category="Food", amount=float(int(45 * duration * budget_multiplier)), details="3 meals daily plus local snacks"),
        BudgetCategory(category="Transport", amount=float(int(15 * duration * budget_multiplier)), details="Public transport passes and occasional taxis"),
        BudgetCategory(category="Activities", amount=float(int(30 * duration * budget_multiplier)), details="Entry tickets and guided experiences"),
        BudgetCategory(category="Miscellaneous", amount=float(int(20 * duration * budget_multiplier)), details="Emergency cash and souvenir shopping")
    ]
    total_usd = sum(c.amount for c in categories)

    packing = [
        PackingItem(item="Comfortable Walking Shoes", category="Clothing", why_needed="Crucial for walking miles on historical cobblestones and sightseeing routes."),
        PackingItem(item="Universal Adapter", category="Electronics", why_needed="Power socket pins may vary from your home country."),
        PackingItem(item="Reusable Water Bottle", category="Essentials", why_needed="Stay hydrated during active walking tours while saving money and plastic."),
        PackingItem(item="Local Currency (Some cash)", category="Documents", why_needed="Some street vendors or taxis may not accept credit cards."),
        PackingItem(item="Weather-appropriate outerwear", category="Clothing", why_needed=f"Based on seasonal averages for {dest}.")
    ]

    flashcards = [
        Flashcard(front="Hello / Good day", back="Bonjour / Konnichiwa / Ciao (Depending on language)", pronunciation="Varies by location", category="Language"),
        Flashcard(front="Thank you very much", back="Merci beaucoup / Arigatou gozaimasu / Grazie mille", pronunciation="Varies", category="Language"),
        Flashcard(front="How much is this?", back="Combien ça coûte? / Kore wa ikura desu ka?", pronunciation="Varies", category="Language"),
        Flashcard(front="Tipping Custom", back="Usually included in bill in Europe/Japan, expected (15-20%) in USA.", pronunciation="", category="Etiquette"),
        Flashcard(front="Greeting style", back="Bow in Japan, handshake in Europe, wave/hug in Americas.", pronunciation="", category="Etiquette"),
        Flashcard(front="Fun Fact", back="Kyoto was once the capital of Japan and has over 1,600 temples.", pronunciation="", category="Fun Fact")
    ]

    return TravelPlanResponse(
        destination=dest,
        tagline=f"Unveiling the best of {dest} for your {travel_style} getaway!",
        description=f"Welcome to {dest}! This custom itinerary balances a {travel_style} travel style with a {budget_level} budget over {duration} exciting days. Prepare to experience {style_desc}.",
        best_time_to_visit="Spring (April-May) or Autumn (September-October) for pleasant weather and beautiful scenery.",
        itinerary=days,
        budget=BudgetEstimate(categories=categories, total_estimated_usd=total_usd, saving_tips=[
            "Purchase local transit passes rather than buying single-trip tickets.",
            "Eat your largest meal during lunch when restaurants offer lower-priced set menus.",
            "Seek out free museum admission days (often the first Sunday of the month)."
        ]),
        packing_checklist=packing,
        flashcards=flashcards
    )

# AI Generation Endpoint using the new google-genai SDK
@app.post("/api/generate-plan", response_model=TravelPlanResponse)
async def generate_plan(request: TravelPlanRequest):
    # Validate API key
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key or not GENAI_AVAILABLE:
        # Fallback to mock data if no key or package is present
        logger.info("Using mock travel planner: GEMINI_API_KEY is not configured or google-genai is missing.")
        return get_mock_travel_plan(request.destination, request.duration, request.travel_style, request.budget_level)

    try:
        # Initialize the new GenAI Client
        client = genai.Client(api_key=api_key)
        
        # Construct the detailed prompt
        prompt = f"""
        You are an expert AI Travel Assistant. Generate a highly detailed, personalized travel plan based on these parameters:
        - Destination: {request.destination}
        - Duration: {request.duration} days
        - Travel Style: {request.travel_style}
        - Budget Level: {request.budget_level}

        Make sure you provide:
        1. An itinerary of exactly {request.duration} days. Each day must contain exactly 3 chronological activities (Morning, Afternoon, Evening).
        2. A budget breakdown matching the duration and budget level. Ensure the categories sum exactly to total_estimated_usd.
        3. At least 5 detailed packing checklist items relevant to the destination weather and activities.
        4. At least 6 flippable travel flashcards:
           - A few key vocabulary items (front is English, back is local translation with pronunciation).
           - An etiquette rule (e.g. greetings, table manners, tipping customs).
           - An interesting fun fact or historical trivia about the destination.
        """

        # Generate content with native pydantic schema validation
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TravelPlanResponse,
                temperature=0.7,
            )
        )

        # Parse the JSON response
        data = json.loads(response.text)
        
        # Validate using Pydantic model
        validated_data = TravelPlanResponse(**data)
        return validated_data

    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        # If API errors out, return a high-quality fallback plan for the destination
        return get_mock_travel_plan(request.destination, request.duration, request.travel_style, request.budget_level)

# Mount the static directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Catch-all to serve index.html
@app.get("/")
async def get_index():
    return FileResponse("app/static/index.html")

# Create static directories if they don't exist
os.makedirs("app/static", exist_ok=True)
