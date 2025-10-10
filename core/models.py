import json
from typing import List, Optional
from sqlmodel import Field, SQLModel, JSON, Column
from datetime import datetime

class NewsBriefing(SQLModel, table=True):
    """
    Represents a single piece of intelligence that has been analyzed.
    """
    id: Optional[int] = Field(default=None, primary_key=True)

    # Raw Intel
    source_name: str = Field(index=True)
    headline: str
    summary: str
    source_url: str = Field(unique=True)

    # Analysis & Scoring
    news_value_score: int = Field(default=0, index=True)
    score_analysis_prompt: str  # The prompt used for Gemini analysis

    # AI-generated content package
    instagram_caption: str
    instagram_hashtags: List[str] = Field(sa_column=Column(JSON))
    image_generation_prompt: str

    # Metadata
    status: str = Field(default="pending_review", index=True) # pending_review, approved, dismissed, posted
    created_at: datetime = Field(default_factory=datetime.utcnow)
    posted_at: Optional[datetime] = None

    # For uniqueness check
    entities: List[str] = Field(sa_column=Column(JSON), default=[])

class Source(SQLModel, table=True):
    """
    Represents a data source to be scraped.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    url: str # e.g., RSS feed URL, Telegram channel link
    type: str # 'rss', 'telegram', 'x', 'api'
    authority_tier: int = Field(default=3, ge=1, le=5)
    is_active: bool = Field(default=True)