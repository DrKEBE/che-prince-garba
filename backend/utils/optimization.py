"""
Optimisations de performance pour le système
"""
from functools import lru_cache
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json


class CacheManager:
    """Gestionnaire de cache pour optimiser les performances"""
    
    _cache: Dict[str, Any] = {}
    _cache_ttl: Dict[str, datetime] = {}
    
    @staticmethod
    def get(key: str, default=None):
        """Récupère une valeur du cache"""
        if key in CacheManager._cache:
            if key in CacheManager._cache_ttl:
                if datetime.utcnow() > CacheManager._cache_ttl[key]:
                    # Cache expiré
                    del CacheManager._cache[key]
                    del CacheManager._cache_ttl[key]
                    return default
            return CacheManager._cache[key]
        return default
    
    @staticmethod
    def set(key: str, value: Any, ttl_seconds: int = 300):
        """Définit une valeur dans le cache avec TTL"""
        CacheManager._cache[key] = value
        CacheManager._cache_ttl[key] = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    
    @staticmethod
    def delete(key: str):
        """Supprime une valeur du cache"""
        if key in CacheManager._cache:
            del CacheManager._cache[key]
        if key in CacheManager._cache_ttl:
            del CacheManager._cache_ttl[key]
    
    @staticmethod
    def clear():
        """Vide tout le cache"""
        CacheManager._cache.clear()
        CacheManager._cache_ttl.clear()


class QueryOptimizer:
    """Optimiseur de requêtes SQLAlchemy"""
    
    @staticmethod
    def optimize_product_query(query, include_stock: bool = False):
        """
        Optimise les requêtes de produits
        """
        from sqlalchemy.orm import selectinload, joinedload
        
        if include_stock:
            # Charger les mouvements de stock si nécessaire
            query = query.options(selectinload(Product.stock_movements))
        
        # Toujours charger les images et variants
        return query
    
    @staticmethod
    def optimize_sale_query(query, include_items: bool = True, 
                           include_client: bool = True):
        """
        Optimise les requêtes de ventes
        """
        from sqlalchemy.orm import selectinload, joinedload
        
        if include_items:
            query = query.options(
                selectinload(Sale.items).selectinload(SaleItem.product)
            )
        
        if include_client:
            query = query.options(joinedload(Sale.client))
        
        return query


@lru_cache(maxsize=128)
def get_cached_dashboard_stats(db_session, days: int = 30):
    """
    Cache les statistiques du dashboard
    """
    from crud.sales import sale as sale_crud
    from crud.product import product as product_crud
    
    # Statistiques avec cache
    cache_key = f"dashboard_stats_{days}_{datetime.utcnow().strftime('%Y%m%d')}"
    cached = CacheManager.get(cache_key)
    
    if cached:
        return cached
    
    # Calculer les statistiques
    stats = {
        "total_products": product_crud.count(db_session),
        "total_sales": sale_crud.get_daily_sales_summary(db_session),
        "top_products": sale_crud.get_top_products(db_session, days, 10)
    }
    
    # Mettre en cache pour 5 minutes
    CacheManager.set(cache_key, stats, 300)
    
    return stats


def bulk_operation_manager():
    """
    Gestionnaire d'opérations en masse pour optimiser les insertions/updates
    """
    class BulkManager:
        def __init__(self, db, batch_size: int = 100):
            self.db = db
            self.batch_size = batch_size
            self._buffer = []
        
        def add(self, obj):
            """Ajoute un objet au buffer"""
            self._buffer.append(obj)
            if len(self._buffer) >= self.batch_size:
                self.flush()
        
        def flush(self):
            """Exécute les insertions en masse"""
            if self._buffer:
                self.db.bulk_save_objects(self._buffer)
                self.db.commit()
                self._buffer.clear()
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.flush()
    
    return BulkManager