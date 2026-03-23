# backend\routes\stock.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from typing import List, Optional
from crud.product import product as product_crud
from pydantic import BaseModel
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal

class BulkStockAdjustment(BaseModel):
    product_id: str
    quantity: int
    movement_type: str
    reason: str = None

router = APIRouter()

@router.post("/stock/movements/", response_model=schemas.StockMovementResponse)
def create_stock_movement(movement: schemas.StockMovementCreate, db: Session = Depends(get_db)):
    """Crée un mouvement de stock avec validation et mise à jour du coût total."""
    product = db.query(models.Product).filter(models.Product.id == movement.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Vérification du stock disponible pour une sortie
    if movement.movement_type in ["OUT", "DAMAGED"]:
        current_stock = product_crud.calculate_current_stock(db, movement.product_id)
        if current_stock < movement.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuffisant. Disponible: {current_stock}, Demandé: {movement.quantity}"
            )
    
    # Calcul du coût total si unit_cost est fourni
    total_cost = None
    if movement.unit_cost:
        total_cost = movement.unit_cost * movement.quantity
    
    # Création du mouvement
    db_movement = models.StockMovement(
        **movement.dict(exclude_unset=True),
        total_cost=total_cost,
        movement_date=movement.movement_date or datetime.utcnow()
    )
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    return db_movement

@router.get("/stock/movements/", response_model=List[schemas.StockMovementResponse])
def read_stock_movements(
    product_id: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.StockMovement)
    if product_id:
        query = query.filter(models.StockMovement.product_id == product_id)
    movements = query.order_by(models.StockMovement.movement_date.desc()).offset(skip).limit(limit).all()
    # Ajouter le nom du produit pour le frontend
    result = []
    for m in movements:
        m_dict = {c.name: getattr(m, c.name) for c in m.__table__.columns}
        m_dict["product_name"] = m.product.name if m.product else None
        result.append(schemas.StockMovementResponse(**m_dict))
    return result

@router.get("/stock/alerts/")
def get_stock_alerts(db: Session = Depends(get_db)):
    """Retourne les produits en alerte et en rupture."""
    products = db.query(models.Product).filter(models.Product.is_active == True).all()
    low_stock = []
    out_of_stock = []
    
    for product in products:
        stock = product_crud.calculate_current_stock(db, product.id)
        if stock <= 0:
            out_of_stock.append({
                "id": product.id,
                "name": product.name,
                "current_stock": stock,
                "threshold": product.alert_threshold
            })
        elif stock <= product.alert_threshold:
            low_stock.append({
                "id": product.id,
                "name": product.name,
                "current_stock": stock,
                "threshold": product.alert_threshold
            })
    
    return {
        "low_stock": low_stock,
        "out_of_stock": out_of_stock
    }

@router.get("/stock/trends")
def get_stock_trends(db: Session = Depends(get_db), days: int = 30):
    """Tendances des entrées/sorties sur les derniers jours."""
    start_date = datetime.utcnow() - timedelta(days=days)
    movements = db.query(models.StockMovement).filter(
        models.StockMovement.movement_date >= start_date
    ).all()

    daily_in = defaultdict(int)
    daily_out = defaultdict(int)
    for m in movements:
        day_key = m.movement_date.strftime("%Y-%m-%d")
        if m.movement_type in ["IN", "RETURN", "ADJUSTMENT"]:
            daily_in[day_key] += m.quantity
        elif m.movement_type in ["OUT", "DAMAGED"]:
            daily_out[day_key] += m.quantity

    all_days = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days+1)]
    in_trend = [daily_in.get(day, 0) for day in all_days]
    out_trend = [daily_out.get(day, 0) for day in all_days]

    return {
        "dates": all_days,
        "in": in_trend,
        "out": out_trend
    }

@router.post("/stock/bulk")
def bulk_stock_adjustments(adjustments: List[BulkStockAdjustment], db: Session = Depends(get_db)):
    """
    Ajustements multiples en une seule transaction atomique.
    """
    results = []
    try:
        for adj in adjustments:
            movement = product_crud.update_stock(
                db=db,
                product_id=adj.product_id,
                quantity=abs(adj.quantity),
                movement_type=adj.movement_type,
                reason=adj.reason
            )
            results.append({"product_id": adj.product_id, "success": True, "movement_id": movement.id})
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors des ajustements: {str(e)}")
    return results