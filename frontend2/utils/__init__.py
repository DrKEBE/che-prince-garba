



# backend\routes\suppliers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from typing import List

router = APIRouter()

@router.post("/suppliers/", response_model=schemas.SupplierResponse)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    db_supplier = models.Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.get("/suppliers/", response_model=List[schemas.SupplierResponse])
def read_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    suppliers = db.query(models.Supplier).filter(models.Supplier.is_active == True).offset(skip).limit(limit).all()
    return suppliers

@router.get("/suppliers/{supplier_id}", response_model=schemas.SupplierResponse)
def read_supplier(supplier_id: str, db: Session = Depends(get_db)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if supplier is None:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    return supplier

@router.put("/suppliers/{supplier_id}", response_model=schemas.SupplierResponse)
def update_supplier(supplier_id: str, supplier: schemas.SupplierUpdate, db: Session = Depends(get_db)):
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    
    for key, value in supplier.dict(exclude_unset=True).items():
        setattr(db_supplier, key, value)
    
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


# backend/routes/stock.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from typing import List
from utils.stock import compute_stock  # Import

router = APIRouter()

@router.post("/stock/movements/", response_model=schemas.StockMovementResponse)
def create_stock_movement(movement: schemas.StockMovementCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == movement.product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Vérification du stock disponible pour un mouvement de sortie
    if movement.movement_type == "OUT":
        current_stock = compute_stock(db, movement.product_id)
        if current_stock < movement.quantity:
            raise HTTPException(status_code=400, detail="Stock insuffisant")
    
    # Pas de mise à jour de product.quantity car on utilise les mouvements
    db_movement = models.StockMovement(**movement.dict())
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    return db_movement

@router.get("/stock/movements/", response_model=List[schemas.StockMovementResponse])
def read_stock_movements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movements = db.query(models.StockMovement).offset(skip).limit(limit).all()
    return movements

@router.get("/stock/alerts/")
def get_stock_alerts(db: Session = Depends(get_db)):
    # Produits avec stock faible
    products = db.query(models.Product).filter(models.Product.is_active == True).all()
    low_stock = []
    out_of_stock = []
    
    for product in products:
        stock = compute_stock(db, product.id)
        if stock <= 0:
            out_of_stock.append(product)
        elif stock <= product.alert_threshold:
            low_stock.append(product)
    
    return {
        "low_stock": low_stock,
        "out_of_stock": out_of_stock
    }

# backend\routes\dashboard.py

"""
Routes de dashboard avec statistiques avancées
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, distinct, and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
import logging

from crud.product import product as product_crud
from database import get_db
from models import (
    Sale, SaleItem, Product, Client, Expense, 
    Appointment, Supplier, StockMovement, Refund
)
from schemas import DashboardStats, SalesTrendItem, TopProductItem
from crud.sale_service import sale_refund_service
from middleware.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Tableau de bord"])
logger = logging.getLogger(__name__)


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Statistiques globales pour le dashboard
    """
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())
    yesterday = today - timedelta(days=1)
    
    # =========================
    # PRODUITS
    # =========================
    total_products = db.query(Product).filter(Product.is_active == True).count()
    
    # Produits en rupture et faible stock
    products = db.query(Product).filter(Product.is_active == True).all()
    out_of_stock = 0
    low_stock = 0
    critical_stock = 0
    
    for product in products:
        stock = product_crud.calculate_current_stock(db, product.id)
        if stock <= 0:
            out_of_stock += 1
        elif stock <= product.alert_threshold:
            low_stock += 1
        elif stock <= product.alert_threshold * 2:
            critical_stock += 1
    
    # =========================
    # CLIENTS
    # =========================
    total_clients = db.query(Client).count()
    
    # Nouveaux clients ce mois
    new_clients_month = db.query(Client).filter(
        extract('month', Client.created_at) == today.month,
        extract('year', Client.created_at) == today.year
    ).count()
    
    # Clients VIP
    vip_clients = db.query(Client).filter(Client.client_type == "VIP").count()
    
    # =========================
    # VENTES
    # =========================
    total_sales = db.query(Sale).filter(Sale.payment_status == "PAID").count()
    
    # Chiffre d'affaires
    daily_revenue = db.query(func.sum(Sale.final_amount)).filter(
        func.date(Sale.sale_date) == today,
        Sale.payment_status == "PAID"
    ).scalar() or 0
    
    yesterday_revenue = db.query(func.sum(Sale.final_amount)).filter(
        func.date(Sale.sale_date) == yesterday,
        Sale.payment_status == "PAID"
    ).scalar() or 0
    
    weekly_revenue = db.query(func.sum(Sale.final_amount)).filter(
        Sale.sale_date >= week_start,
        Sale.payment_status == "PAID"
    ).scalar() or 0
    
    monthly_revenue = db.query(func.sum(Sale.final_amount)).filter(
        Sale.sale_date >= month_start,
        Sale.payment_status == "PAID"
    ).scalar() or 0
    
    # =========================
    # PROFITS
    # =========================
    daily_profit = db.query(func.sum(Sale.total_profit)).filter(
        func.date(Sale.sale_date) == today,
        Sale.payment_status == "PAID"
    ).scalar() or 0
    
    weekly_profit = db.query(func.sum(Sale.total_profit)).filter(
        Sale.sale_date >= week_start,
        Sale.payment_status == "PAID"
    ).scalar() or 0
    
    monthly_profit = db.query(func.sum(Sale.total_profit)).filter(
        Sale.sale_date >= month_start,
        Sale.payment_status == "PAID"
    ).scalar() or 0
    
    total_profit = db.query(func.sum(Sale.total_profit)).filter(
        Sale.payment_status == "PAID"
    ).scalar() or 0
    
    # =========================
    # AUTRES STATISTIQUES
    # =========================
    # Rendez-vous du jour
    today_appointments = db.query(Appointment).filter(
        func.date(Appointment.appointment_date) == today,
        Appointment.status.in_(["SCHEDULED", "CONFIRMED"])
    ).count()
    
    # Dépenses du mois
    monthly_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.expense_date >= month_start
    ).scalar() or 0
    
    # Remboursements en attente
    pending_refunds = db.query(Refund).filter(
        Refund.refund_status == "PENDING"
    ).count()
    
    # Taux de conversion (ventes/clients)
    conversion_rate = (total_sales / total_clients * 100) if total_clients > 0 else 0
    
    # Panier moyen
    avg_ticket = db.query(func.avg(Sale.final_amount)).filter(
        Sale.payment_status == "PAID"
    ).scalar() or 0
    
    # =========================
    # CALCUL DES TENDANCES
    # =========================
    # Tendance CA journalier
    revenue_trend = 0
    if yesterday_revenue > 0:
        revenue_trend = ((daily_revenue - yesterday_revenue) / yesterday_revenue) * 100
    
    # Tendance clients
    last_month_clients = db.query(Client).filter(
        Client.created_at >= month_start - timedelta(days=30),
        Client.created_at < month_start
    ).count()
    
    client_trend = 0
    if last_month_clients > 0:
        client_trend = ((new_clients_month - last_month_clients) / last_month_clients) * 100
    
    return {
        "total_products": total_products,
        "total_clients": total_clients,
        "total_sales": total_sales,
        "daily_revenue": float(daily_revenue),
        "weekly_revenue": float(weekly_revenue),
        "monthly_revenue": float(monthly_revenue),
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
        "critical_stock": critical_stock,
        "total_profit": float(total_profit),
        "daily_profit": float(daily_profit),
        "weekly_profit": float(weekly_profit),
        "monthly_profit": float(monthly_profit),
        "pending_orders": 0,  # À implémenter avec PurchaseOrder
        "pending_appointments": today_appointments,
        "new_clients_month": new_clients_month,
        "vip_clients": vip_clients,
        "monthly_expenses": float(monthly_expenses),
        "pending_refunds": pending_refunds,
        "conversion_rate": float(conversion_rate),
        "avg_ticket": float(avg_ticket),
        "revenue_trend": float(revenue_trend),
        "client_trend": float(client_trend),
        "profit_margin": (float(monthly_profit) / float(monthly_revenue) * 100) if monthly_revenue > 0 else 0
    }


