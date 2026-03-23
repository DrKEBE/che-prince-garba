# backend\crud\client.py

from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta

from models import Client, Sale, SaleItem
from schemas import ClientCreate, ClientUpdate
from crud.base import CRUDBase


class CRUDClient(CRUDBase[Client, ClientCreate, ClientUpdate]):
    def create_with_user(self, db: Session, *, obj_in: ClientCreate, user_id: str) -> Client:
        db_obj = Client(
            id=str(uuid.uuid4()),
            **obj_in.model_dump(exclude_unset=True),
            created_by=user_id,
            updated_by=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_email(self, db: Session, email: str) -> Optional[Client]:
        return db.query(Client).filter(Client.email == email).first()

    def get_by_phone(self, db: Session, phone: str) -> Optional[Client]:
        return db.query(Client).filter(Client.phone == phone).first()

    def search(
        self, db: Session, *, 
        search_term: str = "", 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Client]:
        query = db.query(Client)
        
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                or_(
                    Client.full_name.ilike(search_pattern),
                    Client.email.ilike(search_pattern),
                    Client.phone.ilike(search_pattern),
                    Client.address.ilike(search_pattern)
                )
            )
        
        return query.offset(skip).limit(limit).all()

    def update_client_stats(self, db: Session, client_id: str) -> Client:
        """Met à jour les statistiques du client"""
        client = self.get(db, client_id)
        if not client:
            return None
        
        # Calculer le total des achats
        total_sales = db.query(func.sum(Sale.final_amount))\
            .filter(Sale.client_id == client_id)\
            .scalar() or 0
        
        # Compter le nombre de ventes
        sale_count = db.query(func.count(Sale.id))\
            .filter(Sale.client_id == client_id)\
            .scalar() or 0
        
        # Dernière vente
        last_sale = db.query(Sale)\
            .filter(Sale.client_id == client_id)\
            .order_by(Sale.sale_date.desc())\
            .first()
        
        client.total_purchases = total_sales
        client.total_transactions = sale_count
        client.last_purchase = last_sale.sale_date if last_sale else None
        
        db.commit()
        db.refresh(client)
        return client

    def get_client_stats(self, db: Session, client_id: str) -> dict:
        """Récupère les statistiques détaillées d'un client"""
        client = self.get(db, client_id)
        if not client:
            return None
        
        # Ventes des 30 derniers jours
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_sales = db.query(func.sum(Sale.final_amount))\
            .filter(
                Sale.client_id == client_id,
                Sale.sale_date >= thirty_days_ago
            )\
            .scalar() or 0
        
        return {
            "client_id": client_id,
            "total_purchases": float(client.total_purchases or 0),
            "total_transactions": client.total_transactions or 0,
            "last_purchase": client.last_purchase,
            "recent_purchases_30d": float(recent_sales),
            "average_purchase": float(client.total_purchases or 0) / (client.total_transactions or 1)
        }

    def get_with_stats(self, db: Session, client_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un client avec ses statistiques"""
        client = self.get(db, client_id)
        if not client:
            return None
        
        stats = self.get_client_stats(db, client_id)
        return {**client.__dict__, **stats}


client = CRUDClient(Client)