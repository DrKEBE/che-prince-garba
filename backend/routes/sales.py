# backend/routes/sales.py 
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

import schemas
from database import get_db
from crud.product import product as product_crud
from crud.sale_service import sale_refund_service
from core.exceptions import NotFoundException, BusinessLogicException
from middleware.auth import get_current_user, require_role
from schemas import UserRole, RefundCreate, RefundApprove, RefundProcess

router = APIRouter(prefix="/sales", tags=["Ventes"])


# =========================
# ROUTES DE VENTES
# =========================

@router.post("/", response_model=Dict[str, Any], status_code=201)
def create_sale(
    sale_data: schemas.SaleCreate,
    db: Session = Depends(get_db),
    # UTILISATION COMME DÉPENDANCE
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER]))
):
    """Crée une nouvelle vente"""
    try:
        sale = sale_refund_service.create_sale(db, sale_data, current_user.get("id"))
        return sale
    except BusinessLogicException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/", response_model=List[Dict[str, Any]])
def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    client_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère la liste des ventes avec filtres"""
    from models import Sale, Client
    from sqlalchemy import or_
    
    query = db.query(Sale)
    
    if client_id:
        query = query.filter(Sale.client_id == client_id)
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Sale.sale_date >= start)
        except ValueError:
            raise HTTPException(400, detail="Format de date invalide")
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Sale.sale_date <= end)
        except ValueError:
            raise HTTPException(400, detail="Format de date invalide")
    
    if payment_status:
        query = query.filter(Sale.payment_status == payment_status)
    
    if payment_method:
        query = query.filter(Sale.payment_method == payment_method)
    
    if min_amount is not None:
        query = query.filter(Sale.final_amount >= min_amount)
    
    if max_amount is not None:
        query = query.filter(Sale.final_amount <= max_amount)
    
    sales = query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
    
    result = []
    for sale in sales:
        client_name = None
        if sale.client_id:
            client = db.query(Client).filter(Client.id == sale.client_id).first()
            client_name = client.full_name if client else None
        
        result.append({
            "id": sale.id,
            "invoice_number": sale.invoice_number,
            "client_id": sale.client_id,
            "client_name": client_name,
            "sale_date": sale.sale_date,
            "final_amount": float(sale.final_amount),
            "payment_method": sale.payment_method,
            "payment_status": sale.payment_status,
            "total_profit": float(sale.total_profit),
            "refunded_amount": float(sale.refunded_amount),
            "is_refundable": sale.is_refundable
        })
    
    return result


@router.get("/{sale_id}", response_model=Dict[str, Any])
def get_sale(
    sale_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère une vente par son ID"""
    try:
        return sale_refund_service.get_sale_details(db, sale_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{sale_id}/refundable-items")
def get_refundable_items(
    sale_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère les articles remboursables d'une vente"""
    from models import Sale, SaleItem, RefundItem, Product, Refund
    
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise NotFoundException("Vente", sale_id)
    
    # Calculer les quantités déjà remboursées
    refunded_items = {}
    refund_items = db.query(RefundItem).join(
        Refund, RefundItem.refund_id == Refund.id
    ).filter(
        Refund.sale_id == sale_id,
        Refund.refund_status.in_(["APPROVED", "COMPLETED"])
    ).all()
    
    for item in refund_items:
        if item.sale_item_id not in refunded_items:
            refunded_items[item.sale_item_id] = 0
        refunded_items[item.sale_item_id] += item.quantity
    
    # Articles remboursables
    refundable_items = []
    sale_items = db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()
    
    for item in sale_items:
        already_refunded = refunded_items.get(item.id, 0)
        refundable_qty = item.quantity - already_refunded
        
        if refundable_qty > 0:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            refundable_items.append({
                "sale_item_id": item.id,
                "product_id": item.product_id,
                "product_name": product.name if product else "Produit inconnu",
                "product_sku": product.sku if product else None,
                "quantity": item.quantity,
                "already_refunded": already_refunded,
                "refundable_quantity": refundable_qty,
                "unit_price": float(item.unit_price),
                "total_price": float(item.total_price),
                "max_refund_price": float(item.unit_price),
                "current_stock": product_crud.calculate_current_stock(db, item.product_id) if product else 0
            })
    
    return {
        "sale_id": sale_id,
        "invoice_number": sale.invoice_number,
        "sale_date": sale.sale_date,
        "total_amount": float(sale.final_amount),
        "already_refunded": float(sale.refunded_amount),
        "remaining_refundable": float(sale.final_amount) - float(sale.refunded_amount),
        "is_refundable": sale.is_refundable,
        "refund_deadline": sale.refund_deadline,
        "client_name": sale.client.full_name if sale.client else None,
        "client_id": sale.client_id,
        "items": refundable_items
    }


# =========================
# ROUTES DE REMBOURSEMENTS
# =========================

@router.post("/{sale_id}/refunds/", response_model=Dict[str, Any], status_code=201)
def create_refund_for_sale(
    sale_id: str,
    refund_data: RefundCreate,
    db: Session = Depends(get_db),
    # UTILISATION COMME DÉPENDANCE
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER]))
):
    """Crée un remboursement pour une vente"""
    try:
        refund = sale_refund_service.create_refund(
            db, sale_id, refund_data, current_user.get("id")
        )
        return refund
    except (BusinessLogicException, NotFoundException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/{sale_id}/refunds/")
def get_sale_refunds(
    sale_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère tous les remboursements d'une vente"""
    from models import Refund
    
    refunds = db.query(Refund).filter(
        Refund.sale_id == sale_id
    ).order_by(Refund.created_at.desc()).all()
    
    result = []
    for refund in refunds:
        result.append({
            "id": refund.id,
            "refund_number": refund.refund_number,
            "refund_amount": float(refund.refund_amount),
            "refund_reason": refund.refund_reason,
            "refund_method": refund.refund_method,
            "refund_status": refund.refund_status,
            "is_partial": refund.is_partial,
            "created_at": refund.created_at,
            "approved_at": refund.approved_at
        })
    
    return {
        "sale_id": sale_id,
        "total_refunds": len(refunds),
        "refunds": result
    }


@router.get("/refunds/", response_model=List[Dict[str, Any]])
def get_all_refunds(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    sale_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    # UTILISATION COMME DÉPENDANCE
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Récupère tous les remboursements avec filtres"""
    from models import Refund, Sale
    
    query = db.query(Refund)
    
    if status:
        query = query.filter(Refund.refund_status == status)
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Refund.created_at >= start)
        except ValueError:
            raise HTTPException(400, detail="Format de date invalide")
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Refund.created_at <= end)
        except ValueError:
            raise HTTPException(400, detail="Format de date invalide")
    
    if sale_id:
        query = query.filter(Refund.sale_id == sale_id)
    
    refunds = query.order_by(Refund.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for refund in refunds:
        sale = db.query(Sale).filter(Sale.id == refund.sale_id).first()
        client_name = None
        if sale and sale.client:
            client_name = sale.client.full_name
        
        result.append({
            "id": refund.id,
            "refund_number": refund.refund_number,
            "sale_id": refund.sale_id,
            "invoice_number": sale.invoice_number if sale else None,
            "client_name": client_name,
            "refund_amount": float(refund.refund_amount),
            "refund_reason": refund.refund_reason,
            "refund_method": refund.refund_method,
            "refund_status": refund.refund_status,
            "is_partial": refund.is_partial,
            "refund_date": refund.refund_date,
            "approved_at": refund.approved_at
        })
    
    return result


@router.get("/refunds/{refund_id}", response_model=Dict[str, Any])
def get_refund_details(
    refund_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère les détails d'un remboursement"""
    try:
        return sale_refund_service.get_refund_details(db, refund_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/refunds/{refund_id}/approve", response_model=Dict[str, Any])
def approve_refund(
    refund_id: str,
    approve_data: RefundApprove,
    db: Session = Depends(get_db),
    # UTILISATION COMME DÉPENDANCE
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Approuve ou rejette un remboursement"""
    try:
        return sale_refund_service.approve_refund(
            db, refund_id, approve_data, current_user.get("id")
        )
    except (BusinessLogicException, NotFoundException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.put("/refunds/{refund_id}/process", response_model=Dict[str, Any])
def process_refund(
    refund_id: str,
    process_data: RefundProcess,
    db: Session = Depends(get_db),
    # UTILISATION COMME DÉPENDANCE
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER]))
):
    """Traite un remboursement (exécute le paiement)"""
    try:
        return sale_refund_service.process_refund(
            db, refund_id, process_data, current_user.get("id")
        )
    except (BusinessLogicException, NotFoundException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# =========================
# STATISTIQUES
# =========================

@router.get("/performance/daily")
def get_daily_sales_performance(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Performance des ventes quotidiennes"""
    return sale_refund_service.get_daily_sales(db)


@router.get("/period-analysis")
def get_sales_period_analysis(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Analyse des ventes sur une période"""
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        return sale_refund_service.get_sales_period(db, start, end)
    except ValueError:
        raise HTTPException(400, detail="Format de date invalide")


@router.get("/refund-stats")
def get_refund_statistics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    days: Optional[int] = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Statistiques des remboursements"""
    if start_date and end_date:
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(400, detail="Format de date invalide")
    else:
        end = datetime.utcnow()
        start = end - timedelta(days=days)
    
    return sale_refund_service.get_refund_stats(db, start, end)