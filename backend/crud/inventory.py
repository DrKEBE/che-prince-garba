# backend\crud\inventory.py
"""
CRUD unifié pour la gestion d'inventaire : produits, stock et fournisseurs
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
from decimal import Decimal

from models import Product, StockMovement, Supplier, PurchaseOrder, PurchaseOrderItem
from schemas import (
    ProductCreate, ProductUpdate, 
    SupplierCreate, SupplierUpdate,
    StockMovementCreate,
    PurchaseOrderCreate, PurchaseOrderUpdate,
    PurchaseOrderItemCreate
)
from .base import CRUDBase
from core.exceptions import NotFoundException, BusinessLogicException, ValidationException

logger = logging.getLogger(__name__)


class InventoryCRUD:
    """
    CRUD complet pour la gestion d'inventaire
    """
    
    # =========================
    # PRODUITS
    # =========================
    
    class ProductCRUD(CRUDBase[Product, ProductCreate, ProductUpdate]):
        def __init__(self):
            super().__init__(Product)
        
        def create_with_stock(self, db: Session, *, obj_in: ProductCreate, supplier_id: Optional[str] = None) -> Dict[str, Any]:
            """Crée un produit avec son stock initial"""
            try:
                from models import StockMovement
                
                # Exclure le stock initial des données du produit
                product_data = obj_in.dict(exclude={"initial_stock"})
                
                # Générer des codes uniques si non fournis
                if product_data.get('barcode') in [None, "", "string"]:
                    from uuid import uuid4
                    product_data['barcode'] = f"BAR_{uuid4().hex[:10].upper()}"
                
                if product_data.get('sku') in [None, "", "string"]:
                    name_part = product_data.get('name', 'PROD')[:3].upper()
                    category_part = product_data.get('category', 'CAT')[:3].upper()
                    from uuid import uuid4
                    product_data['sku'] = f"{name_part}-{category_part}-{uuid4().hex[:6].upper()}"
                
                # Calculer la marge
                purchase_price = Decimal(str(product_data.get('purchase_price', 0)))
                selling_price = Decimal(str(product_data.get('selling_price', 0)))
                if purchase_price > 0:
                    product_data['margin'] = ((selling_price - purchase_price) / purchase_price) * 100
                
                # Créer le produit
                db_product = Product(**product_data)
                db.add(db_product)
                db.commit()
                db.refresh(db_product)
                
                # Créer le mouvement de stock initial
                if hasattr(obj_in, 'initial_stock') and obj_in.initial_stock > 0:
                    movement = StockMovement(
                        product_id=db_product.id,
                        movement_type="IN",
                        quantity=obj_in.initial_stock,
                        unit_cost=purchase_price,
                        total_cost=purchase_price * obj_in.initial_stock,
                        reason="STOCK_INITIAL",
                        supplier_id=supplier_id,
                        movement_date=datetime.utcnow()
                    )
                    db.add(movement)
                    db.commit()
                
                return self.get_with_stock(db, db_product.id)
                
            except Exception as e:
                db.rollback()
                raise BusinessLogicException(f"Erreur création produit: {str(e)}")
        
        def get_with_stock(self, db: Session, product_id: str) -> Optional[Dict[str, Any]]:
            """Récupère un produit avec son stock actuel et statistiques"""
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return None
            
            # Calculer le stock actuel
            stock_in = db.query(func.coalesce(func.sum(StockMovement.quantity), 0))\
                .filter(
                    StockMovement.product_id == product_id,
                    StockMovement.movement_type.in_(["IN", "ADJUSTMENT", "RETURN"])
                ).scalar()
            
            stock_out = db.query(func.coalesce(func.sum(StockMovement.quantity), 0))\
                .filter(
                    StockMovement.product_id == product_id,
                    StockMovement.movement_type.in_(["OUT", "DAMAGED"])
                ).scalar()
            
            current_stock = int(stock_in - stock_out)
            
            # Statut du stock
            stock_status = self._get_stock_status(current_stock, product.alert_threshold)
            
            # Statistiques de vente
            from models import SaleItem
            sales_stats = db.query(
                func.sum(SaleItem.quantity).label("total_sold"),
                func.sum(SaleItem.total_price).label("total_revenue"),
                func.sum(SaleItem.profit).label("total_profit")
            ).filter(SaleItem.product_id == product_id).first()
            
            result = {
                **{c.name: getattr(product, c.name) for c in product.__table__.columns},
                "current_stock": current_stock,
                "stock_status": stock_status,
                "total_sold": int(sales_stats.total_sold or 0),
                "total_revenue": float(sales_stats.total_revenue or 0),
                "total_profit": float(sales_stats.total_profit or 0),
                "supplier_info": None
            }
            
            # Ajouter info fournisseur si récent
            if hasattr(product, 'supplier_id') and product.supplier_id:
                supplier = db.query(Supplier).filter(Supplier.id == product.supplier_id).first()
                if supplier:
                    result["supplier_info"] = {
                        "id": supplier.id,
                        "name": supplier.name,
                        "contact_person": supplier.contact_person,
                        "phone": supplier.phone
                    }
            
            return result
        
        def calculate_current_stock(self, db: Session, product_id: str) -> int:
            """Calcule le stock actuel d'un produit"""
            try:
                stock_in = db.query(func.coalesce(func.sum(StockMovement.quantity), 0))\
                    .filter(
                        StockMovement.product_id == product_id,
                        StockMovement.movement_type.in_(["IN", "ADJUSTMENT", "RETURN"])
                    ).scalar()
                
                stock_out = db.query(func.coalesce(func.sum(StockMovement.quantity), 0))\
                    .filter(
                        StockMovement.product_id == product_id,
                        StockMovement.movement_type.in_(["OUT", "DAMAGED"])
                    ).scalar()
                
                return int(stock_in - stock_out)
            except Exception as e:
                logger.error(f"Error calculating stock for product {product_id}: {e}")
                return 0
        
        def _get_stock_status(self, current_stock: int, alert_threshold: int) -> str:
            """Détermine le statut du stock"""
            if current_stock <= 0:
                return "RUPTURE"
            elif current_stock <= alert_threshold:
                return "ALERTE"
            elif current_stock <= alert_threshold * 2:
                return "NORMAL"
            else:
                return "EXCÉDENT"
        
        def search_products(
            self,
            db: Session,
            *,
            search: str = None,
            category: str = None,
            brand: str = None,
            supplier_id: str = None,
            min_price: float = None,
            max_price: float = None,
            low_stock: bool = False,
            out_of_stock: bool = False,
            include_inactive: bool = False,
            skip: int = 0,
            limit: int = 100
        ) -> List[Dict[str, Any]]:
            """Recherche avancée de produits avec stock"""
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
                        Product.barcode.ilike(search_term),
                        Product.brand.ilike(search_term)
                    )
                )
            
            if category:
                query = query.filter(Product.category == category)
            
            if brand:
                query = query.filter(Product.brand == brand)
            
            if supplier_id:
                # Filtrer par fournisseur via les mouvements de stock
                product_ids = db.query(StockMovement.product_id)\
                    .filter(StockMovement.supplier_id == supplier_id)\
                    .distinct().all()
                if product_ids:
                    query = query.filter(Product.id.in_([p[0] for p in product_ids]))
                else:
                    # Aucun produit pour ce fournisseur
                    return []
            
            if min_price is not None:
                query = query.filter(Product.selling_price >= min_price)
            
            if max_price is not None:
                query = query.filter(Product.selling_price <= max_price)
            
            products = query.offset(skip).limit(limit).all()
            
            # Calculer le stock pour chaque produit
            result = []
            for product in products:
                stock = self.calculate_current_stock(db, product.id)
                status = self._get_stock_status(stock, product.alert_threshold)
                
                # Filtrer par statut si demandé
                if low_stock and status != "ALERTE":
                    continue
                if out_of_stock and status != "RUPTURE":
                    continue
                
                result.append({
                    **{c.name: getattr(product, c.name) for c in product.__table__.columns},
                    "current_stock": stock,
                    "stock_status": status
                })
            
            return result
        
        def update_stock(
            self,
            db: Session,
            *,
            product_id: str,
            quantity: int,
            movement_type: str,
            reason: str,
            unit_cost: float = None,
            reference: str = None,
            supplier_id: str = None,
            notes: str = None
        ) -> StockMovement:
            """Met à jour le stock d'un produit via un mouvement"""
            from models import StockMovement
            
            # Vérifier si le produit existe
            product = db.query(Product).filter(Product.id == product_id).first()
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
                unit_cost = float(product.purchase_price or 0)
            
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
                supplier_id=supplier_id,
                notes=notes,
                movement_date=datetime.utcnow()
            )
            
            db.add(movement)
            db.commit()
            db.refresh(movement)
            
            return movement
        
        def get_stock_history(
            self,
            db: Session,
            product_id: str,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            limit: int = 100
        ) -> List[Dict[str, Any]]:
            """Historique des mouvements de stock pour un produit"""
            query = db.query(StockMovement).filter(StockMovement.product_id == product_id)
            
            if start_date:
                query = query.filter(StockMovement.movement_date >= start_date)
            if end_date:
                query = query.filter(StockMovement.movement_date <= end_date)
            
            movements = query.order_by(desc(StockMovement.movement_date)).limit(limit).all()
            
            result = []
            for movement in movements:
                result.append({
                    "id": movement.id,
                    "movement_type": movement.movement_type,
                    "quantity": movement.quantity,
                    "unit_cost": float(movement.unit_cost) if movement.unit_cost else None,
                    "total_cost": float(movement.total_cost) if movement.total_cost else None,
                    "reason": movement.reason,
                    "reference": movement.reference,
                    "supplier_id": movement.supplier_id,
                    "movement_date": movement.movement_date,
                    "created_at": movement.created_at
                })
            
            return result
    
    # =========================
    # FOURNISSEURS
    # =========================
    
    class SupplierCRUD(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
        def __init__(self):
            super().__init__(Supplier)
        
        def get_with_stats(self, db: Session, supplier_id: str) -> Optional[Dict[str, Any]]:
            """Récupère un fournisseur avec ses statistiques"""
            supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
            if not supplier:
                return None
            
            # Statistiques des mouvements de stock
            stock_stats = db.query(
                func.count(StockMovement.id).label("total_movements"),
                func.sum(StockMovement.quantity).label("total_quantity"),
                func.sum(StockMovement.total_cost).label("total_cost")
            ).filter(StockMovement.supplier_id == supplier_id).first()
            
            # Produits fournis
            product_count = db.query(func.count(Product.id))\
                .join(StockMovement, StockMovement.product_id == Product.id)\
                .filter(StockMovement.supplier_id == supplier_id)\
                .scalar() or 0
            
            # Commandes récentes
            recent_orders = db.query(PurchaseOrder)\
                .filter(PurchaseOrder.supplier_id == supplier_id)\
                .order_by(desc(PurchaseOrder.order_date))\
                .limit(5).all()
            
            result = {
                **{c.name: getattr(supplier, c.name) for c in supplier.__table__.columns},
                "stats": {
                    "total_movements": stock_stats.total_movements or 0,
                    "total_quantity": int(stock_stats.total_quantity or 0),
                    "total_cost": float(stock_stats.total_cost or 0),
                    "product_count": product_count,
                    "order_count": len(recent_orders)
                },
                "recent_orders": [
                    {
                        "id": order.id,
                        "order_number": order.order_number,
                        "order_date": order.order_date,
                        "status": order.status,
                        "total_amount": float(order.total_amount or 0)
                    }
                    for order in recent_orders
                ]
            }
            
            return result
        
        def get_supplier_products(
            self,
            db: Session,
            supplier_id: str,
            active_only: bool = True
        ) -> List[Dict[str, Any]]:
            """Récupère tous les produits fournis par un fournisseur"""
            # Produits ayant eu des mouvements de stock de ce fournisseur
            product_ids = db.query(StockMovement.product_id)\
                .filter(StockMovement.supplier_id == supplier_id)\
                .distinct().all()
            
            if not product_ids:
                return []
            
            product_ids = [p[0] for p in product_ids]
            
            query = db.query(Product).filter(Product.id.in_(product_ids))
            if active_only:
                query = query.filter(Product.is_active == True)
            
            products = query.all()
            
            # Pour chaque produit, calculer le stock total fourni par ce fournisseur
            result = []
            for product in products:
                total_supplied = db.query(func.sum(StockMovement.quantity))\
                    .filter(
                        StockMovement.product_id == product.id,
                        StockMovement.supplier_id == supplier_id,
                        StockMovement.movement_type.in_(["IN", "RETURN"])
                    ).scalar() or 0
                
                current_stock = self.product_crud.calculate_current_stock(db, product.id)
                
                result.append({
                    "id": product.id,
                    "name": product.name,
                    "sku": product.sku,
                    "category": product.category,
                    "selling_price": float(product.selling_price),
                    "current_stock": current_stock,
                    "total_supplied": int(total_supplied),
                    "last_supply": db.query(StockMovement.movement_date)\
                        .filter(
                            StockMovement.product_id == product.id,
                            StockMovement.supplier_id == supplier_id
                        )\
                        .order_by(desc(StockMovement.movement_date))\
                        .first()
                })
            
            return result
        
        def search_suppliers(
            self,
            db: Session,
            *,
            search: str = None,
            city: str = None,
            active_only: bool = True,
            skip: int = 0,
            limit: int = 100
        ) -> List[Dict[str, Any]]:
            """Recherche de fournisseurs"""
            query = db.query(Supplier)
            
            if active_only:
                query = query.filter(Supplier.is_active == True)
            
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Supplier.name.ilike(search_term),
                        Supplier.contact_person.ilike(search_term),
                        Supplier.phone.ilike(search_term),
                        Supplier.email.ilike(search_term)
                    )
                )
            
            if city:
                query = query.filter(Supplier.city == city)
            
            suppliers = query.offset(skip).limit(limit).all()
            
            result = []
            for supplier in suppliers:
                # Statistiques rapides
                product_count = db.query(func.count(StockMovement.product_id))\
                    .filter(StockMovement.supplier_id == supplier.id)\
                    .distinct().count()
                
                total_spent = db.query(func.sum(StockMovement.total_cost))\
                    .filter(StockMovement.supplier_id == supplier.id)\
                    .scalar() or 0
                
                result.append({
                    **{c.name: getattr(supplier, c.name) for c in supplier.__table__.columns},
                    "product_count": product_count,
                    "total_spent": float(total_spent),
                    "last_supply": db.query(StockMovement.movement_date)\
                        .filter(StockMovement.supplier_id == supplier.id)\
                        .order_by(desc(StockMovement.movement_date))\
                        .first()
                })
            
            return result
    
    # =========================
    # DASHBOARD INVENTAIRE
    # =========================
    
    def get_inventory_dashboard(self, db: Session) -> Dict[str, Any]:
        """Tableau de bord complet de l'inventaire"""
        # Statistiques produits
        total_products = db.query(Product).filter(Product.is_active == True).count()
        
        # Produits en rupture et faible stock
        products = db.query(Product).filter(Product.is_active == True).all()
        out_of_stock = 0
        low_stock = 0
        
        for product in products:
            stock = self.product_crud.calculate_current_stock(db, product.id)
            if stock <= 0:
                out_of_stock += 1
            elif stock <= product.alert_threshold:
                low_stock += 1
        
        # Statistiques fournisseurs
        total_suppliers = db.query(Supplier).filter(Supplier.is_active == True).count()
        
        # Statistiques de stock
        total_stock_value = db.query(
            func.sum(StockMovement.total_cost)
        ).filter(StockMovement.movement_type.in_(["IN", "ADJUSTMENT"]))\
         .scalar() or 0
        
        # Mouvements récents
        recent_movements = db.query(StockMovement)\
            .join(Product, Product.id == StockMovement.product_id)\
            .order_by(desc(StockMovement.movement_date))\
            .limit(10).all()
        
        # Fournisseurs principaux
        top_suppliers = db.query(
            Supplier.id,
            Supplier.name,
            func.count(StockMovement.id).label("movement_count"),
            func.sum(StockMovement.total_cost).label("total_cost")
        ).join(StockMovement, StockMovement.supplier_id == Supplier.id)\
         .group_by(Supplier.id, Supplier.name)\
         .order_by(desc(func.sum(StockMovement.total_cost)))\
         .limit(5).all()
        
        # Produits à réapprovisionner
        to_reorder = []
        for product in products:
            stock = self.product_crud.calculate_current_stock(db, product.id)
            if stock <= product.alert_threshold and stock > 0:
                to_reorder.append({
                    "id": product.id,
                    "name": product.name,
                    "current_stock": stock,
                    "alert_threshold": product.alert_threshold,
                    "category": product.category,
                    "supplier_id": product.supplier_id
                })
        
        return {
            "stats": {
                "total_products": total_products,
                "total_suppliers": total_suppliers,
                "out_of_stock": out_of_stock,
                "low_stock": low_stock,
                "total_stock_value": float(total_stock_value),
                "reorder_needed": len(to_reorder)
            },
            "recent_movements": [
                {
                    "id": m.id,
                    "product_name": m.product.name,
                    "movement_type": m.movement_type,
                    "quantity": m.quantity,
                    "reason": m.reason,
                    "movement_date": m.movement_date
                }
                for m in recent_movements
            ],
            "top_suppliers": [
                {
                    "id": s.id,
                    "name": s.name,
                    "movement_count": s.movement_count,
                    "total_cost": float(s.total_cost or 0)
                }
                for s in top_suppliers
            ],
            "to_reorder": to_reorder[:10]  # Limiter à 10
        }
    
    # =========================
    # COMMANDES FOURNISSEURS
    # =========================
    
    def create_purchase_order(
        self,
        db: Session,
        *,
        order_in: PurchaseOrderCreate,
        user_id: str
    ) -> PurchaseOrder:
        """Crée une commande fournisseur"""
        from uuid import uuid4
        
        # Générer un numéro de commande
        order_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}"
        
        # Calculer le montant total
        total_amount = sum(item.quantity * item.unit_price for item in order_in.items)
        
        # Créer la commande
        order_data = order_in.dict(exclude={"items"})
        order_data.update({
            "order_number": order_number,
            "total_amount": total_amount,
            "order_date": datetime.utcnow(),
            "created_by": user_id
        })
        
        db_order = PurchaseOrder(**order_data)
        db.add(db_order)
        db.flush()
        
        # Créer les lignes de commande
        for item in order_in.items:
            order_item = PurchaseOrderItem(
                purchase_order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            db.add(order_item)
        
        db.commit()
        db.refresh(db_order)
        
        return db_order
    
    def receive_purchase_order(
        self,
        db: Session,
        *,
        order_id: str,
        items: List[Dict[str, Any]],
        user_id: str
    ) -> PurchaseOrder:
        """Réceptionne une commande fournisseur"""
        order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
        if not order:
            raise NotFoundException("Commande", order_id)
        
        if order.status == "RECEIVED":
            raise BusinessLogicException("La commande a déjà été réceptionnée")
        
        # Mettre à jour les quantités reçues
        for item_data in items:
            order_item = db.query(PurchaseOrderItem).filter(
                PurchaseOrderItem.id == item_data["id"],
                PurchaseOrderItem.purchase_order_id == order_id
            ).first()
            
            if order_item:
                received_qty = item_data.get("received_quantity", order_item.quantity)
                order_item.received_quantity = received_qty
                order_item.status = "RECEIVED"
                
                # Créer un mouvement de stock
                if received_qty > 0:
                    movement = StockMovement(
                        product_id=order_item.product_id,
                        movement_type="IN",
                        quantity=received_qty,
                        unit_cost=order_item.unit_price,
                        total_cost=order_item.unit_price * received_qty,
                        reason="RECEPTION_COMMANDE",
                        reference=order.order_number,
                        supplier_id=order.supplier_id,
                        movement_date=datetime.utcnow()
                    )
                    db.add(movement)
        
        # Mettre à jour le statut de la commande
        order.status = "RECEIVED"
        order.updated_at = datetime.utcnow()
        order.received_by = user_id
        
        db.commit()
        db.refresh(order)
        
        return order
    
def get_purchase_orders(
    self,
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    supplier_id: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Récupère la liste des commandes fournisseurs avec pagination et filtres.
    Retourne un dictionnaire contenant les commandes et le total.
    """
    query = db.query(PurchaseOrder)
    
    if supplier_id:
        query = query.filter(PurchaseOrder.supplier_id == supplier_id)
    if status:
        query = query.filter(PurchaseOrder.status == status)
    if start_date:
        query = query.filter(PurchaseOrder.order_date >= start_date)
    if end_date:
        query = query.filter(PurchaseOrder.order_date <= end_date)
    
    total = query.count()
    orders = query.order_by(PurchaseOrder.order_date.desc()).offset(skip).limit(limit).all()
    
    # Enrichir avec les noms des fournisseurs et des produits
    result = []
    for order in orders:
        supplier = db.query(Supplier).filter(Supplier.id == order.supplier_id).first()
        items = []
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            items.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": product.name if product else "Inconnu",
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "received_quantity": item.received_quantity,
                "status": item.status,
                "subtotal": float(item.quantity * item.unit_price)
            })
        
        result.append({
            "id": order.id,
            "supplier_id": order.supplier_id,
            "supplier_name": supplier.name if supplier else "Inconnu",
            "order_number": order.order_number,
            "order_date": order.order_date,
            "expected_delivery": order.expected_delivery,
            "status": order.status,
            "total_amount": float(order.total_amount or 0),
            "notes": order.notes,
            "items": items,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        })
    
    return {
        "data": result,
        "total": total,
        "skip": skip,
        "limit": limit
    }


def get_purchase_order(
    self,
    db: Session,
    order_id: str
) -> Optional[Dict[str, Any]]:
    """Récupère une commande fournisseur avec ses détails."""
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        return None
    
    supplier = db.query(Supplier).filter(Supplier.id == order.supplier_id).first()
    items = []
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": product.name if product else "Inconnu",
            "quantity": item.quantity,
            "unit_price": float(item.unit_price),
            "received_quantity": item.received_quantity,
            "status": item.status,
            "subtotal": float(item.quantity * item.unit_price)
        })
    
    return {
        "id": order.id,
        "supplier_id": order.supplier_id,
        "supplier_name": supplier.name if supplier else "Inconnu",
        "order_number": order.order_number,
        "order_date": order.order_date,
        "expected_delivery": order.expected_delivery,
        "status": order.status,
        "total_amount": float(order.total_amount or 0),
        "notes": order.notes,
        "items": items,
        "created_at": order.created_at,
        "updated_at": order.updated_at
    }


def delete_purchase_order(
    self,
    db: Session,
    order_id: str
) -> bool:
    """Supprime définitivement une commande fournisseur (seulement si en attente ou annulée)."""
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        return False
    
    if order.status not in ["PENDING", "CANCELLED"]:
        raise BusinessLogicException(
            f"Impossible de supprimer une commande avec statut '{order.status}'"
        )
    
    db.delete(order)
    db.commit()
    return True

# Initialiser les instances
inventory = InventoryCRUD()
inventory.product = InventoryCRUD.ProductCRUD()
inventory.supplier = InventoryCRUD.SupplierCRUD()