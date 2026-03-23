# backend/crud/product.py

from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta

from models import Product, StockMovement
from schemas import ProductCreate, ProductUpdate
from .base import CRUDBase
from core.exceptions import NotFoundException, BusinessLogicException

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def __init__(self):
        super().__init__(Product)

    def create_with_stock(self, db: Session, *, obj_in: ProductCreate) -> Product:
        """Crée un produit avec son stock initial"""
        try:
            # Exclure le stock initial des données du produit
            product_data = obj_in.dict(exclude={"initial_stock"})
            
            # Générer un code-barres unique si non fourni
            if product_data.get('barcode') in [None, "", "string"]:
                product_data['barcode'] = f"BARCODE_{uuid.uuid4().hex[:12].upper()}"
            
            # Générer un SKU unique si non fourni
            if product_data.get('sku') in [None, "", "string"]:
                name_part = product_data.get('name', 'PROD')[:3].upper()
                category_part = product_data.get('category', 'CAT')[:3].upper()
                product_data['sku'] = f"{name_part}-{category_part}-{uuid.uuid4().hex[:6].upper()}"
            
            # Créer le produit
            db_product = Product(**product_data)
            db.add(db_product)
            db.commit()
            db.refresh(db_product)
            
            # Créer le mouvement de stock initial si spécifié
            if hasattr(obj_in, 'initial_stock') and obj_in.initial_stock > 0:
                from decimal import Decimal
                purchase_price = db_product.purchase_price or 0
                unit_cost = Decimal(str(purchase_price))
                
                movement = StockMovement(
                    product_id=db_product.id,
                    movement_type="IN",
                    quantity=obj_in.initial_stock,
                    unit_cost=unit_cost,
                    total_cost=unit_cost * obj_in.initial_stock,
                    reason="STOCK_INITIAL",
                    movement_date=datetime.utcnow()
                )
                db.add(movement)
                db.commit()
            
            return db_product
            
        except Exception as e:
            db.rollback()
            raise BusinessLogicException(f"Erreur création produit: {str(e)}")

    def get_with_stock(self, db: Session, product_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un produit avec son stock actuel"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        
        stock = self.calculate_current_stock(db, product_id)
        
        result = {
            **product.__dict__,
            "current_stock": stock,
            "stock_status": self.get_stock_status(stock, product.alert_threshold)
        }
        
        return result

    def calculate_current_stock(self, db: Session, product_id: str) -> int:
        """
        Calcule le stock actuel d'un produit en sommant tous les mouvements.
        Types:
          - Entrée (augmentation) : IN, RETURN, ADJUSTMENT_POS (si séparé)
          - Sortie (diminution)   : OUT, DAMAGED, ADJUSTMENT_NEG (si séparé)
        Ici, ADJUSTMENT est traité comme une entrée (augmentation) pour rester cohérent.
        Si vous souhaitez gérer les ajustements négatifs, utilisez deux types distincts.
        """
        try:
            # Stock entrant (augmente le stock)
            stock_in = db.query(func.coalesce(func.sum(StockMovement.quantity), 0))\
                .filter(
                    StockMovement.product_id == product_id,
                    StockMovement.movement_type.in_(["IN", "RETURN", "ADJUSTMENT"])
                ).scalar()
            
            # Stock sortant (diminue le stock)
            stock_out = db.query(func.coalesce(func.sum(StockMovement.quantity), 0))\
                .filter(
                    StockMovement.product_id == product_id,
                    StockMovement.movement_type.in_(["OUT", "DAMAGED"])
                ).scalar()
            
            return int(stock_in - stock_out)
        except Exception as e:
            db.rollback()
            raise BusinessLogicException(f"Erreur calcul stock: {str(e)}")

    def get_stock_status(self, current_stock: int, alert_threshold: int) -> str:
        """Détermine le statut du stock"""
        if current_stock <= 0:
            return "RUPTURE"
        elif current_stock <= alert_threshold:
            return "ALERTE"
        elif current_stock <= alert_threshold * 2:
            return "NORMAL"
        else:
            return "BON"

    def search(
        self,
        db: Session,
        *,
        search: str = None,
        category: str = None,
        brand: str = None,
        min_price: float = None,
        max_price: float = None,
        low_stock: bool = False,
        out_of_stock: bool = False,
        include_inactive: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Recherche avancée de produits"""
        query = db.query(Product)
        
        if not include_inactive:
            query = query.filter(Product.is_active == True)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Product.barcode.ilike(search_term)
                )
            )
        
        if category:
            query = query.filter(Product.category == category)
        
        if brand:
            query = query.filter(Product.brand == brand)
        
        if min_price is not None:
            query = query.filter(Product.selling_price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.selling_price <= max_price)
        
        products = query.offset(skip).limit(limit).all()
        
        # Calculer le stock pour chaque produit
        result = []
        for product in products:
            stock = self.calculate_current_stock(db, product.id)
            status = self.get_stock_status(stock, product.alert_threshold)
            
            # Filtrer par statut de stock si demandé
            if low_stock and status != "ALERTE":
                continue
            if out_of_stock and status != "RUPTURE":
                continue
            
            result.append({
                **product.__dict__,
                "current_stock": stock,
                "stock_status": status
            })
        
        return result

    def update_stock(
        self,
        db: Session,
        *,
        product_id: int,
        quantity: int,
        movement_type: str,
        reason: str,
        unit_cost: float = None,
        reference: str = None,
        notes: str = None
    ) -> StockMovement:
        """Met à jour le stock d'un produit via un mouvement"""
        # Vérifier si le produit existe
        product = self.get(db, product_id)
        if not product:
            raise NotFoundException("Produit", product_id)
        
        # Vérifier le stock si c'est un mouvement sortant
        if movement_type == "OUT":
            current_stock = self.calculate_current_stock(db, product_id)
            if current_stock < quantity:
                raise BusinessLogicException(
                    f"Stock insuffisant. Disponible: {current_stock}, Demandé: {quantity}"
                )
        
        # Si pas de coût unitaire fourni et mouvement entrant, utiliser le prix d'achat
        if unit_cost is None and movement_type == "IN":
            unit_cost = product.purchase_price
        
        total_cost = unit_cost * quantity if unit_cost else None
        
        # Créer le mouvement de stock
        movement = StockMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity=quantity,
            unit_cost=unit_cost,
            total_cost=total_cost,
            reason=reason,
            reference=reference,
            notes=notes,
            movement_date=datetime.utcnow()
        )
        
        db.add(movement)
        db.commit()
        db.refresh(movement)
        
        return movement

    def get_low_stock_products(self, db: Session, threshold_percentage: float = 0.3) -> List[Dict[str, Any]]:
        """Récupère les produits avec stock faible"""
        try:
            products = db.query(Product).filter(Product.is_active == True).all()
            
            low_stock_products = []
            for product in products:
                current_stock = self.calculate_current_stock(db, product.id)
                # Utiliser le seuil d'alerte du produit, sinon 10 par défaut
                alert_threshold = getattr(product, 'alert_threshold', 10)
                
                # Calculer le pourcentage par rapport au seuil
                if alert_threshold > 0:
                    current_percentage = current_stock / alert_threshold
                    # Si le stock est > 0 mais inférieur ou égal au seuil * pourcentage
                    if 0 < current_stock <= (alert_threshold * threshold_percentage):
                        low_stock_products.append({
                            "product": product,
                            "current_stock": current_stock,
                            "threshold": alert_threshold,
                            "percentage": current_percentage * 100
                        })
            
            return low_stock_products
        except Exception as e:
            return []

    def get_expiring_products(self, db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """Récupère les produits qui expirent bientôt"""
        try:
            today = datetime.utcnow().date()
            expiry_date = today + timedelta(days=days)
            
            # Vérifier si le modèle Product a un champ expiration_date
            if not hasattr(Product, 'expiration_date'):
                return []
            
            products = db.query(Product)\
                .filter(
                    Product.expiration_date.isnot(None),
                    Product.expiration_date <= expiry_date,
                    Product.expiration_date >= today,
                    Product.is_active == True
                ).all()
            
            result = []
            for product in products:
                current_stock = self.calculate_current_stock(db, product.id)
                if current_stock > 0 and product.expiration_date:
                    days_until_expiry = (product.expiration_date - today).days
                    result.append({
                        "product": product,
                        "current_stock": current_stock,
                        "expiration_date": product.expiration_date,
                        "days_until_expiry": days_until_expiry
                    })
            
            return result
        except Exception as e:
            return []

    def get_stock_alerts(self, db: Session, threshold_percentage: float = 0.3) -> Dict[str, Any]:
        """Récupère toutes les alertes de stock"""
        try:
            # Produits en rupture
            out_of_stock = []
            # Produits avec stock faible
            low_stock = self.get_low_stock_products(db, threshold_percentage)
            # Produits expirant bientôt
            expiring_soon = self.get_expiring_products(db, days=30)
            
            # Récupérer tous les produits pour vérifier les ruptures
            products = db.query(Product).filter(Product.is_active == True).all()
            for product in products:
                current_stock = self.calculate_current_stock(db, product.id)
                if current_stock <= 0:
                    out_of_stock.append({
                        "product": product,
                        "current_stock": current_stock,
                        "threshold": getattr(product, 'alert_threshold', 10)
                    })
            
            return {
                "out_of_stock": out_of_stock,
                "low_stock": low_stock,
                "expiring_soon": expiring_soon
            }
        except Exception as e:
            return {
                "out_of_stock": [],
                "low_stock": [],
                "expiring_soon": []
            }

# Instance singleton du CRUD
product = CRUDProduct()
