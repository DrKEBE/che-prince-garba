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