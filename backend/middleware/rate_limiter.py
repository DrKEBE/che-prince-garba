# backend\middleware\rate_limiter.py
"""
Middleware de rate limiting pour prévenir les abus
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import time
from typing import Dict, List, Tuple
import asyncio
from collections import defaultdict

class RateLimiter:
    """
    Implémentation simple de rate limiting
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def is_rate_limited(self, key: str) -> Tuple[bool, Dict[str, any]]:
        """
        Vérifie si une clé est rate limitée
        """
        async with self.lock:
            current_time = time.time()
            
            # Nettoyer les vieilles requêtes
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if current_time - req_time < 60
            ]
            
            # Vérifier la limite
            if len(self.requests[key]) >= self.requests_per_minute:
                # Calculer le temps d'attente
                oldest_request = min(self.requests[key])
                wait_time = 60 - (current_time - oldest_request)
                
                return True, {
                    "limit": self.requests_per_minute,
                    "remaining": 0,
                    "reset_time": int(current_time + wait_time),
                    "retry_after": int(wait_time)
                }
            
            # Ajouter la requête actuelle
            self.requests[key].append(current_time)
            
            return False, {
                "limit": self.requests_per_minute,
                "remaining": self.requests_per_minute - len(self.requests[key]),
                "reset_time": int(current_time + 60),
                "retry_after": 0
            }

class RateLimitMiddleware:
    """
    Middleware FastAPI pour le rate limiting
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        self.app = app
        self.rate_limiter = RateLimiter(requests_per_minute)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Obtenir la clé de rate limiting (IP ou user_id)
            client_ip = request.client.host if request.client else "unknown"
            user_id = request.headers.get("X-User-ID", client_ip)
            
            # Vérifier le rate limiting
            is_limited, rate_info = await self.rate_limiter.is_rate_limited(user_id)
            
            if is_limited:
                response = JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Trop de requêtes. Réessayez dans {rate_info['retry_after']} secondes.",
                        "retry_after": rate_info['retry_after']
                    },
                    headers={
                        "X-RateLimit-Limit": str(rate_info['limit']),
                        "X-RateLimit-Remaining": str(rate_info['remaining']),
                        "X-RateLimit-Reset": str(rate_info['reset_time']),
                        "Retry-After": str(rate_info['retry_after'])
                    }
                )
                await response(scope, receive, send)
                return
        
        await self.app(scope, receive, send)

# Configuration par défaut
default_rate_limiter = RateLimiter(requests_per_minute=100)