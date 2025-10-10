import json
from typing import List
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select, delete
from contextlib import asynccontextmanager

from core.config import settings
from core.database import engine, create_db_and_tables
from core.models import NewsBriefing, Source
from workers.tasks import post_to_instagram_task # Import the celery task

# --- Database Session Dependency ---

def get_session():
    """
    Dependency to get a database session.
    Ensures the session is always closed after the request.
    """
    with Session(engine) as session:
        yield session

# --- FastAPI App Lifespan ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    """
    print("--- Sentinel Protocol API Starting Up ---")
    create_db_and_tables()
    # You could also pre-load sources from sources.json here
    yield
    print("--- Sentinel Protocol API Shutting Down ---")

# --- FastAPI App Initialization ---

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}"}

@app.get("/api/alerts", response_model=List[NewsBriefing])
def get_alerts(session: Session = Depends(get_session)):
    """
    Fetches all briefings with a score above the threshold that are pending review.
    """
    statement = select(NewsBriefing).where(
        NewsBriefing.news_value_score >= settings.NEWS_VALUE_THRESHOLD,
        NewsBriefing.status == "pending_review"
    ).order_by(NewsBriefing.created_at.desc())

    alerts = session.exec(statement).all()
    return alerts

@app.post("/api/alerts/{briefing_id}/approve")
def approve_alert(briefing_id: int, session: Session = Depends(get_session)):
    """
    Approves an alert and triggers the Instagram posting task.
    """
    briefing = session.get(NewsBriefing, briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")

    if briefing.status != "pending_review":
        raise HTTPException(status_code=400, detail=f"Briefing has already been actioned with status: {briefing.status}")

    # Update status in the database
    briefing.status = "approved"
    session.add(briefing)
    session.commit()
    session.refresh(briefing)

    # Trigger the Celery task
    post_to_instagram_task.delay(briefing.id)

    return {"message": "Briefing approved. Instagram posting task initiated.", "briefing_id": briefing.id}

@app.post("/api/alerts/{briefing_id}/dismiss")
def dismiss_alert(briefing_id: int, session: Session = Depends(get_session)):
    """
    Dismisses an alert, preventing it from being shown again.
    """
    briefing = session.get(NewsBriefing, briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")

    if briefing.status != "pending_review":
        raise HTTPException(status_code=400, detail=f"Briefing has already been actioned with status: {briefing.status}")

    briefing.status = "dismissed"
    session.add(briefing)
    session.commit()

    return {"message": "Briefing dismissed.", "briefing_id": briefing.id}


@app.get("/api/settings")
def get_settings():
    """
    Returns the current application settings.
    Sensitive keys should be excluded in a production environment.
    """
    return settings.dict()

@app.get("/api/sources", response_model=List[Source])
def get_sources(session: Session = Depends(get_session)):
    """
    Retrieves all configured sources from the database.
    """
    sources = session.exec(select(Source)).all()
    return sources

@app.post("/api/sources/reload")
def reload_sources_from_json(session: Session = Depends(get_session)):
    """
    Clears the sources table and reloads it from the `config/sources.json` file.
    This is a simple way to manage sources without a full CRUD UI.
    """
    try:
        with open("config/sources.json", "r") as f:
            sources_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to read or parse sources.json: {e}")

    # Clear existing sources
    session.exec(delete(Source))

    # Load new sources
    new_sources = []
    for s_data in sources_data:
        source = Source(**s_data)
        session.add(source)
        new_sources.append(source)

    session.commit()
    return {"message": f"Successfully reloaded {len(new_sources)} sources from sources.json."}