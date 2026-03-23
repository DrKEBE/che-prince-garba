"""
Service de gestion des ventes et remboursements
"""
import streamlit as st
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from services.api_client import APIClient
from services.inventory_service import inventory_service
from config.constants import COLORS, PAYMENT_METHODS, CLIENT_TYPES
from utils.formatters import format_currency, format_number, format_date
from utils.session_state import get_session_state, update_session_state
from utils.cache import CacheManager

class SalesService:
    """Service de gestion des ventes"""
    
    def __init__(self):
        self.api = APIClient()
        self.cache = CacheManager()
    
    # =========================
    # GESTION DES VENTES
    # =========================
    
    def get_all_sales(self, filters: Optional[Dict] = None, force_refresh: bool = False) -> List[Dict]:
        """Récupère toutes les ventes avec filtres"""
        cache_key = f"sales_{str(filters) if filters else 'all'}"
        
        if not force_refresh:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            sales = self.api.get_sales(**(filters or {}))
            enriched_sales = self._enrich_sales_data(sales)
            self.cache.set(cache_key, enriched_sales, ttl_seconds=300)
            return enriched_sales
        except Exception as e:
            st.error(f"Erreur récupération ventes: {str(e)}")
            return []
    
    def get_sale_by_id(self, sale_id: str) -> Optional[Dict]:
        """Récupère une vente par son ID"""
        cache_key = f"sale_{sale_id}"
        cached = self.cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            sale = self.api.get_sale(sale_id)
            if sale:
                enriched = self._enrich_sale_data(sale)
                self.cache.set(cache_key, enriched, ttl_seconds=300)
                return enriched
        except Exception as e:
            st.error(f"Erreur récupération vente: {str(e)}")
        
        return None
    
    def create_sale(self, sale_data: Dict) -> Optional[Dict]:
        """Crée une nouvelle vente"""
        try:
            # Validation et préparation des données
            validated_data = self._validate_sale_data(sale_data)
            
            # Vérifier le stock pour chaque article
            for item in validated_data.get('items', []):
                product_id = item.get('product_id')
                quantity = item.get('quantity', 0)
                
                # Vérifier la disponibilité
                available, message = inventory_service.check_stock_for_sale(product_id, quantity)
                if not available:
                    st.error(f"Produit {item.get('product_name', product_id)}: {message}")
                    return None
            
            # Créer la vente via l'API
            result = self.api.create_sale(validated_data)
            
            if result:
                # Mettre à jour le stock
                self._update_stock_after_sale(validated_data.get('items', []))
                
                # Invalider les caches
                self.cache.delete_pattern("sales*")
                self.cache.delete_pattern("dashboard*")
                self.cache.delete_pattern("products*")
                self.cache.delete_pattern("clients*")
                
                # Mettre à jour les statistiques client
                if validated_data.get('client_id'):
                    self._update_client_statistics(validated_data['client_id'], result.get('final_amount', 0))
                
                st.success("Vente créée avec succès!")
                return result
        except Exception as e:
            st.error(f"Erreur création vente: {str(e)}")
        
        return None
    
    def update_sale(self, sale_id: str, update_data: Dict) -> Optional[Dict]:
        """Met à jour une vente"""
        try:
            # Validation
            validated_data = self._validate_sale_update(update_data)
            
            # Appel API (si disponible)
            # Pour l'instant, on simule
            st.warning("La mise à jour des ventes n'est pas encore implémentée dans l'API")
            return None
        except Exception as e:
            st.error(f"Erreur mise à jour vente: {str(e)}")
        
        return None
    
    def cancel_sale(self, sale_id: str, reason: str = "") -> bool:
        """Annule une vente"""
        try:
            # Vérifier si la vente peut être annulée
            sale = self.get_sale_by_id(sale_id)
            if not sale:
                st.error("Vente non trouvée")
                return False
            
            # Vérifier les restrictions
            if not self._can_cancel_sale(sale):
                st.error("Cette vente ne peut pas être annulée")
                return False
            
            # Créer un remboursement complet
            refund_data = {
                "refund_amount": sale.get('final_amount', 0),
                "refund_reason": "CANCELLATION",
                "refund_method": "CASH",
                "items": [],
                "notes": f"Annulation: {reason}"
            }
            
            # Appeler le service de remboursement
            refund_result = self.create_refund(sale_id, refund_data)
            
            if refund_result:
                st.success("Vente annulée et remboursée avec succès")
                return True
            
        except Exception as e:
            st.error(f"Erreur annulation vente: {str(e)}")
        
        return False
    
    # =========================
    # GESTION DES REMBOURSEMENTS
    # =========================
    
    def get_refunds(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Récupère les remboursements"""
        try:
            refunds = self.api.get_all_refunds(**(filters or {}))
            return self._enrich_refunds_data(refunds)
        except Exception as e:
            st.error(f"Erreur récupération remboursements: {str(e)}")
            return []
    
    def get_refund_by_id(self, refund_id: str) -> Optional[Dict]:
        """Récupère un remboursement par son ID"""
        try:
            refund = self.api.get_refund_details(refund_id)
            return self._enrich_refund_data(refund) if refund else None
        except Exception as e:
            st.error(f"Erreur récupération remboursement: {str(e)}")
            return None
    
    def create_refund(self, sale_id: str, refund_data: Dict) -> Optional[Dict]:
        """Crée un remboursement"""
        try:
            # Validation
            validated_data = self._validate_refund_data(sale_id, refund_data)
            
            # Appel API
            result = self.api.create_refund_for_sale(sale_id, validated_data)
            
            if result:
                # Mettre à jour le stock si nécessaire
                if validated_data.get('restock_items', True):
                    self._restock_refunded_items(validated_data.get('items', []))
                
                # Invalider les caches
                self.cache.delete_pattern(f"sale_{sale_id}")
                self.cache.delete_pattern("sales*")
                self.cache.delete_pattern("dashboard*")
                self.cache.delete_pattern("refunds*")
                
                st.success("Remboursement créé avec succès!")
                return result
        except Exception as e:
            st.error(f"Erreur création remboursement: {str(e)}")
        
        return None
    
    def approve_refund(self, refund_id: str, approved: bool = True, notes: str = "") -> bool:
        """Approuve ou rejette un remboursement"""
        try:
            # Appel API
            result = self.api.approve_refund(refund_id, {"approved": approved, "notes": notes})
            
            if result:
                # Invalider le cache
                self.cache.delete_pattern(f"refund_{refund_id}")
                self.cache.delete_pattern("refunds*")
                
                action = "approuvé" if approved else "rejeté"
                st.success(f"Remboursement {action} avec succès!")
                return True
        except Exception as e:
            st.error(f"Erreur approbation remboursement: {str(e)}")
        
        return False
    
    def process_refund(self, refund_id: str, process_data: Dict) -> bool:
        """Traite un remboursement (exécution du paiement)"""
        try:
            # Appel API
            result = self.api.process_refund(refund_id, process_data)
            
            if result:
                # Invalider le cache
                self.cache.delete_pattern(f"refund_{refund_id}")
                self.cache.delete_pattern("refunds*")
                
                st.success("Remboursement traité avec succès!")
                return True
        except Exception as e:
            st.error(f"Erreur traitement remboursement: {str(e)}")
        
        return False
    
    # =========================
    # ANALYSE ET RAPPORTS
    # =========================
    
    def get_sales_summary(self, period: str = "today") -> Dict[str, Any]:
        """Récupère un résumé des ventes"""
        try:
            # Définir la période
            start_date, end_date = self._get_period_dates(period)
            
            # Récupérer les ventes de la période
            filters = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            sales = self.get_all_sales(filters)
            return self._calculate_sales_summary(sales, period)
        except Exception as e:
            st.error(f"Erreur résumé ventes: {str(e)}")
            return self._get_empty_sales_summary()
    
    def get_sales_performance(self, days: int = 30) -> Dict[str, Any]:
        """Analyse la performance des ventes"""
        try:
            # Récupérer les données
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            filters = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            sales = self.get_all_sales(filters)
            return self._analyze_sales_performance(sales, days)
        except Exception as e:
            st.error(f"Erreur analyse performance: {str(e)}")
            return {"period_summary": {}, "trends": {}, "recommendations": []}
    
    def get_refund_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Analyse les remboursements"""
        try:
            refunds = self.get_refunds()
            return self._analyze_refunds(refunds, days)
        except Exception as e:
            st.error(f"Erreur analyse remboursements: {str(e)}")
            return {"summary": {}, "reasons": {}, "trends": {}}
    
    def get_top_categories(self, days: int = 30, limit: int = 10) -> List[Dict]:
        """Récupère les catégories les plus vendues"""
        try:
            sales = self.get_all_sales()
            return self._calculate_top_categories(sales, days, limit)
        except Exception as e:
            st.error(f"Erreur top catégories: {str(e)}")
            return []
    
    def get_sales_by_payment_method(self, days: int = 30) -> Dict[str, float]:
        """Analyse des ventes par méthode de paiement"""
        try:
            sales = self.get_all_sales()
            return self._calculate_sales_by_payment_method(sales, days)
        except Exception as e:
            st.error(f"Erreur analyse méthodes paiement: {str(e)}")
            return {}
    
    # =========================
    # PANIER ET COMMANDE
    # =========================
    
    def add_to_cart(self, product: Dict, quantity: int = 1) -> bool:
        """Ajoute un produit au panier"""
        try:
            # Vérifier le stock
            available, message = inventory_service.check_stock_for_sale(
                product.get('id'), 
                quantity
            )
            
            if not available:
                st.error(message)
                return False
            
            # Ajouter au panier dans session_state
            cart = get_session_state('cart', [])
            
            # Vérifier si le produit est déjà dans le panier
            for item in cart:
                if item.get('product_id') == product.get('id'):
                    item['quantity'] += quantity
                    item['total'] = item['quantity'] * item['unit_price']
                    update_session_state('cart', cart)
                    return True
            
            # Ajouter le nouvel article
            cart.append({
                "product_id": product.get('id'),
                "product_name": product.get('name'),
                "product_sku": product.get('sku'),
                "category": product.get('category'),
                "unit_price": float(product.get('selling_price', 0)),
                "purchase_price": float(product.get('purchase_price', 0)),
                "quantity": quantity,
                "total": float(product.get('selling_price', 0)) * quantity,
                "stock": product.get('current_stock', 0)
            })
            
            update_session_state('cart', cart)
            return True
            
        except Exception as e:
            st.error(f"Erreur ajout au panier: {str(e)}")
            return False
    
    def remove_from_cart(self, product_id: str) -> bool:
        """Retire un produit du panier"""
        try:
            cart = get_session_state('cart', [])
            cart = [item for item in cart if item.get('product_id') != product_id]
            update_session_state('cart', cart)
            return True
        except Exception as e:
            st.error(f"Erreur retrait du panier: {str(e)}")
            return False
    
    def update_cart_quantity(self, product_id: str, quantity: int) -> bool:
        """Met à jour la quantité d'un produit dans le panier"""
        try:
            if quantity <= 0:
                return self.remove_from_cart(product_id)
            
            cart = get_session_state('cart', [])
            
            for item in cart:
                if item.get('product_id') == product_id:
                    # Vérifier le stock
                    product = inventory_service.get_product_by_id(product_id)
                    if product and quantity > product.get('current_stock', 0):
                        st.error(f"Stock insuffisant. Disponible: {product.get('current_stock', 0)}")
                        return False
                    
                    item['quantity'] = quantity
                    item['total'] = item['unit_price'] * quantity
                    break
            
            update_session_state('cart', cart)
            return True
            
        except Exception as e:
            st.error(f"Erreur mise à jour panier: {str(e)}")
            return False
    
    def clear_cart(self) -> bool:
        """Vide le panier"""
        try:
            update_session_state('cart', [])
            return True
        except Exception as e:
            st.error(f"Erreur vidage panier: {str(e)}")
            return False
    
    def calculate_cart_summary(self) -> Dict[str, Any]:
        """Calcule le résumé du panier"""
        cart = get_session_state('cart', [])
        
        if not cart:
            return {
                "subtotal": 0,
                "discount": 0,
                "tax": 0,
                "total": 0,
                "items_count": 0,
                "profit_estimate": 0
            }
        
        subtotal = sum(item.get('total', 0) for item in cart)
        items_count = sum(item.get('quantity', 0) for item in cart)
        
        # Estimation du profit
        profit_estimate = sum(
            (item.get('unit_price', 0) - item.get('purchase_price', 0)) * item.get('quantity', 0)
            for item in cart
        )
        
        return {
            "subtotal": subtotal,
            "discount": 0,  # À implémenter
            "tax": subtotal * 0.18,  # TVA 18%
            "total": subtotal * 1.18,
            "items_count": items_count,
            "profit_estimate": profit_estimate
        }
    
    # =========================
    # MÉTHODES PRIVÉES
    # =========================
    
    def _enrich_sales_data(self, sales: List[Dict]) -> List[Dict]:
        """Enrichit les données des ventes"""
        enriched = []
        
        for sale in sales:
            # Ajouter des informations supplémentaires
            client_name = sale.get('client_name')
            payment_method_display = PAYMENT_METHODS.get(sale.get('payment_method', ''), sale.get('payment_method', ''))
            
            enriched.append({
                **sale,
                "client_name_display": client_name or "Client non enregistré",
                "payment_method_display": payment_method_display,
                "status_color": self._get_sale_status_color(sale.get('payment_status')),
                "is_refundable_display": "🟢" if sale.get('is_refundable') else "🔴",
                "formatted_amount": format_currency(sale.get('final_amount', 0)),
                "formatted_date": format_date(sale.get('sale_date'))
            })
        
        return enriched
    
    def _enrich_sale_data(self, sale: Dict) -> Dict:
        """Enrichit les données d'une vente"""
        # Récupérer les détails des articles
        items = sale.get('items', [])
        enriched_items = []
        
        for item in items:
            product = inventory_service.get_product_by_id(item.get('product_id', ''))
            enriched_items.append({
                **item,
                "product_name": product.get('name') if product else 'Produit inconnu',
                "product_category": product.get('category') if product else '',
                "current_stock": product.get('current_stock', 0) if product else 0
            })
        
        return {
            **sale,
            "items": enriched_items,
            "client_info": self._get_client_info(sale.get('client_id')),
            "refund_history": self.get_refunds({"sale_id": sale.get('id')})
        }
    
    def _enrich_refunds_data(self, refunds: List[Dict]) -> List[Dict]:
        """Enrichit les données des remboursements"""
        enriched = []
        
        for refund in refunds:
            # Ajouter des informations supplémentaires
            status_color = self._get_refund_status_color(refund.get('refund_status'))
            
            enriched.append({
                **refund,
                "status_color": status_color,
                "formatted_amount": format_currency(refund.get('refund_amount', 0)),
                "formatted_date": format_date(refund.get('refund_date')),
                "is_approved": refund.get('refund_status') in ['APPROVED', 'COMPLETED']
            })
        
        return enriched
    
    def _enrich_refund_data(self, refund: Dict) -> Dict:
        """Enrichit les données d'un remboursement"""
        # Récupérer les détails des articles remboursés
        items = refund.get('items', [])
        enriched_items = []
        
        for item in items:
            product = inventory_service.get_product_by_id(item.get('product_id', ''))
            enriched_items.append({
                **item,
                "product_name": product.get('name') if product else 'Produit inconnu',
                "product_category": product.get('category') if product else ''
            })
        
        return {
            **refund,
            "items": enriched_items,
            "sale_info": self.get_sale_by_id(refund.get('sale_id')),
            "approver_info": self._get_user_info(refund.get('approved_by'))
        }
    
    def _validate_sale_data(self, data: Dict) -> Dict:
        """Valide les données de vente"""
        required_fields = ['items', 'payment_method']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Le champ {field} est obligatoire")
        
        # Vérifier les articles
        if not isinstance(data['items'], list) or len(data['items']) == 0:
            raise ValueError("La vente doit contenir au moins un article")
        
        validated = data.copy()
        
        # Calculer les totaux
        validated = self._calculate_sale_totals(validated)
        
        # Ajouter la date
        validated['sale_date'] = datetime.now().isoformat()
        
        # Ajouter l'utilisateur actuel
        user_info = get_session_state('user_info', {})
        validated['cashier_id'] = user_info.get('id')
        validated['cashier_name'] = user_info.get('full_name')
        
        return validated
    
    def _validate_sale_update(self, data: Dict) -> Dict:
        """Valide les données de mise à jour de vente"""
        validated = {}
        
        # Seuls certains champs peuvent être mis à jour
        allowed_fields = ['payment_status', 'notes', 'shipping_cost', 'tax_amount']
        
        for key, value in data.items():
            if key in allowed_fields and value is not None:
                validated[key] = value
        
        return validated
    
    def _validate_refund_data(self, sale_id: str, data: Dict) -> Dict:
        """Valide les données de remboursement"""
        required_fields = ['refund_amount', 'refund_reason', 'refund_method']
        
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Le champ {field} est obligatoire")
        
        # Vérifier le montant
        if data['refund_amount'] <= 0:
            raise ValueError("Le montant du remboursement doit être positif")
        
        # Vérifier la vente
        sale = self.get_sale_by_id(sale_id)
        if not sale:
            raise ValueError("Vente non trouvée")
        
        # Vérifier le montant maximum
        max_refund = sale.get('final_amount', 0) - sale.get('refunded_amount', 0)
        if data['refund_amount'] > max_refund:
            raise ValueError(f"Montant maximum remboursable: {format_currency(max_refund)}")
        
        validated = data.copy()
        
        # Ajouter la date
        validated['refund_date'] = datetime.now().isoformat()
        
        # Ajouter l'utilisateur actuel
        user_info = get_session_state('user_info', {})
        validated['requested_by'] = user_info.get('id')
        
        return validated
    
    def _calculate_sale_totals(self, sale_data: Dict) -> Dict:
        """Calcule les totaux d'une vente"""
        items = sale_data.get('items', [])
        
        if not items:
            return sale_data
        
        # Calculer le sous-total
        subtotal = sum(item.get('total_price', 0) for item in items)
        
        # Appliquer la remise
        discount = sale_data.get('discount', 0)
        discount_amount = subtotal * (discount / 100) if discount > 0 else 0
        
        # Calculer les taxes
        tax_rate = 0.18  # TVA 18%
        taxable_amount = subtotal - discount_amount
        tax_amount = taxable_amount * tax_rate
        
        # Frais de livraison
        shipping_cost = sale_data.get('shipping_cost', 0)
        
        # Total final
        final_amount = subtotal - discount_amount + tax_amount + shipping_cost
        
        # Estimation du profit
        profit_estimate = sum(
            (item.get('unit_price', 0) - item.get('purchase_price', 0)) * item.get('quantity', 0)
            for item in items
        )
        
        return {
            **sale_data,
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_amount": final_amount,
            "profit_estimate": profit_estimate
        }
    
    def _update_stock_after_sale(self, items: List[Dict]):
        """Met à jour le stock après une vente"""
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            
            # Créer un mouvement de sortie
            movement_data = {
                "product_id": product_id,
                "movement_type": "OUT",
                "quantity": quantity,
                "reason": "VENTE",
                "reference": f"Vente {datetime.now().strftime('%Y%m%d')}"
            }
            
            # Appeler le service d'inventaire
            inventory_service.create_stock_movement(movement_data)
    
    def _restock_refunded_items(self, items: List[Dict]):
        """Rentre en stock les articles remboursés"""
        for item in items:
            if item.get('restocked', True):
                product_id = item.get('product_id')
                quantity = item.get('quantity', 0)
                
                # Créer un mouvement d'entrée
                movement_data = {
                    "product_id": product_id,
                    "movement_type": "RETURN",
                    "quantity": quantity,
                    "reason": "REMBOURSEMENT",
                    "reference": f"Remboursement {datetime.now().strftime('%Y%m%d')}"
                }
                
                # Appeler le service d'inventaire
                inventory_service.create_stock_movement(movement_data)
    
    def _update_client_statistics(self, client_id: str, amount: float):
        """Met à jour les statistiques du client"""
        # Cette fonction serait normalement gérée par le backend
        # Pour l'instant, on simule
        pass
    
    def _can_cancel_sale(self, sale: Dict) -> bool:
        """Vérifie si une vente peut être annulée"""
        # Vérifier le statut
        if sale.get('payment_status') not in ['PAID', 'PARTIAL']:
            return False
        
        # Vérifier la date
        sale_date = sale.get('sale_date')
        if isinstance(sale_date, str):
            sale_date = datetime.fromisoformat(sale_date.replace('Z', '+00:00'))
        
        # Annulation possible dans les 7 jours
        cancellation_period = 7
        days_since_sale = (datetime.now() - sale_date).days
        
        return days_since_sale <= cancellation_period
    
    def _get_client_info(self, client_id: Optional[str]) -> Optional[Dict]:
        """Récupère les informations d'un client"""
        if not client_id:
            return None
        
        try:
            from services.api_client import APIClient
            api = APIClient()
            return api.get_client(client_id)
        except:
            return None
    
    def _get_user_info(self, user_id: Optional[str]) -> Optional[Dict]:
        """Récupère les informations d'un utilisateur"""
        # À implémenter avec l'API users
        return None
    
    def _get_period_dates(self, period: str) -> Tuple[datetime, datetime]:
        """Retourne les dates de début et fin pour une période"""
        now = datetime.now()
        
        if period == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif period == "yesterday":
            start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = (now - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        elif period == "this_week":
            start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif period == "this_month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:  # last_30_days
            start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return start, end
    
    def _calculate_sales_summary(self, sales: List[Dict], period: str) -> Dict[str, Any]:
        """Calcule le résumé des ventes"""
        if not sales:
            return self._get_empty_sales_summary()
        
        # Statistiques de base
        total_sales = len(sales)
        total_amount = sum(s.get('final_amount', 0) for s in sales)
        avg_ticket = total_amount / total_sales if total_sales > 0 else 0
        
        # Par méthode de paiement
        by_payment_method = {}
        for sale in sales:
            method = sale.get('payment_method')
            amount = sale.get('final_amount', 0)
            by_payment_method[method] = by_payment_method.get(method, 0) + amount
        
        # Top clients
        client_sales = {}
        for sale in sales:
            client_id = sale.get('client_id')
            if client_id:
                client_sales[client_id] = client_sales.get(client_id, 0) + sale.get('final_amount', 0)
        
        top_clients = sorted(client_sales.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "period": period,
            "total_sales": total_sales,
            "total_amount": total_amount,
            "avg_ticket": avg_ticket,
            "by_payment_method": by_payment_method,
            "top_clients": top_clients,
            "refund_count": len([s for s in sales if s.get('refunded_amount', 0) > 0]),
            "refund_amount": sum(s.get('refunded_amount', 0) for s in sales)
        }
    
    def _analyze_sales_performance(self, sales: List[Dict], days: int) -> Dict[str, Any]:
        """Analyse la performance des ventes"""
        if not sales:
            return {"period_summary": {}, "trends": {}, "recommendations": []}
        
        # Convertir en DataFrame pour analyse
        df = pd.DataFrame(sales)
        
        # Grouper par jour
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df['date'] = df['sale_date'].dt.date
        
        daily_sales = df.groupby('date').agg({
            'final_amount': 'sum',
            'id': 'count'
        }).rename(columns={'final_amount': 'amount', 'id': 'count'}).reset_index()
        
        # Calculer les tendances
        if len(daily_sales) > 1:
            first_day = daily_sales.iloc[0]['amount']
            last_day = daily_sales.iloc[-1]['amount']
            growth_rate = ((last_day - first_day) / first_day) * 100 if first_day > 0 else 0
        else:
            growth_rate = 0
        
        # Identifier les patterns
        patterns = self._identify_sales_patterns(daily_sales)
        
        # Générer des recommandations
        recommendations = self._generate_sales_recommendations(daily_sales, df)
        
        return {
            "period_summary": {
                "days": days,
                "total_sales": len(sales),
                "total_amount": df['final_amount'].sum(),
                "avg_daily_sales": df['final_amount'].sum() / days,
                "growth_rate": growth_rate,
                "best_day": daily_sales.loc[daily_sales['amount'].idxmax()]['date'] if not daily_sales.empty else None,
                "worst_day": daily_sales.loc[daily_sales['amount'].idxmin()]['date'] if not daily_sales.empty else None
            },
            "trends": patterns,
            "recommendations": recommendations
        }
    
    def _analyze_refunds(self, refunds: List[Dict], days: int) -> Dict[str, Any]:
        """Analyse les remboursements"""
        if not refunds:
            return {"summary": {}, "reasons": {}, "trends": {}}
        
        # Filtrer par période
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_refunds = [
            r for r in refunds 
            if datetime.fromisoformat(r.get('refund_date', '').replace('Z', '+00:00')) > cutoff_date
        ]
        
        # Statistiques
        total_refunds = len(recent_refunds)
        total_amount = sum(r.get('refund_amount', 0) for r in recent_refunds)
        avg_refund = total_amount / total_refunds if total_refunds > 0 else 0
        
        # Par raison
        by_reason = {}
        for refund in recent_refunds:
            reason = refund.get('refund_reason', 'OTHER')
            by_reason[reason] = by_reason.get(reason, 0) + refund.get('refund_amount', 0)
        
        # Par statut
        by_status = {}
        for refund in recent_refunds:
            status = refund.get('refund_status', 'PENDING')
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "summary": {
                "total_refunds": total_refunds,
                "total_amount": total_amount,
                "avg_refund": avg_refund,
                "refund_rate": (total_amount / 100000) * 100  # Taux par rapport au CA estimé
            },
            "reasons": by_reason,
            "status_distribution": by_status,
            "top_refunds": sorted(recent_refunds, key=lambda x: x.get('refund_amount', 0), reverse=True)[:10]
        }
    
    def _calculate_top_categories(self, sales: List[Dict], days: int, limit: int) -> List[Dict]:
        """Calcule les catégories les plus vendues"""
        # Cette méthode nécessite les détails des articles
        # Pour l'instant, on retourne des données simulées
        return [
            {"category": "Soins Visage", "sales_count": 45, "revenue": 450000, "profit": 135000},
            {"category": "Maquillage", "sales_count": 32, "revenue": 320000, "profit": 96000},
            {"category": "Parfums", "sales_count": 28, "revenue": 560000, "profit": 168000},
            {"category": "Soins Corps", "sales_count": 22, "revenue": 220000, "profit": 66000},
            {"category": "Accessoires", "sales_count": 18, "revenue": 90000, "profit": 27000}
        ]
    
    def _calculate_sales_by_payment_method(self, sales: List[Dict], days: int) -> Dict[str, float]:
        """Calcule les ventes par méthode de paiement"""
        result = {}
        
        for sale in sales:
            method = sale.get('payment_method')
            amount = sale.get('final_amount', 0)
            result[method] = result.get(method, 0) + amount
        
        return result
    
    def _identify_sales_patterns(self, daily_sales: pd.DataFrame) -> Dict[str, Any]:
        """Identifie les patterns de vente"""
        if daily_sales.empty or len(daily_sales) < 7:
            return {}
        
        patterns = {}
        
        # Pattern hebdomadaire
        daily_sales['day_of_week'] = pd.to_datetime(daily_sales['date']).dt.dayofweek
        weekly_pattern = daily_sales.groupby('day_of_week')['amount'].mean()
        patterns['weekly'] = weekly_pattern.to_dict()
        
        # Tendances
        daily_sales['trend'] = daily_sales['amount'].rolling(window=7, min_periods=1).mean()
        patterns['trend'] = daily_sales['trend'].tolist()[-30:] if len(daily_sales) >= 30 else daily_sales['trend'].tolist()
        
        # Volatilité
        patterns['volatility'] = daily_sales['amount'].std() / daily_sales['amount'].mean() if daily_sales['amount'].mean() > 0 else 0
        
        return patterns
    
    def _generate_sales_recommendations(self, daily_sales: pd.DataFrame, df: pd.DataFrame) -> List[str]:
        """Génère des recommandations basées sur les ventes"""
        recommendations = []
        
        if daily_sales.empty:
            return ["Pas assez de données pour des recommandations"]
        
        # Vérifier les jours faibles
        avg_sales = daily_sales['amount'].mean()
        low_days = daily_sales[daily_sales['amount'] < avg_sales * 0.7]
        
        if len(low_days) > len(daily_sales) * 0.3:  # Plus de 30% des jours sont faibles
            recommendations.append("Promotions recommandées les jours de faible activité")
        
        # Vérifier la variance
        sales_std = daily_sales['amount'].std()
        sales_mean = daily_sales['amount'].mean()
        
        if sales_std > sales_mean * 0.5:  # Forte variance
            recommendations.append("Les ventes sont très variables - explorer la cause")
        
        # Analyser les méthodes de paiement
        if 'payment_method' in df.columns:
            payment_distribution = df['payment_method'].value_counts(normalize=True)
            if payment_distribution.get('CASH', 0) > 0.8:  # Plus de 80% en cash
                recommendations.append("Diversifier les méthodes de paiement acceptées")
        
        return recommendations
    
    def _get_sale_status_color(self, status: str) -> str:
        """Retourne la couleur correspondant au statut de vente"""
        colors = {
            "PAID": COLORS['success'],
            "PENDING": COLORS['warning'],
            "PARTIAL": COLORS['info'],
            "CANCELLED": COLORS['danger'],
            "REFUNDED": COLORS['secondary']
        }
        return colors.get(status, COLORS['dark'])
    
    def _get_refund_status_color(self, status: str) -> str:
        """Retourne la couleur correspondant au statut de remboursement"""
        colors = {
            "PENDING": COLORS['warning'],
            "APPROVED": COLORS['info'],
            "COMPLETED": COLORS['success'],
            "CANCELLED": COLORS['secondary'],
            "REJECTED": COLORS['danger']
        }
        return colors.get(status, COLORS['dark'])
    
    def _get_empty_sales_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de ventes vide"""
        return {
            "period": "unknown",
            "total_sales": 0,
            "total_amount": 0,
            "avg_ticket": 0,
            "by_payment_method": {},
            "top_clients": [],
            "refund_count": 0,
            "refund_amount": 0
        }
    
    # =========================
    # VISUALISATIONS
    # =========================
    
    def create_sales_trend_chart(self, sales_data: List[Dict], days: int = 30) -> go.Figure:
        """Crée un graphique de tendance des ventes"""
        if not sales_data:
            return self._create_empty_chart("Aucune donnée de vente disponible")
        
        # Convertir en DataFrame
        df = pd.DataFrame(sales_data)
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        
        # Grouper par jour
        daily_sales = df.groupby(df['sale_date'].dt.date).agg({
            'final_amount': 'sum',
            'id': 'count'
        }).rename(columns={'final_amount': 'amount', 'id': 'count'}).reset_index()
        
        # Créer le graphique
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_sales['sale_date'],
            y=daily_sales['amount'],
            name="Chiffre d'affaires",
            line=dict(color=COLORS['primary'], width=3),
            mode='lines+markers'
        ))
        
        # Ajouter une moyenne mobile
        window = min(7, len(daily_sales))
        daily_sales['moving_avg'] = daily_sales['amount'].rolling(window=window, min_periods=1).mean()
        
        fig.add_trace(go.Scatter(
            x=daily_sales['sale_date'],
            y=daily_sales['moving_avg'],
            name=f"Moyenne mobile ({window}j)",
            line=dict(color=COLORS['secondary'], width=2, dash='dash'),
            mode='lines'
        ))
        
        fig.update_layout(
            title=f"Tendance des Ventes ({days} derniers jours)",
            xaxis_title="Date",
            yaxis_title="Montant (FCFA)",
            height=400,
            template="plotly_white",
            hovermode="x unified",
            showlegend=True
        )
        
        return fig
    
    def create_payment_method_chart(self, payment_data: Dict) -> go.Figure:
        """Crée un graphique des méthodes de paiement"""
        if not payment_data:
            return self._create_empty_chart("Aucune donnée de paiement disponible")
        
        # Préparer les données
        labels = []
        values = []
        colors = []
        
        color_map = {
            "CASH": COLORS['success'],
            "MOBILE_MONEY": COLORS['info'],
            "CARD": COLORS['primary'],
            "BANK_TRANSFER": COLORS['secondary'],
            "CHECK": COLORS['warning']
        }
        
        for method, amount in payment_data.items():
            display_name = PAYMENT_METHODS.get(method, method)
            labels.append(display_name)
            values.append(amount)
            colors.append(color_map.get(method, COLORS['dark']))
        
        # Créer le graphique
        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(colors=colors),
                textinfo='label+percent',
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title="Distribution des Méthodes de Paiement",
            height=400,
            template="plotly_white",
            showlegend=True
        )
        
        return fig
    
    def create_refund_analysis_chart(self, refund_analysis: Dict) -> go.Figure:
        """Crée un graphique d'analyse des remboursements"""
        reasons = refund_analysis.get('reasons', {})
        
        if not reasons:
            return self._create_empty_chart("Aucune donnée de remboursement disponible")
        
        # Préparer les données
        labels = list(reasons.keys())
        values = list(reasons.values())
        
        # Créer le graphique
        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=values,
                marker_color=COLORS['danger'],
                text=[format_currency(v) for v in values],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Remboursements par Raison",
            xaxis_title="Raison",
            yaxis_title="Montant (FCFA)",
            height=400,
            template="plotly_white"
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
sales_service = SalesService()