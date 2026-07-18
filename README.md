# Waypoint — AI Travel Planner

An AI travel assistant with:
- **Destination suggestions** based on preferences
- **Day-wise itinerary** generation
- **Budget estimate** with a category breakdown
- **Packing checklist** tailored to the trip
- **Interactive flashcards** (flip cards) about any destination — culture, language, food, history, practical tips
- **Interactive quiz** (multiple choice, scored) about any destination

Single container: FastAPI backend + a static HTML/JS frontend, calling the Claude API. Ships as one Docker image, deployable to **Cloud Run**.

## Project layout

```
travel-planner/
  app/
    main.py            FastAPI app (API routes + serves the frontend)
    requirements.txt
    Dockerfile
    .dockerignore
    .env.example
    static/
      index.html        Frontend (vanilla HTML/CSS/JS, no build step)
  cloudbuild.yaml        Cloud Build -> Cloud Run pipeline
  IMPLEMENTATION_PLAN.md Full GCP deployment plan
```

## Run locally

```bash
cd app
cp .env.example .env        # add your real ANTHROPIC_API_KEY
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export $(cat .env | xargs)
uvicorn main:app --reload --port 8080
```

Open http://localhost:8080

## Run locally with Docker

```bash
cd app
docker build -t waypoint .
docker run -p 8080:8080 -e ANTHROPIC_API_KEY=sk-ant-xxxx waypoint
```

## Deploy to Cloud Run (quick path)

```bash
gcloud run deploy waypoint \
  --source ./app \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-secrets=ANTHROPIC_API_KEY=anthropic-api-key:latest
```

See `IMPLEMENTATION_PLAN.md` for the full step-by-step plan, including the CI/CD pipeline via `cloudbuild.yaml`.
