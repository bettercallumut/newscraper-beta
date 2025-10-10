from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    """
    Application-wide settings.
    """
    # Core settings
    APP_NAME: str = "The Sentinel Protocol"
    DEBUG: bool = Field(default=False)

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./sentinel.db")

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")
    CHECK_INTERVAL_MINUTES: int = Field(default=15, description="The interval in minutes for the master sweep task.")

    # News Value Algorithm
    NEWS_VALUE_THRESHOLD: int = Field(default=7, ge=1, le=10, description="The score threshold to trigger an alert.")
    KEYWORD_WEIGHT: float = Field(default=0.4)
    SOURCE_AUTHORITY_WEIGHT: float = Field(default=0.2)
    SOCIAL_VELOCITY_WEIGHT: float = Field(default=0.3)
    SENTIMENT_INTENSITY_WEIGHT: float = Field(default=0.1)
    SOCIAL_VELOCITY_MULTIPLIER: float = Field(default=1.5)

    # API Keys
    GEMINI_API_KEY: str = Field(default="YOUR_GEMINI_API_KEY")
    DALLE3_API_KEY: str = Field(default="YOUR_DALLE3_API_KEY")

    # Instagram Credentials
    INSTAGRAM_USERNAME: str = Field(default="YOUR_INSTAGRAM_USERNAME")
    INSTAGRAM_PASSWORD: str = Field(default="YOUR_INSTAGRAM_PASSWORD")

    # High-impact keywords for analysis
    HIGH_IMPACT_KEYWORDS: List[str] = Field(default=["son dakika", "istifa", "patlama", "cinayet", "kaza", "ekonomik kriz"])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate the settings
settings = Settings()