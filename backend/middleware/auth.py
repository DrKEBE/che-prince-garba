# backend\middleware\auth.py
# MODIFIEZ le début du fichier :
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import List, Optional

from core.config import settings
from database import get_db
from models import User
from core.exceptions import CustomException
from schemas import UserRole

# Token URL relative - IMPORTANT pour le proxy Vite
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",  # URL relative (sans /api/v1)
    auto_error=False  # Ne pas lever d'erreur si pas de token
)

async def get_current_user(
    request: Request,  # Ajoutez request pour vérifier le state
    token: Optional[str] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    """
    Récupère l'utilisateur courant avec priorité au mode DEV.
    """
    # ===== VÉRIFICATION PRIMAIRE: Mode DEV via request.state =====
    if hasattr(request.state, 'user') and request.state.user:
        return request.state.user

    # ===== MODE DEV: Retourne admin si pas de token =====
    if settings.DEV_MODE and not token:
        return {
            "id": 1,
            "username": "dev_admin",
            "email": "dev@example.com",
            "role": "ADMIN",
            "full_name": "Admin Dev",
            "is_dev": True
        }

    # ===== MODE DEV: Avec token dev =====
    if settings.DEV_MODE and token:
        # Vérifier si c'est un token de développement
        from core.dev_config import dev_config
        if dev_config.is_dev_token(token):
            role = dev_config.get_role_from_token(token)
            user = dev_config.get_dev_user(username=role)
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "full_name": user["full_name"],
                "is_dev": True
            }

    # ===== MODE PRODUCTION =====
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        
        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compte désactivé"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "is_dev": False
    }

def require_role(allowed_roles: List[UserRole]):
    """
    Dépendance FastAPI pour vérifier les rôles d'accès.
    Usage:
        @app.get("/admin")
        def admin_route(current_user = Depends(require_role([UserRole.admin]))):
            ...
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes"
            )
        return current_user
    return role_checker
