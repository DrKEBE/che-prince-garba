# backend\core\config.py
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # ===== Environnement =====
    ENVIRONMENT: str = "production"  # production, development, testing
    DEV_MODE: bool = True
    DEBUG: bool = True
    
    # ===== Database =====
    DATABASE_URL: str = "sqlite:///./che_prince_garba.db"  # Utilisez la DB principale
    
    APP_NAME: str = "Luxe Beauté Management"
    APP_VERSION: str = "2.0.0"
    
    # ===== Uploads =====
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # ===== JWT =====
    SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ===== CORS =====
    BACKEND_CORS_ORIGINS: List[str] = [
        "https://che-prince-garba.netlify.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",  # Ajouter cette alternative
        "http://localhost:5173",   # Vite par défaut
    ]

    # ===== Trusted Hosts =====
    ALLOWED_HOSTS: List[str] = ["*"]  # À surcharger en production    
    
    # ===== Développement =====
    DEV_TOKEN: Optional[str] = "fake-token-admin"  # Défaut pour le dev
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"

settings = Settings()