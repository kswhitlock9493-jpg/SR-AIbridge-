"""
Configuration management for SR-AIbridge backend
Centralized configuration with environment variable support
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv()


class Settings:
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "SR-AIbridge Backend"
    APP_VERSION: str = "1.2.0-sqlite-first"
    APP_DESCRIPTION: str = "SQLite-first SR-AIbridge backend with comprehensive health checks and self-heal"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Database
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite").lower()
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///bridge.db")
    
    # Bridge Services
    VAULT_URL: str = os.getenv("VAULT_URL", "https://bridge.netlify.app/api/vault")
    CASCADE_MODE: str = os.getenv("CASCADE_MODE", "development")
    FEDERATION_SYNC_KEY: str = os.getenv("FEDERATION_SYNC_KEY", "")
    
    # Optional Monitoring
    DATADOG_API_KEY: str = os.getenv("DATADOG_API_KEY", "")
    DATADOG_REGION: str = os.getenv("DATADOG_REGION", "us")
    
    # Deploy Diagnostics
    AUTO_DIAGNOSE: bool = os.getenv("AUTO_DIAGNOSE", "true").lower() == "true"
    DIAGNOSE_WEBHOOK_URL: str = os.getenv("DIAGNOSE_WEBHOOK_URL", "")
    
    # CORS Configuration
    CORS_ALLOW_ALL: bool = os.getenv("CORS_ALLOW_ALL", "false").lower() == "true"
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://127.0.0.1:3000,https://bridge.netlify.app,https://sr-aibridge.netlify.app"
    ).split(",")
    
    @property
    def async_database_url(self) -> str:
        """Convert database URL to async format"""
        if self.DATABASE_URL.startswith("sqlite:///"):
            return self.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
        elif self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        elif self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
        return self.DATABASE_URL
        
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins with additional development and deployment URLs"""
        origins = [
            *self.ALLOWED_ORIGINS,
            "https://*.netlify.app",  # All Netlify subdomains
            "https://*.onrender.com",  # All Render subdomains
            "http://localhost:3001",   # Alternative dev port
            "https://localhost:3000",  # HTTPS dev
            "https://localhost:3001",  # HTTPS alternative dev
            "http://127.0.0.1:3001",   # IPv4 alternative
            "https://127.0.0.1:3000",  # HTTPS IPv4
            "https://127.0.0.1:3001"   # HTTPS IPv4 alternative
        ]
        return origins


# Global settings instance
settings = Settings()