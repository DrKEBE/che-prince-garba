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
            db.commit()
            db.refresh(db_sale)
        # Récupérer les détails de la vente créée
            return SaleRefundService.get_sale_details(db, db_sale.id)
                
        except Exception as e:
            db.rollback()  # 🔥 TRÈS IMPORTANT
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