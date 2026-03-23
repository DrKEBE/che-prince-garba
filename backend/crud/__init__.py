# backend/crud/__init__.py
from .base import CRUDBase
from .product import product as product_crud
from .sale_service import sale_refund_service
from .client import client as client_crud
from .sales_stats import SalesStatsService

__all__ = [
    "CRUDBase",
    "product_crud",
    "sale_refund_service", 
    "client_crud",
    "SalesStatsService"
]