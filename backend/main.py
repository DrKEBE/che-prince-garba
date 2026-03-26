# backend\main.py
import sys
from pathlib import Path

from sqlalchemy import text

# Assurer que le dossier courant est dans le PYTHONPATH
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from typing import Dict, Any

from database import engine, Base, get_db
from core.config import settings
from core.exceptions import CustomException, NotFoundException
from sqlalchemy.orm import Session

from middleware.dev_middleware import DevMiddleware, DevBypassAuthMiddleware
from core.dev_config import dev_config

# Import des routes
from routes import (
    products,
    sales,
    stock,
    accounting,
    suppliers,
    clients,
    dashboard,
    auth,
    appointments  
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # seulement la console
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Démarrage
    logger.info("Démarrage de l'application Luxe Beauté Management")
    
    # Création des tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Base de données initialisée")
    except Exception as e:
        logger.error(f"Erreur d'initialisation de la base de données: {e}")
    
    yield
    
    # Arrêt
    logger.info("Arrêt de l'application")

# Création de l'application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Système complet de gestion pour institut de beauté luxe",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

if settings.DEV_MODE:
    # Middleware de dev
    app.add_middleware(DevMiddleware)
    
    # Middleware pour bypass l'auth sur certaines routes
    app.add_middleware(
        DevBypassAuthMiddleware,
        exempt_routes=dev_config.DEV_EXEMPT_ROUTES
    )
    
    # Logger en mode dev
    logger.info("Mode développement activé")
    logger.info(f"Env: {settings.ENVIRONMENT}")
    logger.info(f"CORS: {settings.BACKEND_CORS_ORIGINS}")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # Utilisation de la config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Gestionnaire d'exceptions global
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error(f"Erreur non gérée: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Une erreur interne est survenue"}
    )

# Montage des fichiers statiques
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Routes de santé
@app.get("/", tags=["Santé"])
async def root():
    return {
        "message": f"Bienvenue sur {settings.APP_NAME}",
        "version": "2.0.0",
        "status": "operational"
    }

@app.get("/health", tags=["Santé"])
async def health_check(db: Session = Depends(get_db)):
    """Vérification de la santé de l'application"""
    try:
        # Test de la connexion à la base de données
        db.execute(text("SELECT 1"))
        
        # Vérification de l'espace disque
        import shutil
        total, used, free = shutil.disk_usage("/")
        
        return {
            "status": "healthy",
            "database": "connected",
            "disk_space": {
                "total_gb": round(total / (2**30), 2),
                "used_gb": round(used / (2**30), 2),
                "free_gb": round(free / (2**30), 2),
                "free_percentage": round((free / total) * 100, 2)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service indisponible"
        )

# Inclusion des routes
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(products.router, prefix="/api/v1")
app.include_router(sales.router, prefix="/api/v1")
app.include_router(stock.router, prefix="/api/v1")
app.include_router(suppliers.router, prefix="/api/v1")
app.include_router(clients.router, prefix="/api/v1")
app.include_router(accounting.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")


# Route d'info système
@app.get("/api/v1/system/info", tags=["Système"])
async def system_info():
    """Informations sur le système"""
    import platform
    import psutil
    from datetime import datetime
    
    return {
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        },
        "application": {
            "name": settings.APP_NAME,
            "version": "2.0.0",
            "debug": settings.DEBUG,
            "uptime": datetime.utcnow().isoformat()
        }
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        log_level="debug"
    )