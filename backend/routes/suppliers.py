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