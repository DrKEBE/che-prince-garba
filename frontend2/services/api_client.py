import requests
import streamlit as st
from typing import Optional, Dict, Any, List
import json
from datetime import datetime
import pandas as pd

from config.constants import API_ENDPOINTS, APP_CONFIG
from utils.cache import CacheManager

class APIClient:
    """Client pour interagir avec l'API backend"""
    
    def __init__(self):
        self.base_url = API_ENDPOINTS["products"].split("/api")[0] + "/api/v1"
        self.session = requests.Session()
        self.cache = CacheManager()
        self._setup_session()
    
    def _setup_session(self):
        """Configure la session HTTP"""
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": f"{APP_CONFIG['name']}/{APP_CONFIG['version']}"
        })
        
        # Ajouter le token d'authentification si disponible
        token = st.session_state.get('auth_token')
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def _handle_response(self, response: requests.Response):
        """Gère la réponse de l'API"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_detail = "Erreur inconnue"
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', str(e))
            except:
                error_detail = str(e)
            
            st.error(f"Erreur API: {error_detail}")
            raise Exception(f"Erreur API: {error_detail}")
        except json.JSONDecodeError:
            st.error("Réponse API invalide")
            raise Exception("Réponse API invalide")
    
    def _get_cache_key(self, endpoint: str, params: dict = None):
        """Génère une clé de cache"""
        key = endpoint
        if params:
            key += f":{json.dumps(params, sort_keys=True)}"
        return key
    
    # =========================
    # AUTHENTIFICATION
    # =========================
    
    def login(self, username: str, password: str):
        try:
            response = self.session.post(
                API_ENDPOINTS["login"],
                data={
                    "username": username,
                    "password": password
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )

            data = self._handle_response(response)

            if "access_token" in data:
                st.session_state.auth_token = data["access_token"]
                st.session_state.user_info = data.get("user", {})
                self._setup_session()

            return data

        except Exception as e:
            st.error(f"Échec de connexion: {str(e)}")
            return None

    # =========================
    # PRODUITS
    # =========================
    
    def get_products(self, **params) -> List[Dict[str, Any]]:
        """Récupère la liste des produits"""
        cache_key = self._get_cache_key("products", params)
        cached = self.cache.get(cache_key)
        
        if cached and not params.get('force_refresh'):
            return cached
        
        try:
            response = self.session.get(API_ENDPOINTS["products"], params=params)
            data = self._handle_response(response)
            self.cache.set(cache_key, data, ttl_seconds=300)
            return data
        except:
            return []
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un produit par son ID"""
        try:
            response = self.session.get(API_ENDPOINTS["product_detail"](product_id))
            return self._handle_response(response)
        except:
            return None
    
    def create_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée un nouveau produit"""
        try:
            response = self.session.post(
                API_ENDPOINTS["products"],
                json=product_data
            )
            data = self._handle_response(response)
            self.cache.clear()  # Invalider le cache
            return data
        except Exception as e:
            st.error(f"Erreur création produit: {str(e)}")
            return None
    
    def update_product(self, product_id: str, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un produit"""
        try:
            response = self.session.put(
                API_ENDPOINTS["product_detail"](product_id),
                json=product_data
            )
            data = self._handle_response(response)
            self.cache.clear()
            return data
        except Exception as e:
            st.error(f"Erreur mise à jour produit: {str(e)}")
            return None
    
    def delete_product(self, product_id: str) -> bool:
        """Supprime un produit"""
        try:
            response = self.session.delete(API_ENDPOINTS["product_detail"](product_id))
            response.raise_for_status()
            self.cache.clear()
            return True
        except Exception as e:
            st.error(f"Erreur suppression produit: {str(e)}")
            return False
    
    # =========================
    # VENTES
    # =========================
    
    def get_sales(self, **params) -> List[Dict[str, Any]]:
        """Récupère la liste des ventes"""
        try:
            response = self.session.get(API_ENDPOINTS["sales"], params=params)
            return self._handle_response(response)
        except:
            return []
    
    def get_sale(self, sale_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une vente par son ID"""
        try:
            response = self.session.get(f"{API_ENDPOINTS['sales']}/{sale_id}")
            return self._handle_response(response)
        except:
            return None
    
    def create_sale(self, sale_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée une nouvelle vente"""
        try:
            response = self.session.post(
                API_ENDPOINTS["create_sale"],
                json=sale_data
            )
            data = self._handle_response(response)
            
            # Mettre à jour les statistiques en cache
            self.cache.delete_pattern("dashboard*")
            self.cache.delete_pattern("stats*")
            
            return data
        except Exception as e:
            st.error(f"Erreur création vente: {str(e)}")
            return None
    
    # =========================
    # CLIENTS
    # =========================
    
    def get_clients(self, **params) -> List[Dict[str, Any]]:
        """Récupère la liste des clients"""
        try:
            response = self.session.get(API_ENDPOINTS["clients"], params=params)
            return self._handle_response(response)
        except:
            return []
    
    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un client par son ID"""
        try:
            response = self.session.get(API_ENDPOINTS["client_detail"](client_id))
            return self._handle_response(response)
        except:
            return None
    
    def create_client(self, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée un nouveau client"""
        try:
            response = self.session.post(
                API_ENDPOINTS["clients"],
                json=client_data
            )
            data = self._handle_response(response)
            self.cache.delete_pattern("clients*")
            return data
        except Exception as e:
            st.error(f"Erreur création client: {str(e)}")
            return None
    
    # =========================
    # DASHBOARD & STATISTIQUES
    # =========================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du dashboard"""
        cache_key = "dashboard_stats"
        cached = self.cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            response = self.session.get(API_ENDPOINTS["dashboard_stats"])
            data = self._handle_response(response)
            self.cache.set(cache_key, data, ttl_seconds=60)  # Cache 1 minute
            return data
        except:
            return {}
    
    def get_sales_trend(self, days: int = 30, group_by: str = "day") -> List[Dict[str, Any]]:
        """Récupère les tendances des ventes"""
        cache_key = f"sales_trend_{days}_{group_by}"
        cached = self.cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            response = self.session.get(
                API_ENDPOINTS["sales_trend"],
                params={"days": days, "group_by": group_by}
            )
            data = self._handle_response(response).get("data", [])
            self.cache.set(cache_key, data, ttl_seconds=300)
            return data
        except:
            return []
    
    def get_top_products(self, limit: int = 10, days: int = 30) -> List[Dict[str, Any]]:
        """Récupère les meilleurs produits"""
        cache_key = f"top_products_{limit}_{days}"
        cached = self.cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            response = self.session.get(
                API_ENDPOINTS["top_products"],
                params={"limit": limit, "days": days}
            )
            data = self._handle_response(response).get("products", [])
            self.cache.set(cache_key, data, ttl_seconds=300)
            return data
        except:
            return []
    
    # =========================
    # STOCK
    # =========================
    
    def get_stock_movements(self, **params) -> List[Dict[str, Any]]:
        """Récupère les mouvements de stock"""
        try:
            response = self.session.get(API_ENDPOINTS["stock_movements"], params=params)
            return self._handle_response(response)
        except:
            return []
    
    def get_stock_alerts(self) -> Dict[str, Any]:
        """Récupère les alertes de stock"""
        cache_key = "stock_alerts"
        cached = self.cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            response = self.session.get(API_ENDPOINTS["stock_alerts"])
            data = self._handle_response(response)
            self.cache.set(cache_key, data, ttl_seconds=300)
            return data
        except:
            return {"low_stock": [], "out_of_stock": []}
    
    # =========================
    # FOURNISSEURS
    # =========================
    
    def get_suppliers(self, **params) -> List[Dict[str, Any]]:
        """Récupère la liste des fournisseurs"""
        try:
            response = self.session.get(API_ENDPOINTS["suppliers"], params=params)
            return self._handle_response(response)
        except:
            return []
    
    # =========================
    # COMPTABILITÉ
    # =========================
    
    def get_expenses(self, **params) -> List[Dict[str, Any]]:
        """Récupère la liste des dépenses"""
        try:
            response = self.session.get(API_ENDPOINTS["expenses"], params=params)
            return self._handle_response(response)
        except:
            return []
    
    def get_profit_analysis(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Analyse de profitabilité"""
        cache_key = f"profit_analysis_{start_date}_{end_date}"
        cached = self.cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            response = self.session.get(
                API_ENDPOINTS["profit_analysis"],
                params={"start_date": start_date, "end_date": end_date}
            )
            data = self._handle_response(response)
            self.cache.set(cache_key, data, ttl_seconds=300)
            return data
        except:
            return {}
    
    # =========================
    # UTILITAIRES
    # =========================
    
    def health_check(self) -> bool:
        """Vérifie la santé de l'API"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def export_data(self, endpoint: str, format: str = "csv", **params) -> bytes:
        """Exporte des données dans différents formats"""
        try:
            response = self.session.get(endpoint, params=params)
            data = self._handle_response(response)
            
            if format == "csv":
                df = pd.DataFrame(data)
                return df.to_csv(index=False).encode('utf-8')
            elif format == "excel":
                df = pd.DataFrame(data)
                return df.to_excel(index=False)
            elif format == "json":
                return json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            return b""
        except Exception as e:
            st.error(f"Erreur export: {str(e)}")
            return b""