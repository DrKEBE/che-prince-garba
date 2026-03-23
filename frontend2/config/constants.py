# frontend\config\constants.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de l'API
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_VERSION = "api/v1"
BASE_API_URL = f"{BACKEND_URL}/{API_VERSION}"

# Endpoints API
API_ENDPOINTS = {
    # Authentification
    "login": f"{BASE_API_URL}/auth/token",
    "register": f"{BASE_API_URL}/auth/register",
    "me": f"{BASE_API_URL}/auth/me",
    
    # Produits
    "products": f"{BASE_API_URL}/products",
    "product_detail": lambda id: f"{BASE_API_URL}/products/{id}",
    "product_stock": lambda id: f"{BASE_API_URL}/products/{id}/stock",
    
    # Ventes
    "sales": f"{BASE_API_URL}/sales",
    "sale_detail": lambda id: f"{BASE_API_URL}/sales/{id}",
    "create_sale": f"{BASE_API_URL}/sales",
    "refunds": f"{BASE_API_URL}/sales/refunds",
    
    # Clients
    "clients": f"{BASE_API_URL}/clients",
    "client_detail": lambda id: f"{BASE_API_URL}/clients/{id}",
    "client_stats": lambda id: f"{BASE_API_URL}/clients/{id}/stats",
    
    # Stock
    "stock_movements": f"{BASE_API_URL}/stock/movements",
    "stock_alerts": f"{BASE_API_URL}/stock/alerts",
    
    # Fournisseurs
    "suppliers": f"{BASE_API_URL}/suppliers",
    
    # Comptabilité
    "expenses": f"{BASE_API_URL}/accounting/expenses",
    "profit_analysis": f"{BASE_API_URL}/accounting/profit-analysis",
    
    # Dashboard
    "dashboard_stats": f"{BASE_API_URL}/dashboard/stats",
    "sales_trend": f"{BASE_API_URL}/dashboard/sales-trend",
    "top_products": f"{BASE_API_URL}/dashboard/top-products",
    
    # Rendez-vous
    "appointments": f"{BASE_API_URL}/appointments",
    
    # Rapports
    "reports": f"{BASE_API_URL}/accounting/financial-reports",
}

# Configuration de l'application
APP_CONFIG = {
    "name": "Luxe Beauté Management",
    "version": "2.0.0",
    "description": "Système de gestion premium pour instituts de beauté",
    "support_email": "support@luxebeauty.com",
    "max_upload_size": 10 * 1024 * 1024,  # 10 MB
}

# Constantes métier
PRODUCT_CATEGORIES = [
    "Soins Visage", "Soins Corps", "Maquillage", "Parfums", 
    "Accessoires", "Homme", "Femme", "Enfant", "Professionnel"
]

BRANDS = [
    "Chanel", "Dior", "Estée Lauder", "Lancôme", "Clarins",
    "La Roche-Posay", "Vichy", "Nuxe", "Yves Rocher", "L'Oréal"
]

PAYMENT_METHODS = {
    "CASH": "💵 Espèces",
    "MOBILE_MONEY": "📱 Saraly",
    "CARD": "💳 Carte Bancaire",
    "BANK_TRANSFER": "🏦 Virement Bancaire",
    "CHECK": "📋 Chèque"
}

CLIENT_TYPES = {
    "REGULAR": "🟢 Régulier",
    "VIP": "⭐ VIP",
    "FIDELITE": "👑 Fidélité",
    "WHOLESALER": "🏢 Grossiste"
}

STOCK_STATUS = {
    "EN_STOCK": "🟢 En stock",
    "ALERTE": "🟡 Alerte",
    "RUPTURE": "🔴 Rupture"
}

# Couleurs de l'application
COLORS = {
    "primary": "#FF6B9D",  # Rose chic
    "secondary": "#9B59B6",  # Violet
    "success": "#2ECC71",  # Vert
    "warning": "#F1C40F",  # Jaune
    "danger": "#E74C3C",  # Rouge
    "info": "#3498DB",  # Bleu
    "light": "#F8F9FA",
    "dark": "#2C3E50",
    "background": "#FFFFFF",
    "card_bg": "#FFFFFF",
    "sidebar_bg": "#2C3E50",
    "text_primary": "#2C3E50",
    "text_secondary": "#7F8C8D"
}

# Rôles utilisateur
USER_ROLES = {
    "ADMIN": "👑 Administrateur",
    "MANAGER": "💼 Gestionnaire",
    "CASHIER": "💰 Caissier",
    "STOCK_MANAGER": "📦 Gestionnaire Stock",
    "BEAUTICIAN": "💄 Esthéticienne"
}