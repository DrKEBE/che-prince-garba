# backend\routes\accounting.py

"""
Routes complètes de comptabilité
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, distinct
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from database import get_db
from models import Expense, Sale, Payment, Product, SaleItem, Supplier, Refund, StockMovement
from schemas import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    PaymentCreate, ProfitAnalysis
)
from core.exceptions import NotFoundException, BusinessLogicException
from middleware.auth import get_current_user, require_role
from schemas import UserRole
from crud.sale_service import sale_refund_service

router = APIRouter(prefix="/accounting", tags=["Comptabilité"])


@router.post("/expenses/", response_model=ExpenseResponse, status_code=201)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Crée une nouvelle dépense"""
    db_expense = Expense(
        **expense.dict(),
        created_by=current_user.get("id")
    )
    
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    return db_expense


@router.get("/expenses/", response_model=List[ExpenseResponse])
def get_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère la liste des dépenses avec filtres"""
    query = db.query(Expense)
    
    if category:
        query = query.filter(Expense.category == category)
    
    if start_date:
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Expense.expense_date >= start)
        except ValueError:
            raise HTTPException(400, detail="Format de date invalide")
    
    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Expense.expense_date <= end)
        except ValueError:
            raise HTTPException(400, detail="Format de date invalide")
    
    if min_amount is not None:
        query = query.filter(Expense.amount >= min_amount)
    
    if max_amount is not None:
        query = query.filter(Expense.amount <= max_amount)
    
    expenses = query.order_by(Expense.expense_date.desc())\
                   .offset(skip).limit(limit).all()
    
    return expenses


@router.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère une dépense par ID"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise NotFoundException("Dépense", expense_id)
    
    return expense


@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: str,
    expense_update: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Met à jour une dépense"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise NotFoundException("Dépense", expense_id)
    
    for field, value in expense_update.dict(exclude_unset=True).items():
        setattr(expense, field, value)
    
    expense.updated_by = current_user.get("id")
    
    db.commit()
    db.refresh(expense)
    
    return expense


@router.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(
    expense_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.ADMIN]))
):
    """Supprime une dépense"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise NotFoundException("Dépense", expense_id)
    
    db.delete(expense)
    db.commit()


