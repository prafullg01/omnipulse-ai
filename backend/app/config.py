"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class ChurnThresholds:
    """
    Centralized churn probability thresholds used across all modules.
    
    Usage:
        from app.config import ChurnThresholds
        if profile.churn_probability > ChurnThresholds.HIGH:
            ...
    
    Threshold definitions:
        LOW:      < 0.30 — Healthy customers with minimal churn risk
        MEDIUM:   0.30 - 0.59 — Moderate risk, monitor engagement
        HIGH:     0.60 - 0.79 — Elevated risk, proactive outreach recommended
        CRITICAL: >= 0.80 — Urgent intervention required
    
    Executive reporting uses HIGH (0.70) as the "high-risk" cutoff.
    Churn Center uses the full 4-tier system.
    """
    LOW = 0.30
    MEDIUM = 0.60
    HIGH = 0.70       # Used for executive reporting & revenue-at-risk calculations
    CRITICAL = 0.80   # Used for urgent interventions in Churn Center


class AttributionConfig:
    """
    Campaign attribution configuration.
    
    Documents the known limitation: campaign_responses customer IDs
    only partially overlap with orders customer IDs, so campaign
    revenue attribution is incomplete.
    """
    METHOD = "HYBRID"               # Direct match + behavioral estimation
    CONFIDENCE_LABEL = "Medium"     # Overall attribution confidence
    DIRECT_MATCH_RATE = 34.9        # % of campaign recipients matched to orders
    REVENUE_LABEL = "Direct Campaign Conversions"
    REVENUE_NOTE = "Based on confirmed conversions from campaign_responses table"


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "OmniPulse AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "omnipulse-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "sqlite:///./omnipulse.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET_KEY: str = "omnipulse-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours
    
    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
