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