@router.get("/profit-analysis", response_model=ProfitAnalysis)
def get_profit_analysis(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Analyse de profitabilité"""
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(400, detail="Format de date invalide")
    
    # Revenus totaux
    total_revenue = db.query(func.sum(Sale.final_amount)).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end,
        Sale.payment_status == "PAID"
    ).scalar() or 0
    
    # Dépenses totales
    total_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.expense_date >= start,
        Expense.expense_date <= end
    ).scalar() or 0
    
    # Coût des marchandises vendues
    cogs = db.query(func.sum(SaleItem.quantity * Product.purchase_price))\
        .join(Product, SaleItem.product_id == Product.id)\
        .join(Sale, SaleItem.sale_id == Sale.id)\
        .filter(
            Sale.sale_date >= start,
            Sale.sale_date <= end,
            Sale.payment_status == "PAID"
        ).scalar() or 0
    
    # Remboursements
    total_refunds = db.query(func.sum(Payment.amount)).filter(
        Payment.payment_date >= start,
        Payment.payment_date <= end,
        Payment.amount < 0
    ).scalar() or 0
    
    # Calculs
    gross_profit = total_revenue - cogs
    net_profit = gross_profit - total_expenses + total_refunds  # total_refunds est négatif
    margin_percentage = (float(gross_profit) / float(total_revenue)) if total_revenue > 0 else 0

    return {
        "total_revenue": float(total_revenue),
        "total_expenses": float(total_expenses),
        "cogs": float(cogs),
        "gross_profit": float(gross_profit),
        "net_profit": float(net_profit),
        "margin_percentage": margin_percentage
    }


@router.get("/cash-flow")
def get_cash_flow(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(400, detail="Format de date invalide")

    # ===== ENTRÉES : ventes payées =====
    incoming = db.query(
        func.date(Sale.sale_date).label("date"),
        func.sum(Sale.final_amount).label("amount")
    ).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end,
        Sale.payment_status == "PAID"
    ).group_by(func.date(Sale.sale_date)).order_by(func.date(Sale.sale_date)).all()

    # ===== SORTIES : dépenses (toutes) =====
    outgoing_expenses = db.query(
        func.date(Expense.expense_date).label("date"),
        func.sum(Expense.amount).label("amount")
    ).filter(
        Expense.expense_date >= start,
        Expense.expense_date <= end
    ).group_by(func.date(Expense.expense_date)).order_by(func.date(Expense.expense_date)).all()

    # ===== SORTIES supplémentaires : remboursements approuvés =====
    outgoing_refunds = db.query(
        func.date(Refund.refund_date).label("date"),
        func.sum(Refund.refund_amount).label("amount")
    ).filter(
        Refund.refund_date >= start,
        Refund.refund_date <= end,
        Refund.refund_status.in_(["APPROVED", "COMPLETED"])
    ).group_by(func.date(Refund.refund_date)).order_by(func.date(Refund.refund_date)).all()

    # Fusion des données journalières
    daily = {}

    # Traitement des entrées
    for row in incoming:
        d = str(row.date)
        daily.setdefault(d, {"incoming": 0.0, "outgoing": 0.0})
        daily[d]["incoming"] += float(row.amount)

    # Traitement des dépenses (sorties)
    for row in outgoing_expenses:
        d = str(row.date)
        daily.setdefault(d, {"incoming": 0.0, "outgoing": 0.0})
        daily[d]["outgoing"] += float(row.amount)

    # Traitement des remboursements (sorties également)
    for row in outgoing_refunds:
        d = str(row.date)
        daily.setdefault(d, {"incoming": 0.0, "outgoing": 0.0})
        daily[d]["outgoing"] += float(row.amount)

    # Construction du tableau chronologique
    sorted_dates = sorted(daily.keys())
    daily_balance = []
    current_balance = 0.0
    total_incoming = 0.0
    total_outgoing = 0.0

    for date_str in sorted_dates:
        inc = daily[date_str]["incoming"]
        out = daily[date_str]["outgoing"]
        net = inc - out
        current_balance += net
        total_incoming += inc
        total_outgoing += out
        daily_balance.append({
            "date": date_str,
            "incoming": inc,
            "outgoing": out,
            "net_flow": net,
            "balance": current_balance
        })

    return {
        "period": {"start": start_date, "end": end_date},
        "total_incoming": total_incoming,
        "total_outgoing": total_outgoing,
        "net_cash_flow": total_incoming - total_outgoing,
        "ending_balance": current_balance,
        "daily_balance": daily_balance
    }


@router.get("/financial-reports/{report_type}")
def generate_financial_report(
    report_type: str,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Génère des rapports financiers"""
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(400, detail="Format de date invalide")
    
    if report_type == "income_statement":
        # État des résultats
        profit_analysis = get_profit_analysis(start_date, end_date, db, current_user)
        
        # Détails des revenus
        revenue_by_category = db.query(
            Product.category,
            func.sum(SaleItem.total_price).label("revenue"),
            func.sum(SaleItem.profit).label("profit")
        ).join(SaleItem, Product.id == SaleItem.product_id)\
         .join(Sale, SaleItem.sale_id == Sale.id)\
         .filter(
            Sale.sale_date >= start,
            Sale.sale_date <= end,
            Sale.payment_status == "PAID"
         ).group_by(Product.category).all()
        
        # Détails des dépenses
        expenses_by_category = db.query(
            Expense.category,
            func.sum(Expense.amount).label("amount")
        ).filter(
            Expense.expense_date >= start,
            Expense.expense_date <= end
        ).group_by(Expense.category).all()
        
        return {
            "report_type": "income_statement",
            "period": {"start": start_date, "end": end_date},
            "summary": profit_analysis,
            "revenue_by_category": [
                {"category": cat, "revenue": float(rev), "profit": float(prof)}
                for cat, rev, prof in revenue_by_category
            ],
            "expenses_by_category": [
                {"category": cat, "amount": float(amt)}
                for cat, amt in expenses_by_category
            ]
        }
    
    elif report_type == "balance_sheet":
        # Bilan comptable
        # Actifs
        current_assets = {
            "cash": 0.0,  # À implémenter avec un système de caisse
            "inventory": db.query(
                func.sum(Product.purchase_price * func.coalesce(
                    db.query(func.sum(StockMovement.quantity)).filter(
                        StockMovement.product_id == Product.id,
                        StockMovement.movement_type == "IN"
                    ).scalar_subquery() -
                    db.query(func.sum(StockMovement.quantity)).filter(
                        StockMovement.product_id == Product.id,
                        StockMovement.movement_type == "OUT"
                    ).scalar_subquery(), 0
                ))
            ).scalar() or 0.0,
            "receivables": db.query(
                func.sum(Sale.final_amount)
            ).filter(
                Sale.payment_status == "PENDING"
            ).scalar() or 0.0
        }
        
        # Passifs
        current_liabilities = {
            "payables": db.query(
                func.sum(Expense.amount)
            ).filter(
                Expense.payment_method.is_(None)  # Dépenses non payées
            ).scalar() or 0.0,
            "supplier_debts": db.query(
                func.sum(Supplier.current_balance)
            ).scalar() or 0.0
        }
        
        # Capitaux propres
        equity = {
            "retained_earnings": db.query(
                func.sum(Sale.total_profit) - func.sum(Expense.amount)
            ).scalar() or 0.0
        }
        
        total_assets = sum(current_assets.values())
        total_liabilities = sum(current_liabilities.values())
        total_equity = sum(equity.values())
        
        return {
            "report_type": "balance_sheet",
            "as_of_date": end_date,
            "assets": {
                "current_assets": {k: float(v) for k, v in current_assets.items()},
                "total_current_assets": float(total_assets)
            },
            "liabilities": {
                "current_liabilities": {k: float(v) for k, v in current_liabilities.items()},
                "total_current_liabilities": float(total_liabilities)
            },
            "equity": {k: float(v) for k, v in equity.items()},
            "total_equity": float(total_equity),
            "balance_check": float(total_assets - (total_liabilities + total_equity))
        }
    
    elif report_type == "sales_summary":
        # Récupérer via le service des ventes
        return sale_refund_service.get_sales_period(db, start, end)
    
    else:
        raise HTTPException(400, detail="Type de rapport non supporté")


@router.get("/dashboard/financial-metrics")
def get_financial_metrics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Métriques financières pour le dashboard (cohérentes avec l'analyse de profit)"""
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    
    # Fonction utilitaire pour calculer les métriques sur une période donnée
    def period_metrics(start_date, end_date):
        # Chiffre d'affaires (ventes payées)
        revenue = db.query(func.sum(Sale.final_amount)).filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
            Sale.payment_status == "PAID"
        ).scalar()
        revenue = float(revenue) if revenue is not None else 0.0

        # Remboursements (paiements négatifs)
        refunds = db.query(func.sum(Payment.amount)).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date,
            Payment.amount < 0,
            Payment.status == "COMPLETED"
        ).scalar()
        refunds = float(refunds) if refunds is not None else 0.0

        # Coût des marchandises vendues (COGS)
        cogs = db.query(
            func.sum(SaleItem.quantity * Product.purchase_price)
        ).select_from(Sale).join(
            SaleItem, SaleItem.sale_id == Sale.id
        ).join(
            Product, SaleItem.product_id == Product.id
        ).filter(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
            Sale.payment_status == "PAID"
        ).scalar()
        cogs = float(cogs) if cogs is not None else 0.0

        # Dépenses d'exploitation
        expenses = db.query(func.sum(Expense.amount)).filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        ).scalar()
        expenses = float(expenses) if expenses is not None else 0.0

        gross_profit = revenue - cogs
        net_profit = gross_profit - expenses + refunds  # refunds négatif

        return {
            "revenue": revenue,
            "expenses": expenses,
            "gross_profit": gross_profit,
            "net_profit": net_profit
        }
    
    # Calculs pour les différentes périodes
    daily = period_metrics(today, today)
    monthly = period_metrics(month_start, today)
    yearly = period_metrics(year_start, today)
    
    # Dettes fournisseurs, paiements en attente, etc.
    supplier_debts = db.query(func.sum(Supplier.current_balance)).scalar() or 0.0
    pending_payments = db.query(func.sum(Sale.final_amount)).filter(
        Sale.payment_status == "PENDING"
    ).scalar() or 0.0
    pending_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.payment_method.is_(None)
    ).scalar() or 0.0
    
    # Construction de la réponse (on conserve les clés "profit" pour compatibilité frontend)
    return {
        "daily": {
            "revenue": daily["revenue"],
            "expenses": daily["expenses"],
            "profit": daily["net_profit"]          # ← maintenant c'est le résultat net
        },
        "monthly": {
            "revenue": monthly["revenue"],
            "expenses": monthly["expenses"],
            "profit": monthly["net_profit"]
        },
        "yearly": {
            "revenue": yearly["revenue"],
            "expenses": yearly["expenses"],
            "profit": yearly["net_profit"]
        },
        "outstanding": {
            "supplier_debts": float(supplier_debts),
            "pending_payments": float(pending_payments),
            "pending_expenses": float(pending_expenses),
            "total": float(supplier_debts + pending_payments + pending_expenses)
        },
        "metrics": {
            "profit_margin": (
                (monthly["net_profit"] / monthly["revenue"] * 100)
                if monthly["revenue"] > 0 else 0
            ),
            "expense_ratio": (
                (monthly["expenses"] / monthly["revenue"] * 100)
                if monthly["revenue"] > 0 else 0
            ),
            "avg_daily_revenue": (
                float(monthly["revenue"] / today.day) if today.day > 0 else 0
            )
        }
    }


