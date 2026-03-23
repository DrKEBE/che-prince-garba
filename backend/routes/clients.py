# backend/routes/clients.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_  # Ajouté
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import Client, Sale, SaleItem
from schemas import ClientCreate, ClientUpdate, ClientResponse
from crud.client import client as client_crud
from core.exceptions import NotFoundException

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Crée un nouveau client"""
    # Vérifier si le numéro de téléphone existe déjà
    existing = db.query(Client).filter(Client.phone == client.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un client avec ce numéro de téléphone existe déjà"
        )
    
    # Vérifier l'email si fourni
    if client.email:
        existing = db.query(Client).filter(Client.email == client.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un client avec cet email existe déjà"
            )
    
    return client_crud.create(db, obj_in=client)

@router.get("/", response_model=List[ClientResponse])
def read_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    client_type: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère la liste des clients avec filtres"""
    query = db.query(Client)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Client.full_name.ilike(search_pattern),
                Client.email.ilike(search_pattern),
                Client.phone.ilike(search_pattern),
                Client.address.ilike(search_pattern)
            )
        )
    
    if client_type:
        query = query.filter(Client.client_type == client_type)
    
    if city:
        query = query.filter(Client.city == city)
    
    clients = query.offset(skip).limit(limit).all()
    
    # Ajouter les statistiques pour chaque client
    result = []
    for client_obj in clients:
        stats = client_crud.get_client_stats(db, client_obj.id)
        client_data = client_obj.__dict__.copy()
        client_data.update(stats)
        result.append(ClientResponse(**client_data))
    
    return result

@router.get("/{client_id}", response_model=ClientResponse)
def read_client(client_id: str, db: Session = Depends(get_db)):
    """Récupère un client par son ID"""
    db_client = client_crud.get_with_stats(db, client_id=client_id)
    if not db_client:
        raise NotFoundException("Client", client_id)
    return ClientResponse(**db_client)

@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: str,
    client_update: ClientUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour un client"""
    db_client = client_crud.get(db, id=client_id)
    if not db_client:
        raise NotFoundException("Client", client_id)
    
    # Vérifier les doublons
    if client_update.phone and client_update.phone != db_client.phone:
        existing = db.query(Client).filter(Client.phone == client_update.phone).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un client avec ce numéro de téléphone existe déjà"
            )
    
    if client_update.email and client_update.email != db_client.email:
        existing = db.query(Client).filter(Client.email == client_update.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un client avec cet email existe déjà"
            )
    
    updated_client = client_crud.update(db, db_obj=db_client, obj_in=client_update)
    return ClientResponse(**updated_client.__dict__)

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: str, db: Session = Depends(get_db)):
    """Supprime un client"""
    db_client = client_crud.get(db, id=client_id)
    if not db_client:
        raise NotFoundException("Client", client_id)
    
    # Vérifier si le client a des ventes
    sales_count = db.query(Sale).filter(Sale.client_id == client_id).count()
    if sales_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer un client qui a des ventes associées"
        )
    
    client_crud.remove(db, id=client_id)
    return None

@router.get("/{client_id}/purchase-history")
def get_client_purchase_history(
    client_id: str,
    days: int = Query(365, ge=1, le=1095),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Récupère l'historique d'achat d'un client"""
    client = client_crud.get(db, id=client_id)
    if not client:
        raise NotFoundException("Client", client_id)
    
    # Calculer la date de début
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Récupérer les ventes
    sales = db.query(Sale)\
        .filter(
            Sale.client_id == client_id,
            Sale.sale_date >= start_date
        )\
        .order_by(Sale.sale_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    sales_data = []
    for sale in sales:
        total_items = db.query(func.sum(SaleItem.quantity))\
            .filter(SaleItem.sale_id == sale.id)\
            .scalar() or 0
        
        sales_data.append({
            "id": sale.id,
            "invoice_number": sale.invoice_number,
            "sale_date": sale.sale_date,
            "total_amount": float(sale.total_amount),
            "discount": float(sale.discount),
            "final_amount": float(sale.final_amount),
            "payment_method": sale.payment_method,
            "items_count": total_items
        })
    
    return {
        "client_id": client_id,
        "client_name": client.full_name,
        "total_purchases": float(client.total_purchases or 0),
        "loyalty_points": client.loyalty_points or 0,
        "last_purchase": client.last_purchase,
        "sales": sales_data,
        "total_sales": len(sales_data)
    }

@router.get("/stats/top-clients")
def get_top_clients(
    limit: int = Query(10, ge=1, le=50),
    period_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Récupère les meilleurs clients"""
    start_date = datetime.utcnow() - timedelta(days=period_days)
    
    # Requête pour les meilleurs clients par CA
    top_clients = db.query(
        Client.id,
        Client.full_name,
        Client.phone,
        Client.client_type,
        func.sum(Sale.final_amount).label("total_spent"),
        func.count(Sale.id).label("purchase_count")
    )\
    .join(Sale, Sale.client_id == Client.id)\
    .filter(
        Sale.sale_date >= start_date,
        Sale.payment_status == "PAID"
    )\
    .group_by(Client.id, Client.full_name, Client.phone, Client.client_type)\
    .order_by(func.sum(Sale.final_amount).desc())\
    .limit(limit)\
    .all()
    
    result = []
    for client in top_clients:
        result.append({
            "id": client.id,
            "full_name": client.full_name,
            "phone": client.phone,
            "client_type": client.client_type,
            "total_spent": float(client.total_spent or 0),
            "purchase_count": client.purchase_count or 0,
            "average_purchase": float(client.total_spent or 0) / (client.purchase_count or 1)
        })
    
    return {
        "period_days": period_days,
        "total_clients": len(result),
        "clients": result
    }