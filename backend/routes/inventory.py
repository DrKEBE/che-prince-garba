# backend\routes\inventory.py
"""
Routes API pour le module Inventaire unifié (Produits + Stock + Fournisseurs)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from core.exceptions import NotFoundException, BusinessLogicException, ValidationException

from database import get_db
from models import Product, Supplier, StockMovement, PurchaseOrder
from schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    SupplierCreate, SupplierUpdate, SupplierResponse,
    StockMovementCreate, StockMovementResponse,
    PurchaseOrderCreate, PurchaseOrderResponse
)
from crud.inventory import inventory
from middleware.auth import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventaire"])
logger = logging.getLogger(__name__)


# =========================
# DASHBOARD INVENTAIRE
# =========================

@router.get("/dashboard")
def get_inventory_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Tableau de bord complet de l'inventaire"""
    try:
        dashboard_data = inventory.get_inventory_dashboard(db)
        return dashboard_data
    except Exception as e:
        logger.error(f"Erreur dashboard inventaire: {str(e)}")
        raise HTTPException(500, f"Erreur lors de la récupération du dashboard: {str(e)}")


# =========================
# PRODUITS
# =========================

@router.post("/products", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    supplier_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Crée un nouveau produit"""
    try:
        product_data = inventory.product.create_with_stock(
            db=db, 
            obj_in=product, 
            supplier_id=supplier_id
        )
        return product_data
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/products", response_model=List[ProductResponse])
def get_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    supplier_id: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    low_stock: bool = Query(False),
    out_of_stock: bool = Query(False),
    include_inactive: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère la liste des produits avec filtres"""
    try:
        products = inventory.product.search_products(
            db=db,
            search=search,
            category=category,
            brand=brand,
            supplier_id=supplier_id,
            min_price=min_price,
            max_price=max_price,
            low_stock=low_stock,
            out_of_stock=out_of_stock,
            include_inactive=include_inactive,
            skip=skip,
            limit=limit
        )
        return products
    except Exception as e:
        logger.error(f"Erreur recherche produits: {str(e)}")
        raise HTTPException(500, f"Erreur lors de la recherche: {str(e)}")


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str = Path(..., description="ID du produit"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère un produit spécifique avec son stock"""
    product_data = inventory.product.get_with_stock(db, product_id)
    if not product_data:
        raise HTTPException(404, "Produit non trouvé")
    return product_data


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Met à jour un produit"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(404, "Produit non trouvé")
        
        update_data = product_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        # Recalculer la marge si les prix changent
        if 'purchase_price' in update_data or 'selling_price' in update_data:
            if product.purchase_price and product.selling_price and product.purchase_price > 0:
                product.margin = ((product.selling_price - product.purchase_price) / product.purchase_price) * 100
        
        db.commit()
        db.refresh(product)
        
        return inventory.product.get_with_stock(db, product.id)
    except Exception as e:
        db.rollback()
        raise HTTPException(400, str(e))

import os
import uuid
from fastapi import UploadFile, File
from core.config import settings

UPLOAD_DIR = os.path.join(settings.UPLOAD_DIR, "products")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/products/{product_id}/image")
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Ajoute une image à un produit.
    - Format accepté : JPEG, PNG, GIF, WebP
    - Taille max : 5 Mo
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    # Vérifications
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    MAX_SIZE = 5 * 1024 * 1024  # 5 Mo

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Format non supporté. Utilisez JPEG, PNG, GIF ou WebP.")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(400, "L'image ne doit pas dépasser 5 Mo.")

    # Générer un nom unique
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Sauvegarder le fichier
    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    # Ajouter le nom du fichier dans la liste JSON du produit
    if not product.images:
        product.images = []
    product.images.append(filename)
    db.commit()

    return {"filename": filename, "url": f"/uploads/products/{filename}"}

@router.delete("/products/{product_id}")
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Désactive un produit (soft delete)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Produit non trouvé")
    
    product.is_active = False
    db.commit()
    
    return {"message": "Produit désactivé avec succès"}


# =========================
# MOUVEMENTS DE STOCK
# =========================

@router.post("/stock/movements", response_model=StockMovementResponse)
def create_stock_movement(
    movement: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Crée un mouvement de stock"""
    try:
        # Vérifier si le produit existe
        product = db.query(Product).filter(Product.id == movement.product_id).first()
        if not product:
            raise HTTPException(404, "Produit non trouvé")
        
        # Créer le mouvement
        db_movement = StockMovement(**movement.dict())
        db.add(db_movement)
        db.commit()
        db.refresh(db_movement)
        
        # Récupérer avec les informations du produit
        db_movement.product_name = product.name
        return db_movement
    except Exception as e:
        db.rollback()
        raise HTTPException(400, str(e))


@router.get("/stock/movements")
def get_stock_movements(
    product_id: Optional[str] = Query(None),
    supplier_id: Optional[str] = Query(None),
    movement_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère l'historique des mouvements de stock"""
    query = db.query(StockMovement)
    
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    
    if supplier_id:
        query = query.filter(StockMovement.supplier_id == supplier_id)
    
    if movement_type:
        query = query.filter(StockMovement.movement_type == movement_type)
    
    if start_date:
        query = query.filter(StockMovement.movement_date >= start_date)
    
    if end_date:
        query = query.filter(StockMovement.movement_date <= end_date)
    
    movements = query.order_by(StockMovement.movement_date.desc())\
                    .offset(skip).limit(limit).all()
    
    # Enrichir avec les noms de produits et fournisseurs
    result = []
    for movement in movements:
        product = db.query(Product).filter(Product.id == movement.product_id).first()
        supplier = db.query(Supplier).filter(Supplier.id == movement.supplier_id).first() if movement.supplier_id else None
        
        result.append({
            "id": movement.id,
            "product_id": movement.product_id,
            "product_name": product.name if product else "Inconnu",
            "movement_type": movement.movement_type,
            "quantity": movement.quantity,
            "unit_cost": float(movement.unit_cost) if movement.unit_cost else None,
            "total_cost": float(movement.total_cost) if movement.total_cost else None,
            "reason": movement.reason,
            "reference": movement.reference,
            "supplier_id": movement.supplier_id,
            "supplier_name": supplier.name if supplier else None,
            "movement_date": movement.movement_date,
            "created_at": movement.created_at
        })
    
    return result


@router.get("/products/{product_id}/stock-history")
def get_product_stock_history(
    product_id: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Historique des mouvements de stock pour un produit"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        history = inventory.product.get_stock_history(
            db=db,
            product_id=product_id,
            start_date=start_date,
            end_date=end_date,
            limit=100
        )
        
        return history
    except Exception as e:
        logger.error(f"Erreur historique stock: {str(e)}")
        raise HTTPException(500, f"Erreur lors de la récupération de l'historique: {str(e)}")


# =========================
# FOURNISSEURS
# =========================

@router.post("/suppliers", response_model=SupplierResponse)
def create_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Crée un nouveau fournisseur"""
    try:
        db_supplier = Supplier(**supplier.dict())
        db.add(db_supplier)
        db.commit()
        db.refresh(db_supplier)
        return db_supplier
    except Exception as e:
        db.rollback()
        raise HTTPException(400, str(e))


@router.get("/suppliers", response_model=List[SupplierResponse])
def get_suppliers(
    search: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère la liste des fournisseurs"""
    try:
        suppliers = inventory.supplier.search_suppliers(
            db=db,
            search=search,
            city=city,
            active_only=active_only,
            skip=skip,
            limit=limit
        )
        return suppliers
    except Exception as e:
        logger.error(f"Erreur recherche fournisseurs: {str(e)}")
        raise HTTPException(500, f"Erreur lors de la recherche: {str(e)}")


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: str,
    with_stats: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère un fournisseur spécifique"""
    if with_stats:
        supplier_data = inventory.supplier.get_with_stats(db, supplier_id)
    else:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            raise HTTPException(404, "Fournisseur non trouvé")
        supplier_data = {c.name: getattr(supplier, c.name) for c in supplier.__table__.columns}
    
    if not supplier_data:
        raise HTTPException(404, "Fournisseur non trouvé")
    
    return supplier_data


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: str,
    supplier_update: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Met à jour un fournisseur"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(404, "Fournisseur non trouvé")
    
    update_data = supplier_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)
    
    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/suppliers/{supplier_id}")
def delete_supplier(
    supplier_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Désactive un fournisseur (soft delete)"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(404, "Fournisseur non trouvé")
    
    supplier.is_active = False
    db.commit()
    
    return {"message": "Fournisseur désactivé avec succès"}


@router.get("/suppliers/{supplier_id}/products")
def get_supplier_products(
    supplier_id: str,
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère tous les produits fournis par un fournisseur"""
    try:
        products = inventory.supplier.get_supplier_products(
            db=db,
            supplier_id=supplier_id,
            active_only=active_only
        )
        return products
    except Exception as e:
        logger.error(f"Erreur produits fournisseur: {str(e)}")
        raise HTTPException(500, f"Erreur lors de la récupération: {str(e)}")


# =========================
# ALERTES DE STOCK
# =========================

@router.get("/alerts/low-stock")
def get_low_stock_alerts(
    threshold_percentage: float = Query(0.3, ge=0.1, le=1.0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère les produits avec stock faible"""
    try:
        products = db.query(Product).filter(Product.is_active == True).all()
        
        low_stock = []
        for product in products:
            if product.alert_threshold <= 0:
                continue
                
            current_stock = inventory.product.calculate_current_stock(db, product.id)
            if 0 < current_stock <= (product.alert_threshold * threshold_percentage):
                low_stock.append({
                    "product": {
                        "id": product.id,
                        "name": product.name,
                        "category": product.category,
                        "sku": product.sku
                    },
                    "current_stock": current_stock,
                    "alert_threshold": product.alert_threshold,
                    "percentage": (current_stock / product.alert_threshold) * 100
                })
        
        # Trier par pourcentage le plus bas
        low_stock.sort(key=lambda x: x["percentage"])
        
        return low_stock[:limit]
    except Exception as e:
        logger.error(f"Erreur alertes stock: {str(e)}")
        raise HTTPException(500, f"Erreur lors de la récupération des alertes: {str(e)}")


@router.get("/alerts/out-of-stock")
def get_out_of_stock_alerts(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère les produits en rupture de stock"""
    try:
        products = db.query(Product).filter(Product.is_active == True).all()
        
        out_of_stock = []
        for product in products:
            current_stock = inventory.product.calculate_current_stock(db, product.id)
            if current_stock <= 0:
                out_of_stock.append({
                    "product": {
                        "id": product.id,
                        "name": product.name,
                        "category": product.category,
                        "sku": product.sku
                    },
                    "current_stock": current_stock,
                    "last_movement": db.query(StockMovement.movement_date)
                        .filter(StockMovement.product_id == product.id)
                        .order_by(StockMovement.movement_date.desc())
                        .first()
                })
        
        return out_of_stock[:limit]
    except Exception as e:
        logger.error(f"Erreur rupture stock: {str(e)}")
        raise HTTPException(500, f"Erreur lors de la récupération: {str(e)}")


# =========================
# RAPPORTS INVENTAIRE
# =========================

@router.get("/reports/stock-value")
def get_stock_value_report(
    by_category: bool = Query(False),
    by_supplier: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Rapport de la valeur du stock"""
    try:
        # Valeur totale du stock
        total_value = db.query(
            func.sum(StockMovement.total_cost)
        ).filter(StockMovement.movement_type.in_(["IN", "ADJUSTMENT"]))\
         .scalar() or 0
        
        result = {
            "total_stock_value": float(total_value),
            "total_products": db.query(Product).filter(Product.is_active == True).count(),
            "total_items": db.query(func.sum(StockMovement.quantity))
                .filter(StockMovement.movement_type.in_(["IN", "ADJUSTMENT"]))
                .scalar() or 0
        }
        
        # Par catégorie
        if by_category:
            category_value = db.query(
                Product.category,
                func.sum(StockMovement.total_cost).label("value")
            ).join(StockMovement, StockMovement.product_id == Product.id)\
             .filter(StockMovement.movement_type.in_(["IN", "ADJUSTMENT"]))\
             .group_by(Product.category).all()
            
            result["by_category"] = [
                {"category": cat, "value": float(val or 0)}
                for cat, val in category_value
            ]
        
        # Par fournisseur
        if by_supplier:
            supplier_value = db.query(
                Supplier.name,
                func.sum(StockMovement.total_cost).label("value")
            ).join(StockMovement, StockMovement.supplier_id == Supplier.id)\
             .filter(StockMovement.movement_type.in_(["IN", "ADJUSTMENT"]))\
             .group_by(Supplier.name).all()
            
            result["by_supplier"] = [
                {"supplier": name, "value": float(val or 0)}
                for name, val in supplier_value
            ]
        
        return result
    except Exception as e:
        logger.error(f"Erreur rapport valeur stock: {str(e)}")
        raise HTTPException(500, f"Erreur lors du rapport: {str(e)}")


@router.get("/reports/stock-turnover")
def get_stock_turnover_report(
    days: int = Query(90, ge=30, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Rapport de rotation des stocks"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Mouvements de stock
        movements_in = db.query(
            StockMovement.product_id,
            func.sum(StockMovement.quantity).label("quantity_in"),
            func.sum(StockMovement.total_cost).label("cost_in")
        ).filter(
            StockMovement.movement_type.in_(["IN", "ADJUSTMENT"]),
            StockMovement.movement_date >= start_date
        ).group_by(StockMovement.product_id).subquery()
        
        movements_out = db.query(
            StockMovement.product_id,
            func.sum(StockMovement.quantity).label("quantity_out")
        ).filter(
            StockMovement.movement_type == "OUT",
            StockMovement.movement_date >= start_date
        ).group_by(StockMovement.product_id).subquery()
        
        # Requête de rotation
        turnover = db.query(
            Product.id,
            Product.name,
            Product.category,
            Product.sku,
            movements_in.c.quantity_in,
            movements_in.c.cost_in,
            movements_out.c.quantity_out,
            inventory.product.calculate_current_stock(db, Product.id).label("current_stock")
        ).outerjoin(movements_in, movements_in.c.product_id == Product.id)\
         .outerjoin(movements_out, movements_out.c.product_id == Product.id)\
         .filter(Product.is_active == True)\
         .all()
        
        result = []
        for row in turnover:
            quantity_in = row.quantity_in or 0
            quantity_out = row.quantity_out or 0
            current_stock = row.current_stock or 0
            
            # Calculer le taux de rotation
            avg_stock = (quantity_in + current_stock) / 2 if quantity_in > 0 else 0
            turnover_rate = quantity_out / avg_stock if avg_stock > 0 else 0
            
            result.append({
                "product_id": row.id,
                "product_name": row.name,
                "category": row.category,
                "sku": row.sku,
                "quantity_in": quantity_in,
                "quantity_out": quantity_out,
                "current_stock": current_stock,
                "turnover_rate": float(turnover_rate),
                "status": "FAIBLE" if turnover_rate < 0.5 else "NORMAL" if turnover_rate < 2 else "ÉLEVÉ"
            })
        
        # Trier par taux de rotation
        result.sort(key=lambda x: x["turnover_rate"], reverse=True)
        
        return {
            "period_days": days,
            "total_products": len(result),
            "average_turnover": sum(r["turnover_rate"] for r in result) / len(result) if result else 0,
            "products": result[:50]  # Limiter à 50 produits
        }
    except Exception as e:
        logger.error(f"Erreur rapport rotation: {str(e)}")
        raise HTTPException(500, f"Erreur lors du rapport: {str(e)}")
    
    # =========================
# COMMANDES FOURNISSEURS
# =========================

@router.post("/purchase-orders", response_model=PurchaseOrderResponse)
def create_purchase_order(
    order_in: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Crée une nouvelle commande fournisseur."""
    try:
        order = inventory.create_purchase_order(
            db=db,
            order_in=order_in,
            user_id=current_user.get("id")
        )
        return order
    except Exception as e:
        logger.error(f"Erreur création commande: {str(e)}")
        raise HTTPException(400, str(e))


@router.get("/purchase-orders")
def get_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    supplier_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Liste les commandes fournisseurs avec pagination et filtres."""
    try:
        result = inventory.get_purchase_orders(
            db=db,
            skip=skip,
            limit=limit,
            supplier_id=supplier_id,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        return result
    except Exception as e:
        logger.error(f"Erreur liste commandes: {str(e)}")
        raise HTTPException(500, f"Erreur lors de la récupération: {str(e)}")


@router.get("/purchase-orders/{order_id}")
def get_purchase_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère une commande fournisseur avec ses détails."""
    try:
        order = inventory.get_purchase_order(db, order_id)
        if not order:
            raise HTTPException(404, "Commande non trouvée")
        return order
    except Exception as e:
        logger.error(f"Erreur récupération commande: {str(e)}")
        raise HTTPException(500, f"Erreur lors de la récupération: {str(e)}")


@router.post("/purchase-orders/{order_id}/receive")
def receive_purchase_order(
    order_id: str,
    items: List[Dict[str, Any]] = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Réceptionne partiellement ou totalement une commande."""
    try:
        order = inventory.receive_purchase_order(
            db=db,
            order_id=order_id,
            items=items,
            user_id=current_user.get("id")
        )
        return {"message": "Commande réceptionnée avec succès", "order": order}
    except NotFoundException as e:
        raise HTTPException(404, str(e))
    except BusinessLogicException as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Erreur réception commande: {str(e)}")
        raise HTTPException(500, f"Erreur lors de la réception: {str(e)}")


@router.delete("/purchase-orders/{order_id}")
def delete_purchase_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Supprime une commande fournisseur (seulement si en attente ou annulée)."""
    try:
        success = inventory.delete_purchase_order(db, order_id)
        if not success:
            raise HTTPException(404, "Commande non trouvée")
        return {"message": "Commande supprimée avec succès"}
    except BusinessLogicException as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Erreur suppression commande: {str(e)}")
        raise HTTPException(500, f"Erreur lors de la suppression: {str(e)}")