@router.post("/payments/")
def record_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER]))
):
    """Enregistre un paiement (pour vente, dépense, etc.)"""
    db_payment = Payment(
        **payment.dict(),
        processed_by=current_user.get("id"),
        payment_date=datetime.utcnow()
    )
    
    # Mettre à jour le statut de la vente si applicable
    if payment.sale_id:
        sale = db.query(Sale).filter(Sale.id == payment.sale_id).first()
        if sale:
            total_paid = db.query(func.sum(Payment.amount)).filter(
                Payment.sale_id == sale.id,
                Payment.status == "COMPLETED"
            ).scalar() or 0
            
            if total_paid + float(payment.amount) >= float(sale.final_amount):
                sale.payment_status = "PAID"
            elif total_paid + float(payment.amount) > 0:
                sale.payment_status = "PARTIAL"
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    return {
        "id": db_payment.id,
        "amount": float(db_payment.amount),
        "method": db_payment.payment_method,
        "status": db_payment.status,
        "reference": db_payment.reference
    }


@router.get("/payments/reconciliation")
def reconcile_payments(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Réconciliation des paiements"""
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(400, detail="Format de date invalide")
    
    # Paiements enregistrés
    recorded_payments = db.query(Payment).filter(
        Payment.payment_date >= start,
        Payment.payment_date <= end,
        Payment.status == "COMPLETED"
    ).all()
    
    # Calculer le total des paiements enregistrés
    total_recorded = sum(float(p.amount) for p in recorded_payments)
    
    # Ventas correspondientes
    sales_in_period = db.query(Sale).filter(
        Sale.sale_date >= start,
        Sale.sale_date <= end,
        Sale.payment_status == "PAID"
    ).all()
    
    total_sales_amount = sum(float(s.final_amount) for s in sales_in_period)
    
    # Dépenses correspondantes
    expenses_in_period = db.query(Expense).filter(
        Expense.expense_date >= start,
        Expense.expense_date <= end
    ).all()
    
    total_expenses_amount = sum(float(e.amount) for e in expenses_in_period)
    
    # Différence
    expected_total = total_sales_amount - total_expenses_amount
    difference = total_recorded - expected_total
    
    return {
        "period": {
            "start": start_date,
            "end": end_date
        },
        "recorded_payments": {
            "count": len(recorded_payments),
            "total_amount": total_recorded,
            "details": [
                {
                    "id": p.id,
                    "amount": float(p.amount),
                    "method": p.payment_method,
                    "date": p.payment_date,
                    "reference": p.reference,
                    "sale_id": p.sale_id
                }
                for p in recorded_payments
            ]
        },
        "sales_in_period": {
            "count": len(sales_in_period),
            "total_amount": total_sales_amount
        },
        "expenses_in_period": {
            "count": len(expenses_in_period),
            "total_amount": total_expenses_amount
        },
        "reconciliation": {
            "expected_total": expected_total,
            "recorded_total": total_recorded,
            "difference": difference,
            "is_reconciled": abs(difference) < 0.01  # Tolérance de 0.01
        }
    }