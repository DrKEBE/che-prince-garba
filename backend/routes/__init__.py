# backend/routes/__init__.py
"""
Import de toutes les routes
"""
from .products import router as products_router
from .sales import router as sales_router
from .stock import router as stock_router
from .suppliers import router as suppliers_router
from .clients import router as clients_router
from .accounting import router as accounting_router
from .dashboard import router as dashboard_router
from .auth import router as auth_router
from .appointments import router as appointments_router

__all__ = [
    "products_router",
    "sales_router",
    "stock_router",
    "suppliers_router",
    "clients_router",
    "accounting_router",
    "dashboard_router",
    "auth_router",
    "appointments_router"
]