#backend\core\dev_config.py
"""
Configuration spécifique au développement
"""
from typing import Dict, Any, List
from core.config import settings

class DevConfig:
    """Configuration pour le mode développement"""
    
    # Token de développement accepté
    DEV_TOKENS = {
        "admin": "fake-token-admin",
        "manager": "fake-token-manager", 
        "cashier": "fake-token-cashier",
        "stock": "fake-token-stock"
    }
    
    # Utilisateurs de développement
    DEV_USERS = [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@luxe-beaute.fr",
            "full_name": "Administrateur",
            "role": "ADMIN",
            "permissions": ["all"]
        },
        {
            "id": 2,
            "username": "manager",
            "email": "manager@luxe-beaute.fr",
            "full_name": "Responsable",
            "role": "MANAGER",
            "permissions": ["view_dashboard", "manage_products", "manage_sales", "manage_clients"]
        },
        {
            "id": 3,
            "username": "cashier",
            "email": "cashier@luxe-beaute.fr",
            "full_name": "Caissier",
            "role": "CASHIER",
            "permissions": ["view_dashboard", "manage_sales", "view_products"]
        }
    ]
    
    # Routes exemptées d'authentification en dev
    DEV_EXEMPT_ROUTES = [
        "/api/v1/dashboard/stats",
        "/api/v1/dashboard/sales-trend",
        "/api/v1/dashboard/inventory-alerts",
        "/api/v1/dashboard/realtime-updates"
    ]
    
    @classmethod
    def get_dev_user(cls, user_id: int = None, username: str = None):
        """Récupère un utilisateur de développement"""
        if user_id:
            for user in cls.DEV_USERS:
                if user["id"] == user_id:
                    return user
        if username:
            for user in cls.DEV_USERS:
                if user["username"] == username:
                    return user
        return cls.DEV_USERS[0]  # Admin par défaut
    
    @classmethod
    def is_dev_token(cls, token: str) -> bool:
        """Vérifie si le token est un token de développement"""
        return token in cls.DEV_TOKENS.values()
    
    @classmethod
    def get_role_from_token(cls, token: str) -> str:
        """Extrait le rôle du token dev"""
        for role, dev_token in cls.DEV_TOKENS.items():
            if token == dev_token:
                return role.upper()
        return "ADMIN"

dev_config = DevConfig()