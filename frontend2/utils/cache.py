"""
Système de cache pour optimiser les performances
"""
import streamlit as st
from datetime import datetime, timedelta
import json
import hashlib
from typing import Any, Optional, Dict, List
import threading

class CacheManager:
    """
    Gestionnaire de cache avec expiration automatique
    """
    
    def __init__(self):
        self._cache = {}
        self._cache_metadata = {}
        self._lock = threading.Lock()
    
    def _generate_key(self, func_name: str, *args, **kwargs) -> str:
        """Génère une clé de cache unique"""
        key_parts = [func_name]
        
        # Ajouter les arguments positionnels
        key_parts.extend(str(arg) for arg in args)
        
        # Ajouter les arguments nommés
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}={value}")
        
        # Générer un hash MD5
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur du cache
        """
        with self._lock:
            if key not in self._cache:
                return default
            
            # Vérifier l'expiration
            metadata = self._cache_metadata.get(key, {})
            expires_at = metadata.get('expires_at')
            
            if expires_at and datetime.now() > expires_at:
                # Cache expiré
                del self._cache[key]
                del self._cache_metadata[key]
                return default
            
            return self._cache.get(key, default)
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """
        Définit une valeur dans le cache avec TTL
        """
        with self._lock:
            self._cache[key] = value
            self._cache_metadata[key] = {
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=ttl_seconds),
                'ttl': ttl_seconds,
                'size': len(json.dumps(value)) if isinstance(value, (dict, list)) else 1
            }
    
    def delete(self, key: str) -> bool:
        """
        Supprime une valeur du cache
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._cache_metadata[key]
                return True
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Supprime toutes les clés correspondant à un pattern
        """
        count = 0
        with self._lock:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._cache[key]
                del self._cache_metadata[key]
                count += 1
        return count
    
    def clear(self) -> None:
        """
        Vide tout le cache
        """
        with self._lock:
            self._cache.clear()
            self._cache_metadata.clear()
    
    def exists(self, key: str) -> bool:
        """
        Vérifie si une clé existe dans le cache
        """
        with self._lock:
            if key not in self._cache:
                return False
            
            # Vérifier l'expiration
            metadata = self._cache_metadata.get(key, {})
            expires_at = metadata.get('expires_at')
            
            if expires_at and datetime.now() > expires_at:
                del self._cache[key]
                del self._cache_metadata[key]
                return False
            
            return True
    
    def get_with_callback(self, key: str, callback, ttl_seconds: int = 300, *args, **kwargs) -> Any:
        """
        Récupère une valeur du cache ou exécute la callback si absente
        """
        value = self.get(key)
        if value is not None:
            return value
        
        # Exécuter la callback
        value = callback(*args, **kwargs)
        
        # Mettre en cache
        if value is not None:
            self.set(key, value, ttl_seconds)
        
        return value
    
    def increment(self, key: str, amount: int = 1) -> int:
        """
        Incrémente une valeur numérique dans le cache
        """
        with self._lock:
            current = self._cache.get(key, 0)
            if isinstance(current, (int, float)):
                new_value = current + amount
                self._cache[key] = new_value
                return new_value
            return current
    
    def decrement(self, key: str, amount: int = 1) -> int:
        """
        Décrémente une valeur numérique dans le cache
        """
        return self.increment(key, -amount)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du cache
        """
        with self._lock:
            total_items = len(self._cache)
            total_size = sum(m.get('size', 0) for m in self._cache_metadata.values())
            
            expired_items = 0
            for key, metadata in self._cache_metadata.items():
                expires_at = metadata.get('expires_at')
                if expires_at and datetime.now() > expires_at:
                    expired_items += 1
            
            return {
                'total_items': total_items,
                'total_size_bytes': total_size,
                'expired_items': expired_items,
                'hit_ratio': self._calculate_hit_ratio(),
                'oldest_item': min((m.get('created_at') for m in self._cache_metadata.values() if m.get('created_at')), default=None),
                'newest_item': max((m.get('created_at') for m in self._cache_metadata.values() if m.get('created_at')), default=None)
            }
    
    def _calculate_hit_ratio(self) -> float:
        """Calcule le ratio de succès du cache"""
        hits = getattr(self, '_hits', 0)
        misses = getattr(self, '_misses', 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return hits / total
    
    def cleanup(self) -> int:
        """
        Nettoie les éléments expirés du cache
        """
        cleaned = 0
        now = datetime.now()
        
        with self._lock:
            keys_to_delete = []
            
            for key, metadata in self._cache_metadata.items():
                expires_at = metadata.get('expires_at')
                if expires_at and now > expires_at:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self._cache[key]
                del self._cache_metadata[key]
                cleaned += 1
        
        return cleaned

# Cache global
global_cache = CacheManager()

# Décorateur de cache
def cached(ttl_seconds: int = 300):
    """
    Décorateur pour mettre en cache les résultats de fonction
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Générer une clé de cache basée sur la fonction et ses arguments
            cache_key = f"{func.__module__}.{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            # Vérifier le cache
            cached_result = global_cache.get(cache_key)
            if cached_result is not None:
                # Mettre à jour les statistiques de hits
                if not hasattr(wrapper, '_hits'):
                    wrapper._hits = 0
                wrapper._hits += 1
                return cached_result
            
            # Exécuter la fonction
            result = func(*args, **kwargs)
            
            # Mettre en cache
            if result is not None:
                global_cache.set(cache_key, result, ttl_seconds)
            
            # Mettre à jour les statistiques de misses
            if not hasattr(wrapper, '_misses'):
                wrapper._misses = 0
            wrapper._misses += 1
            
            return result
        
        # Ajouter des attributs pour les statistiques
        wrapper._hits = 0
        wrapper._misses = 0
        
        # Ajouter une méthode pour obtenir les statistiques
        def get_cache_stats():
            return {
                'hits': wrapper._hits,
                'misses': wrapper._misses,
                'hit_ratio': wrapper._hits / (wrapper._hits + wrapper._misses) if (wrapper._hits + wrapper._misses) > 0 else 0
            }
        
        wrapper.get_cache_stats = get_cache_stats
        
        return wrapper
    return decorator

# Cache pour Streamlit
class StreamlitCache:
    """
    Adaptateur de cache pour Streamlit
    """
    
    @staticmethod
    @st.cache_data(ttl=300)
    def cache_data(func, *args, **kwargs):
        """Cache de données Streamlit"""
        return func(*args, **kwargs)
    
    @staticmethod
    @st.cache_resource
    def cache_resource(func, *args, **kwargs):
        """Cache de ressources Streamlit"""
        return func(*args, **kwargs)
    
    @staticmethod
    def clear_all():
        """Efface tous les caches Streamlit"""
        st.cache_data.clear()
        st.cache_resource.clear()

# Fonctions utilitaires de cache
def cache_response(endpoint: str, params: dict = None, ttl: int = 300):
    """
    Décorateur pour mettre en cache les réponses API
    """
    def decorator(func):
        @cached(ttl_seconds=ttl)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern: str):
    """Invalide le cache correspondant à un pattern"""
    return global_cache.delete_pattern(pattern)

def get_cache_info():
    """Récupère les informations du cache"""
    return global_cache.get_stats()