# backend/utils/stock.py
from sqlalchemy.orm import Session
from sqlalchemy import func
import models

def compute_stock(db: Session, product_id: str) -> int:
    """Calcule le stock actuel d'un produit"""
    # Stock entrant (IN, ADJUSTMENT positif, RETOUR)
    stock_in = db.query(
        func.coalesce(func.sum(models.StockMovement.quantity), 0)
    ).filter(
        models.StockMovement.product_id == product_id,
        models.StockMovement.movement_type.in_(["IN", "ADJUSTMENT", "RETURN"])
    ).scalar()

    # Stock sortant (OUT, DAMAGED, ADJUSTMENT négatif)
    stock_out = db.query(
        func.coalesce(func.sum(models.StockMovement.quantity), 0)
    ).filter(
        models.StockMovement.product_id == product_id,
        models.StockMovement.movement_type.in_(["OUT", "DAMAGED"])
    ).scalar()

    # Pour les ajustements négatifs, nous devons les traiter séparément
    adjustments_negatif = db.query(
        func.coalesce(func.sum(models.StockMovement.quantity), 0)
    ).filter(
        models.StockMovement.product_id == product_id,
        models.StockMovement.movement_type == "ADJUSTMENT",
        models.StockMovement.quantity < 0
    ).scalar() or 0

    return stock_in - stock_out + adjustments_negatif

def get_stock_status(stock: int, threshold: int) -> str:
    """Détermine le statut du stock"""
    if stock <= 0:
        return "RUPTURE"
    elif stock <= threshold:
        return "ALERTE"
    elif stock <= threshold * 2:
        return "NORMAL"
    else:
        return "EXCÉDENT"

def compute_product_stock_with_status(db: Session, product_id: str, alert_threshold: int = None) -> dict:
    """Calcule le stock et le statut d'un produit"""
    stock = compute_stock(db, product_id)
    
    if alert_threshold is None:
        # Récupérer le seuil d'alerte du produit
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        alert_threshold = product.alert_threshold if product else 10
    
    status = get_stock_status(stock, alert_threshold)
    
    return {
        "current_stock": stock,
        "stock_status": status,
        "alert_threshold": alert_threshold
    }