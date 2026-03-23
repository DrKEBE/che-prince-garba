# backend/middleware/dev_middleware.py
"""
Middleware pour le mode développement
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class DevMiddleware(BaseHTTPMiddleware):
    """Middleware pour le développement"""
    
    async def dispatch(self, request: Request, call_next):
        # Log des requêtes en dev
        logger.debug(f"[DEV] {request.method} {request.url}")
        
        # Ajouter des headers de dev si nécessaire
        response = await call_next(request)
        
        # Ajouter des headers CORS en dev
        if hasattr(request.app.state, 'settings') and request.app.state.settings.DEV_MODE:
            response.headers["X-Dev-Mode"] = "true"
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        return response

class DevBypassAuthMiddleware(BaseHTTPMiddleware):
    """Middleware pour bypass l'authentification en dev pour certaines routes"""
    
    def __init__(self, app, exempt_routes=None):
        super().__init__(app)
        self.exempt_routes = exempt_routes or []
    
    async def dispatch(self, request: Request, call_next):
        # Vérifier si la route est exemptée
        path = request.url.path
        if any(path.startswith(route) for route in self.exempt_routes):
            # Ajouter un user dev au request.state
            request.state.user = {
                "id": 1,
                "username": "dev_user",
                "role": "ADMIN",
                "is_dev": True
            }
            logger.debug(f"[DEV] Bypass auth for {path}")
        
        return await call_next(request)