@router.get("/sales-trend")
def get_sales_trend(
    days: int = Query(30, ge=1, le=365),
    group_by: str = Query("day", pattern="^(day|week|month)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Tendances des ventes sur une période
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Fonction pour formater la période selon le group_by
    def format_period(period, group_by):
        """Formate une période selon le type de regroupement"""
        if period is None:
            return ""
        
        # Si c'est déjà une chaîne, la retourner telle quelle
        if isinstance(period, str):
            return period
        
        # Si c'est un objet date/datetime, le formater
        try:
            if group_by == "day":
                return period.strftime("%Y-%m-%d")
            elif group_by == "week":
                # Pour les semaines, retourner lundi de la semaine
                if isinstance(period, date):
                    period = datetime.combine(period, datetime.min.time())
                # Calculer le lundi de la semaine
                monday = period - timedelta(days=period.weekday())
                return monday.strftime("%Y-%m-%d")
            else:  # month
                return period.strftime("%Y-%m")
        except AttributeError:
            return str(period)
    
    if group_by == "day":
        date_expr = func.date(Sale.sale_date)
        group_by_field = func.date(Sale.sale_date)

    elif group_by == "week":
        date_expr = func.strftime('%Y-%W', Sale.sale_date)
        group_by_field = func.strftime('%Y-%W', Sale.sale_date)

    else:  # month
        date_expr = func.strftime('%Y-%m', Sale.sale_date)
        group_by_field = func.strftime('%Y-%m', Sale.sale_date)

    
    # Ventes par période - CORRIGÉ : éviter le produit cartésien
    sales_data = db.query(
        date_expr.label("period"),
        func.count(Sale.id).label("sales_count"),
        func.sum(Sale.final_amount).label("amount"),
        func.sum(Sale.total_profit).label("profit"),
        func.avg(Sale.final_amount).label("avg_ticket")
    ).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.payment_status == "PAID"
    ).group_by(
        group_by_field
    ).order_by(
        group_by_field
    ).all()
    
    # Remboursements par période - CORRIGÉ : requête séparée sans jointure implicite
    refunds_data = db.query(
        date_expr.label("period"),
        func.count(Refund.id).label("refunds_count"),
        func.sum(Refund.refund_amount).label("refund_amount")
    ).filter(
        Refund.created_at >= start_date,
        Refund.created_at <= end_date,
        Refund.refund_status.in_(["APPROVED", "COMPLETED"])
    ).group_by(
        group_by_field
    ).order_by(
        group_by_field
    ).all()
    
    # Créer un dictionnaire pour les remboursements
    refunds_map = {}
    for r in refunds_data:
        period_key = format_period(r.period, group_by)
        if period_key:
            refunds_map[period_key] = {
                "refunds_count": r.refunds_count or 0,
                "refund_amount": float(r.refund_amount or 0)
            }
    
    # Combiner les données
    result = []
    for row in sales_data:
        period_key = format_period(row.period, group_by)
        if not period_key:
            continue
            
        refund = refunds_map.get(period_key, {"refunds_count": 0, "refund_amount": 0.0})
        
        result.append({
            "period": period_key,
            "sales_count": row.sales_count or 0,
            "amount": float(row.amount or 0),
            "profit": float(row.profit or 0),
            "avg_ticket": float(row.avg_ticket or 0),
            "refunds_count": refund["refunds_count"],
            "refund_amount": refund["refund_amount"],
            "net_amount": float(row.amount or 0) - refund["refund_amount"]
        })
    
    return {
        "period_days": days,
        "group_by": group_by,
        "data": result
    }


@router.get("/top-products")
def get_top_products(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
    sort_by: str = Query("revenue", pattern="^(revenue|profit|quantity)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Top produits par revenu, profit ou quantité vendue
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Base query
    query = db.query(
        Product.id,
        Product.name,
        Product.category,
        Product.selling_price,
        Product.purchase_price,
        func.sum(SaleItem.quantity).label("total_sold"),
        func.sum(SaleItem.total_price).label("total_revenue"),
        func.sum(SaleItem.profit).label("total_profit")
    ).join(SaleItem, SaleItem.product_id == Product.id)\
     .join(Sale, SaleItem.sale_id == Sale.id)\
     .filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.payment_status == "PAID",
        Product.is_active == True
     ).group_by(
        Product.id, Product.name, Product.category, 
        Product.selling_price, Product.purchase_price
     )
    
    # Trier selon le critère
    if sort_by == "revenue":
        query = query.order_by(func.sum(SaleItem.total_price).desc())
    elif sort_by == "profit":
        query = query.order_by(func.sum(SaleItem.profit).desc())
    else:  # quantity
        query = query.order_by(func.sum(SaleItem.quantity).desc())
    
    top_products = query.limit(limit).all()
    
    result = []
    for row in top_products:
        # Calculer la marge
        revenue = float(row.total_revenue or 0)
        profit = float(row.total_profit or 0)
        margin = (profit / revenue * 100) if revenue > 0 else 0
        
        # Stock actuel
        current_stock = product_crud.calculate_current_stock(db, row.id)
        
        result.append({
            "id": row.id,
            "name": row.name,
            "category": row.category,
            "selling_price": float(row.selling_price),
            "purchase_price": float(row.purchase_price),
            "total_sold": row.total_sold or 0,
            "total_revenue": revenue,
            "total_profit": profit,
            "margin_percentage": float(margin),
            "current_stock": current_stock,
            "stock_status": product_crud.get_stock_status(current_stock, 10)  # threshold par défaut
        })
    
    return {
        "period_days": days,
        "sort_by": sort_by,
        "products": result
    }


@router.get("/client-insights")
def get_client_insights(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Insights sur les clients : meilleurs clients, fréquence d'achat, etc.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Meilleurs clients par CA
    top_clients = db.query(
        Client.id,
        Client.full_name,
        Client.phone,
        Client.email,
        Client.client_type,
        func.count(Sale.id).label("purchase_count"),
        func.sum(Sale.final_amount).label("total_spent"),
        func.avg(Sale.final_amount).label("avg_purchase"),
        func.max(Sale.sale_date).label("last_purchase")
    ).join(Sale, Sale.client_id == Client.id)\
     .filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.payment_status == "PAID"
     ).group_by(
        Client.id, Client.full_name, Client.phone, 
        Client.email, Client.client_type
     ).order_by(
        func.sum(Sale.final_amount).desc()
     ).limit(limit).all()
    
    # Clients inactifs (pas d'achat depuis 60 jours)
    sixty_days_ago = end_date - timedelta(days=60)
    inactive_clients = db.query(
        Client.id,
        Client.full_name,
        Client.phone,
        Client.last_purchase
    ).filter(
        Client.last_purchase < sixty_days_ago
    ).order_by(
        Client.last_purchase.desc()
    ).limit(limit).all()
    
    # Nouveaux clients
    new_clients = db.query(
        Client.id,
        Client.full_name,
        Client.phone,
        Client.created_at
    ).filter(
        Client.created_at >= start_date
    ).order_by(
        Client.created_at.desc()
    ).limit(limit).all()
    
    # Distribution par type de client
    client_type_distribution = db.query(
        Client.client_type,
        func.count(Client.id).label("count"),
        func.sum(Client.total_purchases).label("total_value")
    ).group_by(Client.client_type).all()
    
    return {
        "period_days": days,
        "top_clients": [
            {
                "id": row.id,
                "full_name": row.full_name,
                "phone": row.phone,
                "email": row.email,
                "client_type": row.client_type,
                "purchase_count": row.purchase_count or 0,
                "total_spent": float(row.total_spent or 0),
                "avg_purchase": float(row.avg_purchase or 0),
                "last_purchase": row.last_purchase
            }
            for row in top_clients
        ],
        "inactive_clients": [
            {
                "id": row.id,
                "full_name": row.full_name,
                "phone": row.phone,
                "last_purchase": row.last_purchase,
                "days_inactive": (end_date.date() - row.last_purchase.date()).days if row.last_purchase else None
            }
            for row in inactive_clients
        ],
        "new_clients": [
            {
                "id": row.id,
                "full_name": row.full_name,
                "phone": row.phone,
                "created_at": row.created_at
            }
            for row in new_clients
        ],
        "client_type_distribution": [
            {
                "client_type": row.client_type,
                "count": row.count,
                "total_value": float(row.total_value or 0)
            }
            for row in client_type_distribution
        ]
    }


@router.get("/inventory-alerts")
def get_inventory_alerts(
    threshold_percentage: float = Query(0.3, ge=0.1, le=1.0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    """
    Alertes d'inventaire : produits en rupture, stock faible, produits expirés
    """
    # Produits en rupture
    out_of_stock = []
    products = db.query(Product).filter(Product.is_active == True).all()
    
    for product in products:
        current_stock = product_crud.calculate_current_stock(db, product.id)
        if current_stock <= 0:
            out_of_stock.append({
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "current_stock": current_stock,
                "alert_threshold": product.alert_threshold,
                "status": "RUPTURE"
            })
    
    # Produits avec stock faible
    low_stock = product_crud.get_low_stock_products(db, threshold_percentage)
    
    # Produits expirant bientôt (30 jours)
    expiring_soon = product_crud.get_expiring_products(db, days=30)
    
    # Produits les plus vendus mais avec stock faible
    top_selling_low_stock = []
    top_products = db.query(
        Product.id,
        Product.name,
        func.sum(SaleItem.quantity).label("total_sold")
    ).join(SaleItem, SaleItem.product_id == Product.id)\
     .join(Sale, SaleItem.sale_id == Sale.id)\
     .filter(
        Sale.sale_date >= datetime.utcnow() - timedelta(days=30),
        Sale.payment_status == "PAID",
        Product.is_active == True
     ).group_by(Product.id, Product.name)\
      .order_by(func.sum(SaleItem.quantity).desc())\
      .limit(20).all()
    
    for product in top_products:
        current_stock = product_crud.calculate_current_stock(db, product.id)
        db_product = db.query(Product).filter(Product.id == product.id).first()
        if db_product and 0 < current_stock <= db_product.alert_threshold:
            top_selling_low_stock.append({
                "id": product.id,
                "name": product.name,
                "total_sold": product.total_sold or 0,
                "current_stock": current_stock,
                "alert_threshold": db_product.alert_threshold,
                "percentage": (current_stock / db_product.alert_threshold) * 100 if db_product.alert_threshold > 0 else 0
            })
    
    return {
        "out_of_stock": {
            "count": len(out_of_stock),
            "products": out_of_stock[:20]  # Limiter à 20
        },
        "low_stock": {
            "count": len(low_stock),
            "products": [
                {
                    "id": item["product"].id,
                    "name": item["product"].name,
                    "category": item["product"].category,
                    "current_stock": item["current_stock"],
                    "threshold": item["threshold"],
                    "percentage": item["percentage"],
                    "status": "ALERTE"
                }
                for item in low_stock[:20]
            ]
        },
        "expiring_soon": {
            "count": len(expiring_soon),
            "products": [
                {
                    "id": item["product"].id,
                    "name": item["product"].name,
                    "category": item["product"].category,
                    "expiration_date": item["expiration_date"],
                    "days_until_expiry": item["days_until_expiry"],
                    "current_stock": item["current_stock"]
                }
                for item in expiring_soon[:20]
            ]
        },
        "top_selling_low_stock": {
            "count": len(top_selling_low_stock),
            "products": top_selling_low_stock[:20]
        }
    }


@router.get("/performance-metrics")
def get_performance_metrics(
    period: str = Query("month", pattern="^(day|week|month|quarter|year)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Métriques de performance : taux de conversion, panier moyen, etc.
    """
    today = datetime.utcnow()
    
    # Définir la période
    if period == "day":
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == "month":
        start_date = today.replace(day=1)
        # Fin du mois
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    elif period == "quarter":
        quarter = (today.month - 1) // 3 + 1
        start_date = today.replace(month=(quarter - 1) * 3 + 1, day=1)
        if quarter == 4:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=quarter * 3 + 1, day=1) - timedelta(days=1)
    else:  # year
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    
    # =========================
    # VENTES
    # =========================
    sales_data = db.query(
        func.count(Sale.id).label("total_sales"),
        func.sum(Sale.final_amount).label("total_revenue"),
        func.sum(Sale.total_profit).label("total_profit"),
        func.avg(Sale.final_amount).label("avg_ticket"),
        func.sum(SaleItem.quantity).label("total_items")
    ).join(SaleItem, SaleItem.sale_id == Sale.id)\
     .filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.payment_status == "PAID"
     ).first()
    
    # =========================
    # CLIENTS
    # =========================
    clients_data = db.query(
        func.count(Client.id).label("total_clients"),
        func.count(distinct(Sale.client_id)).label("active_clients")
    ).outerjoin(Sale, Sale.client_id == Client.id).first()
    
    # Nouveaux clients
    new_clients = db.query(func.count(Client.id)).filter(
        Client.created_at >= start_date,
        Client.created_at <= end_date
    ).scalar() or 0
    
    # =========================
    # TAUX DE CONVERSION
    # =========================
    # Visites (approximatif - à intégrer avec un système de suivi)
    estimated_visits = sales_data.total_sales * 3  # Approximation
    
    conversion_rate = (sales_data.total_sales / estimated_visits * 100) if estimated_visits > 0 else 0
    
    # =========================
    # FRÉQUENCE D'ACHAT
    # =========================
    avg_purchase_frequency = None
    if clients_data.active_clients > 0:
        avg_purchase_frequency = sales_data.total_sales / clients_data.active_clients
    
    # =========================
    # VALEUR DU CYCLE DE VIE CLIENT
    # =========================
    total_revenue = sales_data.total_revenue or 0
    total_clients = clients_data.total_clients or 0

    avg_client_value = (
        total_revenue / total_clients
        if total_clients > 0
        else 0
    )

    # =========================
    # PRODUITS
    # =========================
    top_categories = db.query(
        Product.category,
        func.count(SaleItem.id).label("sales_count"),
        func.sum(SaleItem.total_price).label("revenue"),
        func.sum(SaleItem.profit).label("profit")
    ).join(SaleItem, SaleItem.product_id == Product.id)\
     .join(Sale, SaleItem.sale_id == Sale.id)\
     .filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.payment_status == "PAID"
     ).group_by(Product.category)\
      .order_by(func.sum(SaleItem.total_price).desc())\
      .limit(5).all()
    
    return {
        "period": {
            "type": period,
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "sales_metrics": {
            "total_sales": sales_data.total_sales or 0,
            "total_revenue": float(sales_data.total_revenue or 0),
            "total_profit": float(sales_data.total_profit or 0),
            "total_items": sales_data.total_items or 0,
            "avg_ticket": float(sales_data.avg_ticket or 0),
            "profit_margin": (float(sales_data.total_profit or 0) / float(sales_data.total_revenue or 1) * 100)
        },
        "client_metrics": {
            "total_clients": clients_data.total_clients or 0,
            "active_clients": clients_data.active_clients or 0,
            "new_clients": new_clients,
            "client_retention_rate": (clients_data.active_clients / clients_data.total_clients * 100) if clients_data.total_clients > 0 else 0
        },
        "performance_metrics": {
            "estimated_visits": estimated_visits,
            "conversion_rate": float(conversion_rate),
            "avg_purchase_frequency": float(avg_purchase_frequency) if avg_purchase_frequency else 0,
            "avg_client_value": float(avg_client_value) if avg_client_value else 0,
            "customer_lifetime_value": float(avg_client_value * 12) if avg_client_value else 0  # Estimation annuelle
        },
        "top_categories": [
            {
                "category": row.category,
                "sales_count": row.sales_count or 0,
                "revenue": float(row.revenue or 0),
                "profit": float(row.profit or 0),
                "profit_margin": (float(row.profit or 0) / float(row.revenue or 1) * 100) if row.revenue else 0
            }
            for row in top_categories
        ]
    }


@router.get("/realtime-updates")
def get_realtime_updates(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Mises à jour en temps réel pour le dashboard
    """
    try:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Ventes aujourd'hui
        today_sales = db.query(Sale).filter(
            Sale.sale_date >= today_start,
            Sale.payment_status == "PAID"
        ).count()
        
        today_revenue = db.query(func.sum(Sale.final_amount)).filter(
            Sale.sale_date >= today_start,
            Sale.payment_status == "PAID"
        ).scalar() or 0
        
        # Dernières ventes
        recent_sales = db.query(Sale).filter(
            Sale.payment_status == "PAID"
        ).order_by(Sale.sale_date.desc()).limit(5).all()
        
        recent_sales_data = []
        for sale in recent_sales:
            try:
                client_name = None
                if sale.client_id:
                    client = db.query(Client).filter(Client.id == sale.client_id).first()
                    client_name = client.full_name if client else None
                
                recent_sales_data.append({
                    "id": sale.id,
                    "invoice_number": sale.invoice_number,
                    "client_name": client_name,
                    "amount": float(sale.final_amount),
                    "time": sale.sale_date.strftime("%H:%M") if sale.sale_date else "N/A",
                    "payment_method": sale.payment_method
                })
            except Exception as e:
                logger.error(f"Error processing sale {sale.id}: {e}")
                continue
        
        # Rendez-vous aujourd'hui
        today_appointments = db.query(Appointment).filter(
            func.date(Appointment.appointment_date) == now.date()
        ).order_by(Appointment.appointment_date).limit(5).all()
        
        appointments_data = []
        for app in today_appointments:
            try:
                client = db.query(Client).filter(Client.id == app.client_id).first()
                
                appointments_data.append({
                    "id": app.id,
                    "client_name": client.full_name if client else "Client inconnu",
                    "service": app.service_type,
                    "time": app.appointment_date.strftime("%H:%M") if app.appointment_date else "N/A",
                    "status": app.status
                })
            except Exception as e:
                logger.error(f"Error processing appointment {app.id}: {e}")
                continue
        
        # Alertes de stock urgentes - OPTIMISÉE
        urgent_stock_alerts = []
        try:
            # Récupérer seulement les produits actifs avec stock faible
            products_with_low_stock = db.query(Product).filter(
                Product.is_active == True,
                Product.alert_threshold > 0
            ).all()
            
            for product in products_with_low_stock[:50]:  # Limiter à 50 produits pour performance
                try:
                    stock = product_crud.calculate_current_stock(db, product.id)
                    if stock is not None and stock > 0 and stock <= (product.alert_threshold or 10) / 2:
                        urgent_stock_alerts.append({
                            "product_id": product.id,
                            "product_name": product.name,
                            "current_stock": stock,
                            "threshold": product.alert_threshold or 10,
                            "urgency": "HAUTE"
                        })
                except Exception as e:
                    logger.error(f"Error calculating stock for product {product.id}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            # Continuer même si les alertes échouent
        
        # Si nous avons trop d'alertes, limiter
        if len(urgent_stock_alerts) > 10:
            urgent_stock_alerts = urgent_stock_alerts[:10]
        
        return {
            "timestamp": now.isoformat(),
            "today_sales": today_sales,
            "today_revenue": float(today_revenue),
            "recent_sales": recent_sales_data,
            "today_appointments": {
                "total": len(today_appointments),
                "upcoming": appointments_data
            },
            "urgent_alerts": {
                "stock_alerts": urgent_stock_alerts,
                "count": len(urgent_stock_alerts)
            }
        }
    
    except Exception as e:
        logger.error(f"Critical error in get_realtime_updates: {str(e)}", exc_info=True)
        # Retourner une réponse minimale pour éviter l'erreur 500
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "today_sales": 0,
            "today_revenue": 0.0,
            "recent_sales": [],
            "today_appointments": {
                "total": 0,
                "upcoming": []
            },
            "urgent_alerts": {
                "stock_alerts": [],
                "count": 0
            },
            "error": "Partial data loaded"
        }

# backend/routes/products.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models, schemas
from crud.product import product as product_crud
from typing import List, Optional
import shutil, os, uuid
from core.config import settings

router = APIRouter(prefix="/products", tags=["Produits"])

UPLOAD_DIR = os.path.join(settings.UPLOAD_DIR, "products")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ================================
# UTILS
# ================================
def compute_margin(purchase: float, selling: float) -> float:
    if purchase <= 0:
        return 0.0
    return round(((selling - purchase) / purchase) * 100, 2)

def compute_stock(db: Session, product_id: str) -> int:
    """Calcul du stock disponible pour un produit"""
    stock_in = db.query(
        func.coalesce(func.sum(models.StockMovement.quantity), 0)
    ).filter(
        models.StockMovement.product_id == product_id,
        models.StockMovement.movement_type == "IN"
    ).scalar()

    stock_out = db.query(
        func.coalesce(func.sum(models.StockMovement.quantity), 0)
    ).filter(
        models.StockMovement.product_id == product_id,
        models.StockMovement.movement_type == "OUT"
    ).scalar()

    return stock_in - stock_out

def stock_status(stock: int, threshold: int) -> str:
    if stock <= 0:
        return "RUPTURE"
    if stock <= threshold:
        return "ALERTE"
    return "EN_STOCK"

def enrich_product(db: Session, product: models.Product) -> schemas.ProductResponse:
    """Prépare la réponse produit avec stock et status"""
    stock = compute_stock(db, product.id)
    status = stock_status(stock, product.alert_threshold)
    
    # Créer un dictionnaire avec les données du produit
    product_dict = {
        key: getattr(product, key)
        for key in schemas.ProductResponse.__fields__.keys()
        if hasattr(product, key)
    }
    
    # Ajouter les champs calculés
    product_dict.update({
        "current_stock": stock,
        "stock_status": status
    })
    
    return schemas.ProductResponse(**product_dict)

# ================================
# CREATE PRODUCT
# ================================
@router.post("/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Crée un produit avec son stock initial - Utilise le CRUD dédié"""
    try:
        # Utiliser le CRUD qui gère déjà correctement la logique métier
        db_product = product_crud.create_with_stock(db=db, obj_in=product)
        
        # Récupérer le produit enrichi avec son stock via le CRUD
        product_data = product_crud.get_with_stock(db, db_product.id)
        
        if not product_data:
            raise HTTPException(500, "Erreur lors de la récupération du produit")
            
        return schemas.ProductResponse(**product_data)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Erreur lors de la création: {str(e)}")


# ================================
# READ PRODUCTS
# ================================
@router.get("/", response_model=List[schemas.ProductResponse])
def read_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    low_stock: bool = False,
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """Récupère la liste des produits - Utilise le CRUD"""
    try:
        products_data = product_crud.search(
            db=db,
            search=search,
            category=category,
            low_stock=low_stock,
            include_inactive=include_inactive
        )
        
        return [schemas.ProductResponse(**p) for p in products_data]
    except Exception as e:
        raise HTTPException(500, f"Erreur lors de la récupération: {str(e)}")


# ================================
# READ ONE PRODUCT
# ================================
@router.get("/{product_id}", response_model=schemas.ProductResponse)
def read_product(product_id: str, db: Session = Depends(get_db)):
    """Récupère un produit spécifique - Utilise le CRUD"""
    product_data = product_crud.get_with_stock(db, product_id)
    
    if not product_data:
        raise HTTPException(404, "Produit non trouvé")
    
    return schemas.ProductResponse(**product_data)


# ================================
# UPDATE PRODUCT
# ================================
@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: str,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not db_product:
        raise HTTPException(404, "Produit non trouvé")

    data = product.dict(exclude_unset=True, exclude={"quantity"})

    for key, value in data.items():
        setattr(db_product, key, value)

    if "purchase_price" in data or "selling_price" in data:
        # Calculer la marge
        db_product.margin = compute_margin(
            float(db_product.purchase_price),
            float(db_product.selling_price)
        )

    db.commit()
    db.refresh(db_product)

    return enrich_product(db, db_product)


# ================================
# SOFT DELETE
# ================================
@router.delete("/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_db)):

    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(404, "Produit non trouvé")

    product.is_active = False
    db.commit()

    return {"message": "Produit désactivé"}


# ================================
# IMAGE UPLOAD
# ================================
@router.post("/{product_id}/image")
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(404, "Produit non trouvé")

    # Vérifier taille max
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(400, "Fichier trop volumineux")
    
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as buffer:
        buffer.write(contents)

    # Ajouter au produit
    product.images = (product.images or []) + [filename]
    db.commit()

    return {"image": filename}

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


    def calculate_current_stock(self, db: Session, product_id: int) -> int:
        """Calcule le stock actuel d'un produit"""
        try:
            # Stock entrant (IN, ADJUSTMENT, RETURN)
            stock_in = db.query(func.coalesce(func.sum(StockMovement.quantity), 0))\
                .filter(
                    StockMovement.product_id == product_id,
                    StockMovement.movement_type.in_(["IN", "ADJUSTMENT", "RETURN"])
                ).scalar()
            
            # Stock sortant (OUT, DAMAGED)
            stock_out = db.query(func.coalesce(func.sum(StockMovement.quantity), 0))\
                .filter(
                    StockMovement.product_id == product_id,
                    StockMovement.movement_type.in_(["OUT", "DAMAGED"])
                ).scalar()
            
            return int(stock_in - stock_out)
        except Exception as e:
            # En cas d'erreur, retourner 0
            return 0

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


# backend\crud\sales_stats.py

from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, text
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from models import Sale, Client, Product, SaleItem  

class SalesStatsService:
    """
    Service spécialisé dans les statistiques de ventes
    """
    
    @staticmethod
    def get_monthly_sales(db: Session, months: int = 12) -> List[Dict[str, Any]]:
        """
        Statistiques mensuelles des ventes
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)
        
        # Requête optimisée avec group by mois
        monthly_stats = db.query(
            func.date_trunc('month', Sale.sale_date).label("month"),
            func.count(Sale.id).label("sale_count"),
            func.sum(Sale.final_amount).label("total_amount"),
            func.sum(Sale.total_profit).label("total_profit"),
            func.avg(Sale.final_amount).label("avg_ticket")
        ).filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
            Sale.payment_status == "PAID"
        ).group_by(
            func.date_trunc('month', Sale.sale_date)
        ).order_by(
            func.date_trunc('month', Sale.sale_date).desc()
        ).all()
        
        return [
            {
                "month": month.strftime("%Y-%m"),
                "sale_count": sale_count,
                "total_amount": float(total_amount or 0),
                "total_profit": float(total_profit or 0),
                "avg_ticket": float(avg_ticket or 0),
                "profit_margin": float((total_profit or 0) / (total_amount or 1) * 100)
            }
            for month, sale_count, total_amount, total_profit, avg_ticket in monthly_stats
        ]
    
    @staticmethod
    def get_sales_by_hour(db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """
        Analyse des ventes par heure de la journée
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        hourly_stats = db.query(
            extract('hour', Sale.sale_date).label("hour"),
            func.count(Sale.id).label("sale_count"),
            func.sum(Sale.final_amount).label("total_amount")
        ).filter(
            Sale.sale_date >= start_date,
            Sale.payment_status == "PAID"
        ).group_by(
            extract('hour', Sale.sale_date)
        ).order_by(
            extract('hour', Sale.sale_date)
        ).all()
        
        return [
            {
                "hour": int(hour),
                "sale_count": sale_count,
                "total_amount": float(total_amount or 0),
                "percentage": (sale_count / sum([h[1] for h in hourly_stats])) * 100 if hourly_stats else 0
            }
            for hour, sale_count, total_amount in hourly_stats
        ]
    
    @staticmethod
    def get_client_segmentation(db: Session) -> Dict[str, Any]:
        """
        Segmentation des clients par valeur
        """
        # Clients VIP (top 10%)
        vip_clients = db.query(Client)\
            .filter(Client.total_purchases > 0)\
            .order_by(Client.total_purchases.desc())\
            .limit(int(db.query(Client).count() * 0.1))\
            .all()
        
        # Clients réguliers (prochain 40%)
        regular_clients = db.query(Client)\
            .filter(
                Client.total_purchases > 0,
                Client.id.notin_([c.id for c in vip_clients])
            )\
            .order_by(Client.total_purchases.desc())\
            .limit(int(db.query(Client).count() * 0.4))\
            .all()
        
        # Clients occasionnels (reste)
        occasional_clients = db.query(Client)\
            .filter(
                Client.total_purchases > 0,
                Client.id.notin_([c.id for c in vip_clients + regular_clients])
            )\
            .all()
        
        return {
            "vip": {
                "count": len(vip_clients),
                "total_value": sum([float(c.total_purchases or 0) for c in vip_clients]),
                "avg_value": sum([float(c.total_purchases or 0) for c in vip_clients]) / len(vip_clients) if vip_clients else 0
            },
            "regular": {
                "count": len(regular_clients),
                "total_value": sum([float(c.total_purchases or 0) for c in regular_clients]),
                "avg_value": sum([float(c.total_purchases or 0) for c in regular_clients]) / len(regular_clients) if regular_clients else 0
            },
            "occasional": {
                "count": len(occasional_clients),
                "total_value": sum([float(c.total_purchases or 0) for c in occasional_clients]),
                "avg_value": sum([float(c.total_purchases or 0) for c in occasional_clients]) / len(occasional_clients) if occasional_clients else 0
            }
        }
    
    @staticmethod
    def get_product_performance_matrix(db: Session) -> List[Dict[str, Any]]:
        """
        Matrice de performance produit (rotation vs marge)
        """
        # Requête optimisée avec CTE
        product_stats = db.query(
            Product.id,
            Product.name,
            func.coalesce(func.sum(SaleItem.quantity), 0).label("total_sold"),
            func.coalesce(func.sum(SaleItem.profit), 0).label("total_profit"),
            func.coalesce(func.avg(Product.margin), 0).label("avg_margin")
        ).outerjoin(SaleItem, SaleItem.product_id == Product.id)\
         .outerjoin(Sale, SaleItem.sale_id == Sale.id)\
         .filter(
            Product.is_active == True,
            Sale.payment_status == "PAID"
         )\
         .group_by(Product.id, Product.name)\
         .all()
        
        # Calculer les quartiles pour classification
        quantities = [p[2] for p in product_stats if p[2] > 0]
        margins = [float(p[4]) for p in product_stats if p[4] > 0]
        
        if quantities:
            q1_qty = sorted(quantities)[len(quantities) // 4]
            q3_qty = sorted(quantities)[3 * len(quantities) // 4]
        else:
            q1_qty = q3_qty = 0
        
        if margins:
            q1_margin = sorted(margins)[len(margins) // 4]
            q3_margin = sorted(margins)[3 * len(margins) // 4]
        else:
            q1_margin = q3_margin = 0
        
        # Classification
        classified_products = []
        for product_id, name, total_sold, total_profit, avg_margin in product_stats:
            avg_margin_float = float(avg_margin or 0)
            
            if total_sold > q3_qty and avg_margin_float > q3_margin:
                category = "STARS"
            elif total_sold > q3_qty and avg_margin_float <= q3_margin:
                category = "CASH_COWS"
            elif total_sold <= q3_qty and avg_margin_float > q3_margin:
                category = "QUESTION_MARKS"
            else:
                category = "DOGS"
            
            classified_products.append({
                "product_id": product_id,
                "name": name,
                "total_sold": int(total_sold),
                "total_profit": float(total_profit or 0),
                "avg_margin": avg_margin_float,
                "category": category,
                "revenue_per_unit": float(total_profit or 0) / total_sold if total_sold > 0 else 0
            })
        
        return classified_products
    
    @staticmethod
    def get_sales_forecast(db: Session, days: int = 90) -> Dict[str, Any]:
        """
        Prévision des ventes basée sur les données historiques
        """
        from datetime import date
        import statistics
        
        # Données historiques
        historical_data = db.query(
            func.date(Sale.sale_date).label("sale_date"),
            func.sum(Sale.final_amount).label("daily_amount")
        ).filter(
            Sale.sale_date >= date.today() - timedelta(days=days * 2),
            Sale.payment_status == "PAID"
        ).group_by(
            func.date(Sale.sale_date)
        ).all()
        
        if not historical_data:
            return {"forecast": [], "confidence": 0}
        
        # Prévision simple (moyenne mobile sur 7 jours)
        daily_amounts = [float(amount) for _, amount in historical_data[-7:]]
        
        if len(daily_amounts) < 7:
            forecast_value = statistics.mean(daily_amounts) if daily_amounts else 0
        else:
            forecast_value = statistics.mean(daily_amounts)
        
        # Calcul de la confiance
        if len(daily_amounts) >= 7:
            confidence = min(95, (len(daily_amounts) / 30) * 100)
        else:
            confidence = max(30, (len(daily_amounts) / 7) * 50)
        
        # Générer les prévisions pour les 30 prochains jours
        forecasts = []
        for i in range(1, 31):
            forecast_date = date.today() + timedelta(days=i)
            
            # Ajustement par jour de la semaine (si assez de données)
            weekday_avg = 1.0
            if len(historical_data) >= 30:
                same_weekday_data = [
                    float(amount) for d, amount in historical_data 
                    if d.weekday() == forecast_date.weekday()
                ]
                if same_weekday_data:
                    weekday_avg = statistics.mean(same_weekday_data) / forecast_value
        
            forecasts.append({
                "date": forecast_date.isoformat(),
                "forecast_amount": forecast_value * weekday_avg,
                "confidence": confidence * (1 - (i / 30 * 0.5))  # Décroissance de la confiance
            })
        
        return {
            "forecast": forecasts,
            "confidence": confidence,
            "historical_days": len(historical_data),
            "current_trend": "stable" if len(daily_amounts) < 2 else 
                            "up" if daily_amounts[-1] > daily_amounts[-2] else "down"
        }


# Singleton
sales_stats = SalesStatsService()

# backend/crud/sale_service.py
"""
Service complet de gestion des ventes et remboursements
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid
import logging

from models import Sale, SaleItem, Refund, RefundItem, Product, Client, StockMovement, Payment
from schemas import SaleCreate, RefundCreate, RefundApprove, RefundProcess
from crud.product import product as product_crud
from core.exceptions import (
    NotFoundException,
    InsufficientStockException,
    BusinessLogicException,
    ValidationException
)

logger = logging.getLogger(__name__)


class SaleRefundService:
    """Service unifié pour la gestion des ventes et remboursements"""
    
    # =========================
    # VENTES
    # =========================
    
    @staticmethod
    def generate_invoice_number() -> str:
        """Génère un numéro de facture unique"""
        date_str = datetime.utcnow().strftime("%Y%m%d")
        unique_id = uuid.uuid4().hex[:6].upper()
        return f"FACT-{date_str}-{unique_id}"
    
    @staticmethod
    def generate_refund_number() -> str:
        """Génère un numéro de remboursement unique"""
        date_str = datetime.utcnow().strftime("%Y%m%d")
        unique_id = uuid.uuid4().hex[:6].upper()
        return f"REM-{date_str}-{unique_id}"
    
    @staticmethod
    def create_sale(db: Session, sale_data: SaleCreate, user_id: str = None) -> Dict[str, Any]:
        """
        Crée une vente complète de manière transactionnelle
        """
        if not sale_data.items or len(sale_data.items) == 0:
            raise BusinessLogicException("La vente doit contenir au moins un produit")
        
        try:
            # Démarrer une transaction
            with db.begin():
                # Récupérer et verrouiller les produits
                product_ids = [item.product_id for item in sale_data.items]
                products = db.query(Product).filter(
                    Product.id.in_(product_ids)
                ).with_for_update().all()
                
                if len(products) != len(product_ids):
                    found_ids = [p.id for p in products]
                    missing = set(product_ids) - set(found_ids)
                    raise NotFoundException("Produit", list(missing)[0])
                
                products_map = {p.id: p for p in products}
                
                # Validation et calculs - utiliser des entiers
                items_data = []
                total_amount = 0
                total_cost = 0
                total_profit = 0
                total_tax = sale_data.tax_amount or 0
                total_shipping = sale_data.shipping_cost or 0
                
                for item in sale_data.items:
                    product = products_map[item.product_id]
                    
                    # Vérifier le stock
                    current_stock = product_crud.calculate_current_stock(db, product.id)
                    if current_stock < item.quantity:
                        raise InsufficientStockException(
                            product.name, current_stock, item.quantity
                        )
                    
                    # Convertir les Decimal en int
                    unit_price = int(item.unit_price) if item.unit_price is not None else int(product.selling_price)
                    purchase_price = int(product.purchase_price)
                    line_discount = item.discount or 0
                    
                    # Calculs de la ligne en entiers
                    line_total = (unit_price * item.quantity) - line_discount
                    line_cost = purchase_price * item.quantity
                    line_profit = line_total - line_cost - line_discount
                    
                    items_data.append({
                        "product": product,
                        "quantity": item.quantity,
                        "unit_price": unit_price,
                        "purchase_price": purchase_price,
                        "line_discount": line_discount,
                        "line_total": line_total,
                        "line_cost": line_cost,
                        "line_profit": line_profit
                    })
                    
                    total_amount += line_total
                    total_cost += line_cost
                    total_profit += line_profit
                
                # Appliquer la remise globale
                discount = sale_data.discount or 0
                if discount > total_amount:
                    raise BusinessLogicException("La remise ne peut pas dépasser le montant total")
                
                final_amount = total_amount - discount + total_tax + total_shipping
                
                # Vérifier le client
                client = None
                if sale_data.client_id:
                    client = db.query(Client).filter(Client.id == sale_data.client_id).first()
                    if not client:
                        raise NotFoundException("Client", sale_data.client_id)
                
                # Créer la vente - tous les champs en entiers
                invoice_number = SaleRefundService.generate_invoice_number()
                db_sale = Sale(
                    client_id=sale_data.client_id,
                    invoice_number=invoice_number,
                    total_amount=total_amount,
                    discount=discount,
                    tax_amount=total_tax,
                    shipping_cost=total_shipping,
                    final_amount=final_amount,
                    payment_method=sale_data.payment_method,
                    payment_status="PAID",
                    total_profit=total_profit,
                    total_cost=total_cost,
                    notes=sale_data.notes,
                    sale_date=datetime.utcnow(),
                    cashier_id=user_id
                )
                
                db.add(db_sale)
                db.flush()
                
                # Créer les lignes de vente
                for item_data in items_data:
                    sale_item = SaleItem(
                        sale_id=db_sale.id,
                        product_id=item_data["product"].id,
                        quantity=item_data["quantity"],
                        unit_price=item_data["unit_price"],
                        purchase_price=item_data["purchase_price"],
                        discount=item_data["line_discount"],
                        total_price=item_data["line_total"],
                        cost=item_data["line_cost"],
                        profit=item_data["line_profit"]
                    )
                    db.add(sale_item)
                    
                    # Mouvement de stock
                    movement = StockMovement(
                        product_id=item_data["product"].id,
                        movement_type="OUT",
                        quantity=item_data["quantity"],
                        unit_cost=item_data["purchase_price"],
                        total_cost=item_data["line_cost"],
                        reason="VENTE",
                        reference=invoice_number,
                        movement_date=datetime.utcnow()
                    )
                    db.add(movement)
                
                # Mettre à jour le client
                if client:
                    # Convertir le Decimal en int
                    client_total = int(client.total_purchases) if client.total_purchases else 0
                    client.total_purchases = client_total + final_amount
                    client.last_purchase = datetime.utcnow()
                    
                    # Points de fidélité (1 point par 1000 FCFA)
                    points_to_add = final_amount // 1000
                    client.loyalty_points = (client.loyalty_points or 0) + points_to_add
                    
                    # Mise à jour du type de client
                    if client.total_purchases > 1000000:
                        client.client_type = "VIP"
                    elif client.total_purchases > 500000:
                        client.client_type = "FIDELITE"
                
                # Créer le paiement
                payment = Payment(
                    sale_id=db_sale.id,
                    amount=final_amount,
                    payment_method=sale_data.payment_method,
                    payment_date=datetime.utcnow(),
                    status="COMPLETED",
                    reference=invoice_number
                )
                db.add(payment)
            
            # Récupérer les détails de la vente créée
            return SaleRefundService.get_sale_details(db, db_sale.id)
                
        except Exception as e:
            logger.error(f"Erreur création vente: {str(e)}")
            raise BusinessLogicException(f"Erreur lors de la création de la vente: {str(e)}")
        
    @staticmethod
    def get_sale_details(db: Session, sale_id: str) -> Dict[str, Any]:
        """Récupère les détails complets d'une vente"""
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            raise NotFoundException("Vente", sale_id)
        
        items = db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()
        payments = db.query(Payment).filter(Payment.sale_id == sale_id).all()
        refunds = db.query(Refund).filter(Refund.sale_id == sale_id).all()
        
        item_details = []
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            # Convertir Decimal en int
            unit_price = int(item.unit_price) if item.unit_price else 0
            purchase_price = int(item.purchase_price) if item.purchase_price else 0
            
            item_details.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": product.name if product else "Produit inconnu",
                "sku": product.sku if product else None,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "purchase_price": purchase_price,
                "discount": int(item.discount) if item.discount else 0,
                "total_price": int(item.total_price) if item.total_price else 0,
                "cost": int(item.cost) if item.cost else 0,
                "profit": int(item.profit) if item.profit else 0,
                "margin": ((unit_price - purchase_price) / purchase_price * 100) if purchase_price > 0 else 0
            })
        
        payment_details = []
        for payment in payments:
            payment_details.append({
                "id": payment.id,
                "amount": int(payment.amount) if payment.amount else 0,
                "method": payment.payment_method,
                "date": payment.payment_date,
                "status": payment.status,
                "reference": payment.reference
            })
        
        refund_details = []
        total_refunded = 0
        for refund in refunds:
            refund_amount = int(refund.refund_amount) if refund.refund_amount else 0
            refund_details.append({
                "id": refund.id,
                "refund_number": refund.refund_number,
                "amount": refund_amount,
                "status": refund.refund_status,
                "date": refund.refund_date
            })
            total_refunded += refund_amount
        
        client_name = None
        if sale.client_id:
            client = db.query(Client).filter(Client.id == sale.client_id).first()
            client_name = client.full_name if client else None
        
        # Convertir tous les champs Decimal en int
        sale_total_amount = int(sale.total_amount) if sale.total_amount else 0
        sale_total_cost = int(sale.total_cost) if sale.total_cost else 0
        sale_discount = int(sale.discount) if sale.discount else 0
        sale_tax_amount = int(sale.tax_amount) if sale.tax_amount else 0
        sale_shipping_cost = int(sale.shipping_cost) if sale.shipping_cost else 0
        sale_final_amount = int(sale.final_amount) if sale.final_amount else 0
        sale_total_profit = int(sale.total_profit) if sale.total_profit else 0
        
        return {
            "id": sale.id,
            "invoice_number": sale.invoice_number,
            "client_id": sale.client_id,
            "client_name": client_name,
            "sale_date": sale.sale_date,
            "cashier_id": sale.cashier_id,
            "total_amount": sale_total_amount,
            "total_cost": sale_total_cost,
            "discount": sale_discount,
            "tax_amount": sale_tax_amount,
            "shipping_cost": sale_shipping_cost,
            "final_amount": sale_final_amount,
            "payment_method": sale.payment_method,
            "payment_status": sale.payment_status,
            "total_profit": sale_total_profit,
            "margin_percentage": (sale_total_profit / sale_total_amount * 100) if sale_total_amount > 0 else 0,
            "notes": sale.notes,
            "items": item_details,
            "payments": payment_details,
            "refunds": refund_details,
            "total_refunded": total_refunded,
            "remaining_refundable": sale_final_amount - total_refunded,
            "is_refundable": sale.is_refundable,
            "created_at": sale.created_at
        }
    
    # =========================
    # REMBOURSEMENTS
    # =========================
    
    @staticmethod
    def validate_refund_eligibility(db: Session, sale_id: str, refund_amount: float) -> Tuple[Sale, float]:
        """Valide l'éligibilité d'une vente au remboursement"""
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            raise NotFoundException("Vente", sale_id)
        
        if not sale.is_refundable:
            raise BusinessLogicException("Cette vente n'est pas éligible au remboursement")
        
        # Vérifier la date limite
        if sale.refund_deadline and datetime.utcnow() > sale.refund_deadline:
            raise BusinessLogicException("La période de remboursement est expirée")
        
        # Calculer le montant déjà remboursé
        total_refunded = db.query(func.coalesce(func.sum(Refund.refund_amount), 0)).filter(
            Refund.sale_id == sale_id,
            Refund.refund_status.in_(["APPROVED", "COMPLETED"])
        ).scalar()
        
        remaining = float(sale.final_amount) - float(total_refunded)
        
        if refund_amount > remaining:
            raise BusinessLogicException(
                f"Montant trop élevé. Maximum remboursable: {remaining:.2f} €"
            )
        
        return sale, remaining
    
    @staticmethod
    def create_refund(db: Session, sale_id: str, refund_data: RefundCreate, user_id: str) -> Dict[str, Any]:
        """Crée un remboursement"""
        # Validation
        sale, max_refundable = SaleRefundService.validate_refund_eligibility(
            db, sale_id, float(refund_data.refund_amount)
        )
        
        try:
            with db.begin():
                # Créer le remboursement
                refund_number = SaleRefundService.generate_refund_number()
                is_partial = float(refund_data.refund_amount) < float(sale.final_amount)
                
                refund = Refund(
                    sale_id=sale_id,
                    refund_number=refund_number,
                    refund_amount=refund_data.refund_amount,
                    refund_reason=refund_data.refund_reason.value,
                    refund_method=refund_data.refund_method.value,
                    refund_status="PENDING",
                    is_partial=is_partial,
                    notes=refund_data.notes,
                    approved_by=user_id if user_id else None
                )
                
                db.add(refund)
                db.flush()
                
                # Traiter les articles remboursés
                total_refund_calc = 0.0
                for item in refund_data.items:
                    sale_item = db.query(SaleItem).filter(SaleItem.id == item.sale_item_id).first()
                    if not sale_item:
                        raise NotFoundException("Article de vente", item.sale_item_id)
                    
                    # Vérifier la quantité
                    if item.quantity > sale_item.quantity:
                        raise BusinessLogicException(
                            f"Quantité invalide pour l'article {sale_item.product.name}"
                        )
                    
                    refund_item = RefundItem(
                        refund_id=refund.id,
                        sale_item_id=item.sale_item_id,
                        product_id=sale_item.product_id,
                        quantity=item.quantity,
                        refund_price=item.refund_price,
                        reason=item.reason,
                        restocked=item.restocked
                    )
                    
                    db.add(refund_item)
                    total_refund_calc += float(item.refund_price) * item.quantity
                    
                    # Retour en stock si demandé
                    if item.restocked:
                        product = db.query(Product).filter(Product.id == sale_item.product_id).first()
                        if product:
                            movement = StockMovement(
                                product_id=product.id,
                                movement_type="IN",
                                quantity=item.quantity,
                                unit_cost=float(sale_item.purchase_price),
                                total_cost=float(sale_item.purchase_price) * item.quantity,
                                reason="RETOUR_CLIENT",
                                reference=refund_number,
                                movement_date=datetime.utcnow(),
                                notes=f"Remboursement: {refund_number}"
                            )
                            db.add(movement)
                
                # Vérifier la correspondance des montants
                if abs(float(refund_data.refund_amount) - total_refund_calc) > 0.01:
                    raise BusinessLogicException(
                        f"Montant calculé ({total_refund_calc:.2f} €) ≠ montant déclaré ({refund_data.refund_amount} €)"
                    )
                
                # Mettre à jour la vente
                total_refunded = db.query(func.coalesce(func.sum(Refund.refund_amount), 0)).filter(
                    Refund.sale_id == sale_id,
                    Refund.refund_status.in_(["APPROVED", "COMPLETED"])
                ).scalar()
                
                sale.refunded_amount = total_refunded + float(refund_data.refund_amount)
                
                # Si remboursement total, marquer comme non remboursable
                if not is_partial:
                    sale.is_refundable = False
                
                # Ajuster les points de fidélité
                if sale.client_id:
                    client = db.query(Client).filter(Client.id == sale.client_id).first()
                    if client and client.loyalty_points > 0:
                        points_to_remove = int(
                            (float(refund_data.refund_amount) / float(sale.final_amount)) * 
                            (sale.final_amount // 1000)
                        )
                        client.loyalty_points = max(0, client.loyalty_points - points_to_remove)
                
                db.commit()
                
                return SaleRefundService.get_refund_details(db, refund.id)
                
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur création remboursement: {str(e)}")
            raise BusinessLogicException(f"Erreur lors du remboursement: {str(e)}")
    
    @staticmethod
    def get_refund_details(db: Session, refund_id: str) -> Dict[str, Any]:
        """Récupère les détails d'un remboursement"""
        refund = db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise NotFoundException("Remboursement", refund_id)
        
        sale = refund.sale
        items = []
        
        for item in refund.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            sale_item = item.sale_item
            
            items.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": product.name if product else "Produit inconnu",
                "sku": product.sku if product else None,
                "quantity": item.quantity,
                "refund_price": float(item.refund_price),
                "original_price": float(sale_item.unit_price) if sale_item else 0,
                "price_difference": float(sale_item.unit_price) - float(item.refund_price) if sale_item else 0,
                "reason": item.reason,
                "restocked": item.restocked
            })
        
        return {
            "id": refund.id,
            "refund_number": refund.refund_number,
            "sale_id": refund.sale_id,
            "invoice_number": sale.invoice_number,
            "refund_date": refund.refund_date,
            "refund_amount": float(refund.refund_amount),
            "refund_reason": refund.refund_reason,
            "refund_method": refund.refund_method,
            "refund_status": refund.refund_status,
            "is_partial": refund.is_partial,
            "approved_by": refund.approved_by,
            "approved_at": refund.approved_at,
            "notes": refund.notes,
            "items": items,
            "created_at": refund.created_at,
            "sale_total": float(sale.final_amount),
            "already_refunded": float(sale.refunded_amount),
            "remaining_refundable": float(sale.final_amount) - float(sale.refunded_amount),
            "client_name": sale.client.full_name if sale.client else None,
            "client_id": sale.client_id
        }
    
    @staticmethod
    def approve_refund(db: Session, refund_id: str, approve_data: RefundApprove, user_id: str) -> Dict[str, Any]:
        """Approuve un remboursement"""
        refund = db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise NotFoundException("Remboursement", refund_id)
        
        if refund.refund_status != "PENDING":
            raise BusinessLogicException(f"Le remboursement est déjà {refund.refund_status.lower()}")
        
        refund.refund_status = "APPROVED" if approve_data.approved else "REJECTED"
        refund.approved_by = user_id
        refund.approved_at = datetime.utcnow()
        
        if approve_data.notes:
            refund.notes = f"{refund.notes or ''}\n{approve_data.notes}"
        
        db.commit()
        
        return SaleRefundService.get_refund_details(db, refund.id)
    
    @staticmethod
    def process_refund(db: Session, refund_id: str, process_data: RefundProcess, user_id: str) -> Dict[str, Any]:
        """Traite un remboursement (exécute le paiement)"""
        refund = db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise NotFoundException("Remboursement", refund_id)
        
        if refund.refund_status != "APPROVED":
            raise BusinessLogicException("Le remboursement doit être approuvé avant traitement")
        
        refund.refund_status = "COMPLETED"
        
        if process_data.transaction_id:
            refund.notes = f"{refund.notes or ''}\nTransaction: {process_data.transaction_id}"
        
        if process_data.bank_reference:
            refund.notes = f"{refund.notes or ''}\nRéférence bancaire: {process_data.bank_reference}"
        
        if process_data.notes:
            refund.notes = f"{refund.notes or ''}\n{process_data.notes}"
        
        # Créer un paiement pour le remboursement
        payment = Payment(
            sale_id=refund.sale_id,
            amount=-float(refund.refund_amount),  # Montant négatif pour un remboursement
            payment_method=refund.refund_method,
            payment_date=datetime.utcnow(),
            status="COMPLETED",
            reference=f"REFUND-{refund.refund_number}",
            notes=f"Remboursement {refund.refund_number}"
        )
        db.add(payment)
        
        db.commit()
        
        return SaleRefundService.get_refund_details(db, refund.id)
    
    # =========================
    # STATISTIQUES ET RAPPORTS
    # =========================
    
    @staticmethod
    def get_daily_sales(db: Session, date: datetime = None) -> Dict[str, Any]:
        """Calcule les ventes du jour"""
        if date is None:
            date = datetime.utcnow()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        sales = db.query(Sale).filter(
            Sale.sale_date >= start_of_day,
            Sale.sale_date <= end_of_day,
            Sale.payment_status == "PAID"
        ).all()
        
        total_amount = sum(float(s.final_amount) for s in sales)
        total_cost = sum(float(s.total_cost or 0) for s in sales)
        total_profit = sum(float(s.total_profit) for s in sales)
        
        total_items = 0
        for sale in sales:
            items_count = db.query(func.sum(SaleItem.quantity))\
                .filter(SaleItem.sale_id == sale.id)\
                .scalar() or 0
            total_items += items_count
        
        return {
            "date": date.date().isoformat(),
            "total_sales": len(sales),
            "total_amount": total_amount,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "total_items": total_items,
            "average_ticket": total_amount / len(sales) if sales else 0,
            "margin_percentage": (total_profit / total_amount * 100) if total_amount > 0 else 0
        }
    
    @staticmethod
    def get_sales_period(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyse des ventes sur une période"""
        sales = db.query(Sale).filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
            Sale.payment_status == "PAID"
        ).all()
        
        # Statistiques de base
        stats = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_sales": len(sales),
            "total_amount": sum(float(s.final_amount) for s in sales),
            "total_cost": sum(float(s.total_cost or 0) for s in sales),
            "total_profit": sum(float(s.total_profit) for s in sales),
            "total_refunded": 0,
            "net_amount": 0
        }
        
        # Calculer les remboursements
        refunds = db.query(Refund).filter(
            Refund.refund_status.in_(["APPROVED", "COMPLETED"]),
            Refund.created_at >= start_date,
            Refund.created_at <= end_date
        ).all()
        
        stats["total_refunded"] = sum(float(r.refund_amount) for r in refunds)
        stats["net_amount"] = stats["total_amount"] - stats["total_refunded"]
        
        # Par méthode de paiement
        payment_methods = {}
        for sale in sales:
            method = sale.payment_method
            if method not in payment_methods:
                payment_methods[method] = {
                    "count": 0,
                    "amount": 0.0
                }
            payment_methods[method]["count"] += 1
            payment_methods[method]["amount"] += float(sale.final_amount)
        
        stats["payment_methods"] = payment_methods
        
        # Top produits
        top_products = db.query(
            Product.id,
            Product.name,
            func.sum(SaleItem.quantity).label("total_sold"),
            func.sum(SaleItem.total_price).label("total_revenue"),
            func.sum(SaleItem.profit).label("total_profit")
        ).join(SaleItem, SaleItem.product_id == Product.id)\
         .join(Sale, SaleItem.sale_id == Sale.id)\
         .filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
            Sale.payment_status == "PAID"
         ).group_by(Product.id, Product.name)\
          .order_by(func.sum(SaleItem.quantity).desc())\
          .limit(10).all()
        
        stats["top_products"] = [
            {
                "id": row.id,
                "name": row.name,
                "total_sold": row.total_sold or 0,
                "total_revenue": float(row.total_revenue or 0),
                "total_profit": float(row.total_profit or 0)
            }
            for row in top_products
        ]
        
        # Tendances quotidiennes
        daily_trends = db.query(
            func.date(Sale.sale_date).label("date"),
            func.count(Sale.id).label("count"),
            func.sum(Sale.final_amount).label("amount"),
            func.sum(Sale.total_profit).label("profit")
        ).filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
            Sale.payment_status == "PAID"
        ).group_by(func.date(Sale.sale_date))\
         .order_by(func.date(Sale.sale_date)).all()
        
        stats["daily_trends"] = [
            {
                "date": str(row.date),
                "sales_count": row.count or 0,
                "amount": float(row.amount or 0),
                "profit": float(row.profit or 0)
            }
            for row in daily_trends
        ]
        
        return stats
    
    @staticmethod
    def get_refund_stats(db: Session, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Statistiques des remboursements"""
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.utcnow()
        
        query = db.query(Refund).filter(
            Refund.created_at >= start_date,
            Refund.created_at <= end_date
        )
        
        # Statistiques de base
        total_refunds = query.count()
        total_refund_amount = query.with_entities(
            func.coalesce(func.sum(Refund.refund_amount), 0)
        ).scalar()
        
        # Par statut
        by_status = db.query(
            Refund.refund_status,
            func.count(Refund.id).label("count"),
            func.sum(Refund.refund_amount).label("amount")
        ).filter(
            Refund.created_at >= start_date,
            Refund.created_at <= end_date
        ).group_by(Refund.refund_status).all()
        
        # Par raison
        by_reason = db.query(
            Refund.refund_reason,
            func.count(Refund.id).label("count"),
            func.sum(Refund.refund_amount).label("amount")
        ).filter(
            Refund.created_at >= start_date,
            Refund.created_at <= end_date,
            Refund.refund_status.in_(["APPROVED", "COMPLETED"])
        ).group_by(Refund.refund_reason)\
         .order_by(func.count(Refund.id).desc())\
         .limit(10).all()
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_refunds": total_refunds,
            "total_refund_amount": float(total_refund_amount),
            "avg_refund_amount": float(total_refund_amount / total_refunds if total_refunds > 0 else 0),
            "by_status": {
                status: {
                    "count": count,
                    "amount": float(amount or 0)
                }
                for status, count, amount in by_status
            },
            "top_reasons": [
                {
                    "reason": reason,
                    "count": count,
                    "amount": float(amount or 0)
                }
                for reason, count, amount in by_reason
            ]
        }


# Instance singleton
sale_refund_service = SaleRefundService()


# backend\core\config.py
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # ===== Environnement =====
    ENVIRONMENT: str = "development"
    DEV_MODE: bool = True
    DEBUG: bool = True
    
    # ===== Database =====
    DATABASE_URL: str = "sqlite:///./che_prince_garba.db"  # Utilisez la DB principale
    
    APP_NAME: str = "Luxe Beauté Management"
    APP_VERSION: str = "2.0.0"
    
    # ===== Uploads =====
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # ===== JWT =====
    SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ===== CORS =====
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",  # Ajouter cette alternative
        "http://localhost:5173",   # Vite par défaut
    ]
    
    # ===== Développement =====
    DEV_TOKEN: Optional[str] = "fake-token-admin"  # Défaut pour le dev
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"

settings = Settings()

# backend\core\constants.py

"""
Constantes globales de l'application
"""

# Types de paiement
PAYMENT_METHODS = {
    "CASH": "Espèces",
    "MOBILE_MONEY": "Saraly",
    "CARD": "Carte Bancaire",
    "BANK_TRANSFER": "Virement Bancaire",
    "CHECK": "Chèque"
}

# Statuts de vente
SALE_STATUS = {
    "PENDING": "En attente",
    "PAID": "Payé",
    "PARTIAL": "Partiel",
    "CANCELLED": "Annulé",
    "REFUNDED": "Remboursé"
}

# Statuts de remboursement
REFUND_STATUS = {
    "PENDING": "En attente",
    "APPROVED": "Approuvé",
    "COMPLETED": "Traité",
    "CANCELLED": "Annulé",
    "REJECTED": "Rejeté"
}

# Types de mouvement de stock
STOCK_MOVEMENT_TYPES = {
    "IN": "Entrée",
    "OUT": "Sortie",
    "ADJUSTMENT": "Ajustement",
    "RETURN": "Retour",
    "DAMAGED": "Détérioré"
}

# Rôles utilisateur
USER_ROLES = {
    "ADMIN": "Administrateur",
    "MANAGER": "Gestionnaire",
    "CASHIER": "Caissier",
    "STOCK_MANAGER": "Gestionnaire Stock",
    "BEAUTICIAN": "Esthéticienne"
}

# Catégories de produits
PRODUCT_CATEGORIES = [
    "Soins Visage",
    "Soins Corps",
    "Maquillage",
    "Parfums",
    "Accessoires",
    "Homme",
    "Femme",
    "Enfant",
    "Professionnel"
]

# Marques populaires
BRANDS = [
    "Chanel", "Dior", "Estée Lauder", "Lancôme", "Clarins",
    "La Roche-Posay", "Vichy", "Nuxe", "Yves Rocher", "L'Oréal"
]

# Villes de Côte d'Ivoire
CITIES_CI = [
    "Abidjan", "Yamoussoukro", "Bouaké", "Daloa", "San-Pédro",
    "Korhogo", "Man", "Gagnoa", "Abengourou", "Bondoukou"
]

# Limites de l'application
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_ITEMS_PER_SALE = 50
MAX_SEARCH_RESULTS = 1000
SESSION_TIMEOUT_MINUTES = 30

# Paramètres de fidélité
LOYALTY_POINTS_PER_AMOUNT = 1000  # 1 point par 1000 FCFA
LOYALTY_LEVELS = {
    "BRONZE": 0,
    "SILVER": 10000,
    "GOLD": 50000,
    "PLATINUM": 200000
}

#backend\core\dev_config.py
"""
Configuration spécifique au développement
"""
from typing import Dict, Any, List
from core.config import settings

class DevConfig:
    """Configuration pour le mode développement"""
    
    # Token de développement accepté
    DEV_TOKENS = {
        "admin": "fake-token-admin",
        "manager": "fake-token-manager", 
        "cashier": "fake-token-cashier",
        "stock": "fake-token-stock"
    }
    
    # Utilisateurs de développement
    DEV_USERS = [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@luxe-beaute.fr",
            "full_name": "Administrateur",
            "role": "ADMIN",
            "permissions": ["all"]
        },
        {
            "id": 2,
            "username": "manager",
            "email": "manager@luxe-beaute.fr",
            "full_name": "Responsable",
            "role": "MANAGER",
            "permissions": ["view_dashboard", "manage_products", "manage_sales", "manage_clients"]
        },
        {
            "id": 3,
            "username": "cashier",
            "email": "cashier@luxe-beaute.fr",
            "full_name": "Caissier",
            "role": "CASHIER",
            "permissions": ["view_dashboard", "manage_sales", "view_products"]
        }
    ]
    
    # Routes exemptées d'authentification en dev
    DEV_EXEMPT_ROUTES = [
        "/api/v1/dashboard/stats",
        "/api/v1/dashboard/sales-trend",
        "/api/v1/dashboard/inventory-alerts",
        "/api/v1/dashboard/realtime-updates"
    ]
    
    @classmethod
    def get_dev_user(cls, user_id: int = None, username: str = None):
        """Récupère un utilisateur de développement"""
        if user_id:
            for user in cls.DEV_USERS:
                if user["id"] == user_id:
                    return user
        if username:
            for user in cls.DEV_USERS:
                if user["username"] == username:
                    return user
        return cls.DEV_USERS[0]  # Admin par défaut
    
    @classmethod
    def is_dev_token(cls, token: str) -> bool:
        """Vérifie si le token est un token de développement"""
        return token in cls.DEV_TOKENS.values()
    
    @classmethod
    def get_role_from_token(cls, token: str) -> str:
        """Extrait le rôle du token dev"""
        for role, dev_token in cls.DEV_TOKENS.items():
            if token == dev_token:
                return role.upper()
        return "ADMIN"

dev_config = DevConfig()

# backend\main.py
import sys
from pathlib import Path

# Assurer que le dossier courant est dans le PYTHONPATH
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from typing import Dict, Any

from database import engine, Base, get_db
from core.config import settings
from core.exceptions import CustomException, NotFoundException
from sqlalchemy.orm import Session

from middleware.dev_middleware import DevMiddleware, DevBypassAuthMiddleware
from core.dev_config import dev_config

# Import des routes
from routes import (
    products,
    sales,
    stock,
    accounting,
    suppliers,
    clients,
    dashboard,
    auth,
    appointments  
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Démarrage
    logger.info("Démarrage de l'application Luxe Beauté Management")
    
    # Création des tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Base de données initialisée")
    except Exception as e:
        logger.error(f"Erreur d'initialisation de la base de données: {e}")
    
    yield
    
    # Arrêt
    logger.info("Arrêt de l'application")

# Création de l'application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Système complet de gestion pour institut de beauté luxe",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

if settings.DEV_MODE:
    # Middleware de dev
    app.add_middleware(DevMiddleware)
    
    # Middleware pour bypass l'auth sur certaines routes
    app.add_middleware(
        DevBypassAuthMiddleware,
        exempt_routes=dev_config.DEV_EXEMPT_ROUTES
    )
    
    # Logger en mode dev
    logger.info("Mode développement activé")
    logger.info(f"Env: {settings.ENVIRONMENT}")
    logger.info(f"CORS: {settings.BACKEND_CORS_ORIGINS}")

# Middleware
app.add_middleware(
    CORSMiddleware,
    #allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["votre-domaine.com"]
)

# Gestionnaire d'exceptions global
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error(f"Erreur non gérée: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Une erreur interne est survenue"}
    )

# Montage des fichiers statiques
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Routes de santé
@app.get("/", tags=["Santé"])
async def root():
    return {
        "message": f"Bienvenue sur {settings.APP_NAME}",
        "version": "2.0.0",
        "status": "operational"
    }

@app.get("/health", tags=["Santé"])
async def health_check(db: Session = Depends(get_db)):
    """Vérification de la santé de l'application"""
    try:
        # Test de la connexion à la base de données
        db.execute("SELECT 1")
        
        # Vérification de l'espace disque
        import shutil
        total, used, free = shutil.disk_usage("/")
        
        return {
            "status": "healthy",
            "database": "connected",
            "disk_space": {
                "total_gb": round(total / (2**30), 2),
                "used_gb": round(used / (2**30), 2),
                "free_gb": round(free / (2**30), 2),
                "free_percentage": round((free / total) * 100, 2)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service indisponible"
        )

# Inclusion des routes
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(products.router, prefix="/api/v1")
app.include_router(sales.router, prefix="/api/v1")
app.include_router(stock.router, prefix="/api/v1")
app.include_router(suppliers.router, prefix="/api/v1")
app.include_router(clients.router, prefix="/api/v1")
app.include_router(accounting.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")


# Route d'info système
@app.get("/api/v1/system/info", tags=["Système"])
async def system_info():
    """Informations sur le système"""
    import platform
    import psutil
    from datetime import datetime
    
    return {
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        },
        "application": {
            "name": settings.APP_NAME,
            "version": "2.0.0",
            "debug": settings.DEBUG,
            "uptime": datetime.utcnow().isoformat()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug"
    )


    