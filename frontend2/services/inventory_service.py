"""
Service de gestion d'inventaire et de stocks
"""
import streamlit as st
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.api_client import APIClient
from config.constants import COLORS, STOCK_STATUS
from utils.formatters import format_currency, format_number
from utils.session_state import get_session_state, update_session_state
from utils.cache import CacheManager

class InventoryService:
    """Service de gestion d'inventaire"""
    
    def __init__(self):
        self.api = APIClient()
        self.cache = CacheManager()
    
    # =========================
    # GESTION DES PRODUITS
    # =========================
    
    def get_all_products(self, filters: Optional[Dict] = None, force_refresh: bool = False) -> List[Dict]:
        """Récupère tous les produits avec filtres"""
        cache_key = f"products_{str(filters) if filters else 'all'}"
        
        if not force_refresh:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            products = self.api.get_products(**(filters or {}))
            enriched_products = self._enrich_products_data(products)
            self.cache.set(cache_key, enriched_products, ttl_seconds=300)
            return enriched_products
        except Exception as e:
            st.error(f"Erreur récupération produits: {str(e)}")
            return []
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Récupère un produit par son ID"""
        cache_key = f"product_{product_id}"
        cached = self.cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            product = self.api.get_product(product_id)
            if product:
                enriched = self._enrich_product_data(product)
                self.cache.set(cache_key, enriched, ttl_seconds=300)
                return enriched
        except Exception as e:
            st.error(f"Erreur récupération produit: {str(e)}")
        
        return None
    
    def create_product(self, product_data: Dict) -> Optional[Dict]:
        """Crée un nouveau produit"""
        try:
            # Validation des données
            validated_data = self._validate_product_data(product_data)
            
            # Appel API
            result = self.api.create_product(validated_data)
            
            if result:
                # Invalider le cache
                self.cache.delete_pattern("products*")
                self.cache.delete_pattern("dashboard*")
                self.cache.delete_pattern("inventory*")
                
                st.success("Produit créé avec succès!")
                return result
        except Exception as e:
            st.error(f"Erreur création produit: {str(e)}")
        
        return None
    
    def update_product(self, product_id: str, update_data: Dict) -> Optional[Dict]:
        """Met à jour un produit"""
        try:
            # Validation des données
            validated_data = self._validate_product_update(update_data)
            
            # Appel API
            result = self.api.update_product(product_id, validated_data)
            
            if result:
                # Invalider le cache
                self.cache.delete_pattern(f"product_{product_id}")
                self.cache.delete_pattern("products*")
                self.cache.delete_pattern("dashboard*")
                
                st.success("Produit mis à jour avec succès!")
                return result
        except Exception as e:
            st.error(f"Erreur mise à jour produit: {str(e)}")
        
        return None
    
    def delete_product(self, product_id: str) -> bool:
        """Supprime un produit (désactive)"""
        try:
            # Dans notre système, on désactive plutôt que supprimer
            success = self.api.delete_product(product_id)
            
            if success:
                # Invalider le cache
                self.cache.delete_pattern(f"product_{product_id}")
                self.cache.delete_pattern("products*")
                self.cache.delete_pattern("dashboard*")
                
                st.success("Produit désactivé avec succès!")
                return True
        except Exception as e:
            st.error(f"Erreur suppression produit: {str(e)}")
        
        return False
    
    # =========================
    # GESTION DU STOCK
    # =========================
    
    def get_stock_movements(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Récupère les mouvements de stock"""
        try:
            movements = self.api.get_stock_movements(**(filters or {}))
            return self._enrich_movements_data(movements)
        except Exception as e:
            st.error(f"Erreur récupération mouvements: {str(e)}")
            return []
    
    def create_stock_movement(self, movement_data: Dict) -> Optional[Dict]:
        """Crée un mouvement de stock"""
        try:
            # Validation
            validated_data = self._validate_movement_data(movement_data)
            
            # Vérifier le stock disponible pour les sorties
            if validated_data.get('movement_type') == 'OUT':
                product_id = validated_data.get('product_id')
                quantity = validated_data.get('quantity', 0)
                
                if not self._check_stock_availability(product_id, quantity):
                    st.error("Stock insuffisant pour cette sortie")
                    return None
            
            # Dans l'API actuelle, on doit utiliser l'endpoint approprié
            # Pour l'instant, on simule
            st.success("Mouvement de stock créé (simulation)")
            
            # Invalider le cache
            self.cache.delete_pattern("stock*")
            self.cache.delete_pattern(f"product_{validated_data.get('product_id')}")
            
            return validated_data
        except Exception as e:
            st.error(f"Erreur création mouvement: {str(e)}")
            return None
    
    def get_stock_alerts(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Récupère les alertes de stock"""
        cache_key = "stock_alerts"
        
        if not force_refresh:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            alerts = self.api.get_stock_alerts()
            enriched_alerts = self._analyze_stock_alerts(alerts)
            self.cache.set(cache_key, enriched_alerts, ttl_seconds=300)
            return enriched_alerts
        except Exception as e:
            st.error(f"Erreur récupération alertes: {str(e)}")
            return {"low_stock": [], "out_of_stock": [], "critical": []}
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """Récupère un résumé de l'inventaire"""
        try:
            products = self.get_all_products()
            alerts = self.get_stock_alerts()
            
            return self._calculate_inventory_summary(products, alerts)
        except Exception as e:
            st.error(f"Erreur résumé inventaire: {str(e)}")
            return self._get_empty_inventory_summary()
    
    def get_low_stock_products(self, threshold_percentage: float = 0.3) -> List[Dict]:
        """Récupère les produits avec stock faible"""
        try:
            products = self.get_all_products()
            return self._filter_low_stock_products(products, threshold_percentage)
        except Exception as e:
            st.error(f"Erreur produits stock faible: {str(e)}")
            return []
    
    def get_expiring_products(self, days_threshold: int = 30) -> List[Dict]:
        """Récupère les produits qui expirent bientôt"""
        try:
            products = self.get_all_products()
            return self._filter_expiring_products(products, days_threshold)
        except Exception as e:
            st.error(f"Erreur produits expirants: {str(e)}")
            return []
    
    def calculate_product_stock(self, product_id: str) -> int:
        """Calcule le stock actuel d'un produit"""
        try:
            movements = self.get_stock_movements({"product_id": product_id})
            
            stock_in = sum(
                m['quantity'] for m in movements 
                if m['movement_type'] in ['IN', 'ADJUSTMENT', 'RETURN']
            )
            
            stock_out = sum(
                m['quantity'] for m in movements 
                if m['movement_type'] in ['OUT', 'DAMAGED']
            )
            
            return max(0, stock_in - stock_out)
        except Exception as e:
            st.error(f"Erreur calcul stock: {str(e)}")
            return 0
    
    def check_stock_for_sale(self, product_id: str, quantity: int) -> Tuple[bool, str]:
        """Vérifie si le stock est suffisant pour une vente"""
        try:
            current_stock = self.calculate_product_stock(product_id)
            
            if current_stock >= quantity:
                return True, f"Stock disponible: {current_stock} unités"
            else:
                return False, f"Stock insuffisant. Disponible: {current_stock}, Demande: {quantity}"
        except Exception as e:
            return False, f"Erreur vérification stock: {str(e)}"
    
    # =========================
    # ANALYSE ET RAPPORTS
    # =========================
    
    def get_inventory_turnover_report(self, days: int = 30) -> Dict[str, Any]:
        """Génère un rapport de rotation des stocks"""
        try:
            products = self.get_all_products()
            movements = self.get_stock_movements()
            
            return self._calculate_turnover_metrics(products, movements, days)
        except Exception as e:
            st.error(f"Erreur rapport rotation: {str(e)}")
            return {"turnover_rate": 0, "slow_movers": [], "fast_movers": []}
    
    def get_stock_value_report(self) -> Dict[str, Any]:
        """Calcule la valeur du stock"""
        try:
            products = self.get_all_products()
            return self._calculate_stock_value(products)
        except Exception as e:
            st.error(f"Erreur calcul valeur stock: {str(e)}")
            return {"total_value": 0, "by_category": {}, "by_brand": {}}
    
    def get_reorder_recommendations(self) -> List[Dict]:
        """Génère des recommandations de réapprovisionnement"""
        try:
            products = self.get_all_products()
            sales_data = self.api.get_top_products(limit=50, days=30)
            
            return self._generate_reorder_recommendations(products, sales_data)
        except Exception as e:
            st.error(f"Erreur recommandations réappro: {str(e)}")
            return []
    
    # =========================
    # MÉTHODES PRIVÉES
    # =========================
    
    def _enrich_products_data(self, products: List[Dict]) -> List[Dict]:
        """Enrichit les données des produits"""
        enriched = []
        
        for product in products:
            # Calculer le stock actuel
            current_stock = self.calculate_product_stock(product.get('id', ''))
            
            # Déterminer le statut
            alert_threshold = product.get('alert_threshold', 10)
            status = self._determine_stock_status(current_stock, alert_threshold)
            
            # Calculer la valeur
            stock_value = current_stock * product.get('purchase_price', 0)
            
            enriched.append({
                **product,
                "current_stock": current_stock,
                "stock_status": status,
                "stock_value": stock_value,
                "status_color": self._get_status_color(status),
                "days_of_supply": self._calculate_days_of_supply(product, current_stock)
            })
        
        return enriched
    
    def _enrich_product_data(self, product: Dict) -> Dict:
        """Enrichit les données d'un produit"""
        current_stock = self.calculate_product_stock(product.get('id', ''))
        alert_threshold = product.get('alert_threshold', 10)
        
        return {
            **product,
            "current_stock": current_stock,
            "stock_status": self._determine_stock_status(current_stock, alert_threshold),
            "stock_value": current_stock * product.get('purchase_price', 0),
            "movement_history": self.get_stock_movements({"product_id": product.get('id')})
        }
    
    def _enrich_movements_data(self, movements: List[Dict]) -> List[Dict]:
        """Enrichit les données des mouvements"""
        enriched = []
        
        for movement in movements:
            # Ajouter des informations supplémentaires
            product = self.get_product_by_id(movement.get('product_id', ''))
            
            enriched.append({
                **movement,
                "product_name": product.get('name', '') if product else 'Produit inconnu',
                "product_category": product.get('category', '') if product else '',
                "total_value": movement.get('quantity', 0) * movement.get('unit_cost', 0)
            })
        
        return enriched
    
    def _validate_product_data(self, data: Dict) -> Dict:
        """Valide les données du produit"""
        required_fields = ['name', 'category', 'purchase_price', 'selling_price']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Le champ {field} est obligatoire")
        
        # Vérifier que le prix de vente est supérieur au prix d'achat
        if data['selling_price'] <= data['purchase_price']:
            raise ValueError("Le prix de vente doit être supérieur au prix d'achat")
        
        # Formatage des données
        validated = data.copy()
        
        # Convertir les prix en Decimal/float
        if 'purchase_price' in validated:
            validated['purchase_price'] = float(validated['purchase_price'])
        
        if 'selling_price' in validated:
            validated['selling_price'] = float(validated['selling_price'])
        
        # Valeurs par défaut
        validated.setdefault('alert_threshold', 10)
        validated.setdefault('is_active', True)
        
        return validated
    
    def _validate_product_update(self, data: Dict) -> Dict:
        """Valide les données de mise à jour"""
        validated = {}
        
        # Ne copier que les champs fournis
        for key, value in data.items():
            if value is not None:
                if key in ['purchase_price', 'selling_price']:
                    validated[key] = float(value)
                else:
                    validated[key] = value
        
        return validated
    
    def _validate_movement_data(self, data: Dict) -> Dict:
        """Valide les données de mouvement"""
        required_fields = ['product_id', 'movement_type', 'quantity']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Le champ {field} est obligatoire")
        
        if data['quantity'] <= 0:
            raise ValueError("La quantité doit être positive")
        
        valid_types = ['IN', 'OUT', 'ADJUSTMENT', 'RETURN', 'DAMAGED']
        if data['movement_type'] not in valid_types:
            raise ValueError(f"Type de mouvement invalide. Options: {', '.join(valid_types)}")
        
        return data
    
    def _check_stock_availability(self, product_id: str, quantity: int) -> bool:
        """Vérifie la disponibilité du stock"""
        current_stock = self.calculate_product_stock(product_id)
        return current_stock >= quantity
    
    def _analyze_stock_alerts(self, alerts: Dict) -> Dict[str, Any]:
        """Analyse les alertes de stock"""
        low_stock = alerts.get('low_stock', [])
        out_of_stock = alerts.get('out_of_stock', [])
        
        # Identifier les alertes critiques
        critical_alerts = []
        
        for product in low_stock:
            if isinstance(product, dict) and product.get('current_stock', 0) <= 2:
                critical_alerts.append(product)
        
        return {
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "critical": critical_alerts,
            "total_alerts": len(low_stock) + len(out_of_stock),
            "priority_alerts": len(critical_alerts) + len(out_of_stock)
        }
    
    def _calculate_inventory_summary(self, products: List[Dict], alerts: Dict) -> Dict[str, Any]:
        """Calcule le résumé de l'inventaire"""
        if not products:
            return self._get_empty_inventory_summary()
        
        total_products = len(products)
        active_products = len([p for p in products if p.get('is_active', True)])
        
        # Calculer les stocks
        total_stock = sum(p.get('current_stock', 0) for p in products)
        total_value = sum(p.get('stock_value', 0) for p in products)
        
        # Statistiques de statut
        status_counts = {}
        for product in products:
            status = product.get('stock_status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_products": total_products,
            "active_products": active_products,
            "total_stock_units": total_stock,
            "total_stock_value": total_value,
            "avg_stock_value": total_value / total_products if total_products > 0 else 0,
            "status_distribution": status_counts,
            "alerts_summary": {
                "low_stock": len(alerts.get('low_stock', [])),
                "out_of_stock": len(alerts.get('out_of_stock', [])),
                "critical": len(alerts.get('critical', []))
            },
            "health_score": self._calculate_inventory_health_score(products, alerts)
        }
    
    def _filter_low_stock_products(self, products: List[Dict], threshold_percentage: float) -> List[Dict]:
        """Filtre les produits avec stock faible"""
        low_stock = []
        
        for product in products:
            current_stock = product.get('current_stock', 0)
            alert_threshold = product.get('alert_threshold', 10)
            
            if 0 < current_stock <= alert_threshold:
                # Calculer le pourcentage par rapport au seuil
                percentage = (current_stock / alert_threshold) * 100 if alert_threshold > 0 else 0
                
                low_stock.append({
                    **product,
                    "threshold_percentage": percentage,
                    "urgency": "HIGH" if percentage <= 30 else "MEDIUM" if percentage <= 60 else "LOW"
                })
        
        # Trier par urgence
        return sorted(low_stock, key=lambda x: x.get('threshold_percentage', 100))
    
    def _filter_expiring_products(self, products: List[Dict], days_threshold: int) -> List[Dict]:
        """Filtre les produits qui expirent bientôt"""
        expiring = []
        today = datetime.now()
        
        for product in products:
            exp_date = product.get('expiration_date')
            if exp_date:
                try:
                    exp_datetime = datetime.fromisoformat(exp_date.replace('Z', '+00:00'))
                    days_until_expiry = (exp_datetime - today).days
                    
                    if 0 <= days_until_expiry <= days_threshold:
                        expiring.append({
                            **product,
                            "days_until_expiry": days_until_expiry,
                            "urgency": "CRITICAL" if days_until_expiry <= 7 else "HIGH" if days_until_expiry <= 14 else "MEDIUM"
                        })
                except:
                    continue
        
        # Trier par date d'expiration
        return sorted(expiring, key=lambda x: x.get('days_until_expiry', 999))
    
    def _determine_stock_status(self, current_stock: int, alert_threshold: int) -> str:
        """Détermine le statut du stock"""
        if current_stock <= 0:
            return "RUPTURE"
        elif current_stock <= alert_threshold:
            return "ALERTE"
        elif current_stock <= alert_threshold * 2:
            return "NORMAL"
        else:
            return "EXCÉDENT"
    
    def _get_status_color(self, status: str) -> str:
        """Retourne la couleur correspondant au statut"""
        colors = {
            "RUPTURE": COLORS['danger'],
            "ALERTE": COLORS['warning'],
            "NORMAL": COLORS['success'],
            "EXCÉDENT": COLORS['info']
        }
        return colors.get(status, COLORS['secondary'])
    
    def _calculate_days_of_supply(self, product: Dict, current_stock: int) -> int:
        """Calcule les jours de stock"""
        # Estimation basée sur les ventes récentes
        # À implémenter avec les données réelles
        avg_daily_sales = product.get('avg_daily_sales', 1)
        return int(current_stock / avg_daily_sales) if avg_daily_sales > 0 else 0
    
    def _calculate_inventory_health_score(self, products: List[Dict], alerts: Dict) -> float:
        """Calcule un score de santé de l'inventaire"""
        if not products:
            return 0
        
        total_products = len(products)
        out_of_stock = len(alerts.get('out_of_stock', []))
        low_stock = len(alerts.get('low_stock', []))
        
        # Pénalités
        out_of_stock_penalty = (out_of_stock / total_products) * 50
        low_stock_penalty = (low_stock / total_products) * 25
        
        # Bonus pour les produits avec stock optimal
        optimal_stock = len([p for p in products if p.get('stock_status') == 'NORMAL'])
        optimal_bonus = (optimal_stock / total_products) * 10
        
        score = 100 - out_of_stock_penalty - low_stock_penalty + optimal_bonus
        
        return max(0, min(100, score))
    
    def _calculate_turnover_metrics(self, products: List[Dict], movements: List[Dict], days: int) -> Dict[str, Any]:
        """Calcule les métriques de rotation"""
        # Calculer les ventes récentes
        recent_movements = [
            m for m in movements 
            if m.get('movement_type') == 'OUT' 
            and datetime.fromisoformat(m.get('created_at', '').replace('Z', '+00:00')) > datetime.now() - timedelta(days=days)
        ]
        
        # Regrouper par produit
        product_sales = {}
        for movement in recent_movements:
            product_id = movement.get('product_id')
            quantity = movement.get('quantity', 0)
            product_sales[product_id] = product_sales.get(product_id, 0) + quantity
        
        # Analyser la rotation
        slow_movers = []
        fast_movers = []
        
        for product in products:
            product_id = product.get('id')
            current_stock = product.get('current_stock', 0)
            sales = product_sales.get(product_id, 0)
            
            if current_stock > 0:
                turnover = sales / current_stock if current_stock > 0 else 0
                
                if turnover < 0.5:  # Moins d'une demi-vente par unité en stock
                    slow_movers.append({
                        **product,
                        "turnover_rate": turnover,
                        "sales_last_period": sales
                    })
                elif turnover > 2:  # Plus de 2 ventes par unité en stock
                    fast_movers.append({
                        **product,
                        "turnover_rate": turnover,
                        "sales_last_period": sales
                    })
        
        # Taux de rotation global
        total_stock = sum(p.get('current_stock', 0) for p in products)
        total_sales = sum(product_sales.values())
        overall_turnover = total_sales / total_stock if total_stock > 0 else 0
        
        return {
            "turnover_rate": overall_turnover,
            "slow_movers": sorted(slow_movers, key=lambda x: x.get('turnover_rate', 0))[:10],
            "fast_movers": sorted(fast_movers, key=lambda x: -x.get('turnover_rate', 0))[:10],
            "analysis_period_days": days,
            "total_units_sold": total_sales,
            "average_stock": total_stock / len(products) if products else 0
        }
    
    def _calculate_stock_value(self, products: List[Dict]) -> Dict[str, Any]:
        """Calcule la valeur du stock"""
        if not products:
            return {"total_value": 0, "by_category": {}, "by_brand": {}}
        
        total_value = 0
        by_category = {}
        by_brand = {}
        
        for product in products:
            value = product.get('stock_value', 0)
            total_value += value
            
            # Par catégorie
            category = product.get('category', 'Non catégorisé')
            by_category[category] = by_category.get(category, 0) + value
            
            # Par marque
            brand = product.get('brand', 'Sans marque')
            by_brand[brand] = by_brand.get(brand, 0) + value
        
        return {
            "total_value": total_value,
            "by_category": by_category,
            "by_brand": by_brand,
            "avg_value_per_product": total_value / len(products),
            "most_valuable_category": max(by_category.items(), key=lambda x: x[1])[0] if by_category else None,
            "most_valuable_brand": max(by_brand.items(), key=lambda x: x[1])[0] if by_brand else None
        }
    
    def _generate_reorder_recommendations(self, products: List[Dict], sales_data: Dict) -> List[Dict]:
        """Génère des recommandations de réapprovisionnement"""
        recommendations = []
        
        for product in products:
            current_stock = product.get('current_stock', 0)
            alert_threshold = product.get('alert_threshold', 10)
            min_stock = product.get('min_stock', 5)
            
            # Vérifier si besoin de réapprovisionner
            if current_stock <= min_stock:
                # Calculer la quantité recommandée
                max_stock = product.get('max_stock', alert_threshold * 3)
                recommended_qty = max_stock - current_stock
                
                # Estimer le délai d'urgence
                avg_daily_sales = 1  # À remplacer par données réelles
                days_until_out = current_stock / avg_daily_sales if avg_daily_sales > 0 else 0
                
                recommendations.append({
                    "product_id": product.get('id'),
                    "product_name": product.get('name'),
                    "current_stock": current_stock,
                    "recommended_qty": recommended_qty,
                    "urgency": "CRITIQUE" if days_until_out <= 3 else "ÉLEVÉE" if days_until_out <= 7 else "NORMALE",
                    "estimated_cost": recommended_qty * product.get('purchase_price', 0),
                    "supplier": product.get('supplier', 'N/A')
                })
        
        # Trier par urgence
        urgency_order = {"CRITIQUE": 0, "ÉLEVÉE": 1, "NORMALE": 2}
        return sorted(recommendations, key=lambda x: urgency_order.get(x['urgency'], 3))
    
    def _get_empty_inventory_summary(self) -> Dict[str, Any]:
        """Retourne un résumé d'inventaire vide"""
        return {
            "total_products": 0,
            "active_products": 0,
            "total_stock_units": 0,
            "total_stock_value": 0,
            "avg_stock_value": 0,
            "status_distribution": {},
            "alerts_summary": {"low_stock": 0, "out_of_stock": 0, "critical": 0},
            "health_score": 0
        }
    
    # =========================
    # VISUALISATIONS
    # =========================
    
    def create_stock_status_chart(self, summary: Dict) -> go.Figure:
        """Crée un graphique du statut des stocks"""
        status_data = summary.get('status_distribution', {})
        
        if not status_data:
            return self._create_empty_chart("Aucune donnée de statut disponible")
        
        colors = {
            "RUPTURE": COLORS['danger'],
            "ALERTE": COLORS['warning'],
            "NORMAL": COLORS['success'],
            "EXCÉDENT": COLORS['info']
        }
        
        labels = list(status_data.keys())
        values = list(status_data.values())
        
        # Créer la figure
        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(colors=[colors.get(label, COLORS['secondary']) for label in labels])
            )
        ])
        
        fig.update_layout(
            title="Distribution du Statut des Stocks",
            height=400,
            template="plotly_white",
            showlegend=True
        )
        
        return fig
    
    def create_stock_value_chart(self, value_report: Dict) -> go.Figure:
        """Crée un graphique de la valeur du stock"""
        by_category = value_report.get('by_category', {})
        
        if not by_category:
            return self._create_empty_chart("Aucune donnée de valeur disponible")
        
        # Trier par valeur
        sorted_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:10]
        categories = [cat[0] for cat in sorted_categories]
        values = [cat[1] for cat in sorted_categories]
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=COLORS['primary'],
                text=[format_currency(v) for v in values],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Valeur du Stock par Catégorie (Top 10)",
            xaxis_title="Catégorie",
            yaxis_title="Valeur (FCFA)",
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    def create_stock_movement_timeline(self, movements: List[Dict], product_name: str = "") -> go.Figure:
        """Crée une timeline des mouvements de stock"""
        if not movements:
            return self._create_empty_chart("Aucun mouvement disponible")
        
        # Préparer les données
        df = pd.DataFrame(movements)
        
        # Convertir les dates
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Grouper par jour
        daily_movements = df.groupby([df['created_at'].dt.date, 'movement_type'])['quantity'].sum().reset_index()
        
        # Pivoter pour avoir IN et OUT séparés
        pivot_df = daily_movements.pivot(index='created_at', columns='movement_type', values='quantity').fillna(0)
        
        # Créer le graphique
        fig = go.Figure()
        
        # Ajouter les entrées
        if 'IN' in pivot_df.columns:
            fig.add_trace(go.Scatter(
                x=pivot_df.index,
                y=pivot_df['IN'],
                name="Entrées",
                line=dict(color=COLORS['success'], width=2),
                mode='lines+markers'
            ))
        
        # Ajouter les sorties
        if 'OUT' in pivot_df.columns:
            fig.add_trace(go.Scatter(
                x=pivot_df.index,
                y=pivot_df['OUT'],
                name="Sorties",
                line=dict(color=COLORS['danger'], width=2),
                mode='lines+markers'
            ))
        
        title = f"Timeline des Mouvements de Stock {product_name}".strip()
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Quantité",
            height=400,
            template="plotly_white",
            hovermode="x unified"
        )
        
        return fig
    
    def _create_empty_chart(self, message: str = "Aucune donnée disponible") -> go.Figure:
        """Crée un graphique vide avec un message"""
        fig = go.Figure()
        fig.update_layout(
            title=message,
            xaxis_title="",
            yaxis_title="",
            height=400,
            template="plotly_white",
            annotations=[{
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 14}
            }]
        )
        return fig


# Instance globale du service
inventory_service = InventoryService()