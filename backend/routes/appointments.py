# backend\routes\appointments.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import Appointment, Client
from schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from core.exceptions import NotFoundException

router = APIRouter(prefix="/appointments", tags=["Rendez-vous"])

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """Crée un nouveau rendez-vous"""
    # Vérifier le client
    client = db.query(Client).filter(Client.id == appointment.client_id).first()
    if not client:
        raise NotFoundException("Client", appointment.client_id)
    
    # Vérifier les conflits d'horaire
    existing_appointment = db.query(Appointment).filter(
        Appointment.employee_id == appointment.employee_id,
        Appointment.appointment_date == appointment.appointment_date,
        Appointment.status.in_(["SCHEDULED", "CONFIRMED"])
    ).first()
    
    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'employé a déjà un rendez-vous à cette heure"
        )
    
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.get("/", response_model=List[AppointmentResponse])
def read_appointments(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    employee_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère les rendez-vous avec filtres"""
    query = db.query(Appointment)
    
    if start_date:
        query = query.filter(Appointment.appointment_date >= start_date)
    
    if end_date:
        query = query.filter(Appointment.appointment_date <= end_date)
    
    if employee_id:
        query = query.filter(Appointment.employee_id == employee_id)
    
    if status:
        query = query.filter(Appointment.status == status)
    
    return query.order_by(Appointment.appointment_date).all()

@router.get("/calendar/{date}")
def get_calendar_view(date: datetime, db: Session = Depends(get_db)):
    """Récupère les rendez-vous pour une vue calendrier"""
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    appointments = db.query(Appointment)\
        .filter(
            Appointment.appointment_date >= start_of_day,
            Appointment.appointment_date <= end_of_day
        )\
        .order_by(Appointment.appointment_date)\
        .all()
    
    # Grouper par heure
    slots = {}
    for hour in range(9, 19):  # 9h à 18h
        slots[f"{hour}:00"] = []
    
    for app in appointments:
        hour_key = app.appointment_date.strftime("%H:00")
        if hour_key in slots:
            client = db.query(Client).filter(Client.id == app.client_id).first()
            slots[hour_key].append({
                "id": app.id,
                "client_name": client.full_name if client else "Client inconnu",
                "service": app.service_type,
                "status": app.status
            })
    
    return {
        "date": date.date().isoformat(),
        "slots": slots
    }