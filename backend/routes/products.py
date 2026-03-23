# backend/routes/products.py

from collections import defaultdict
from datetime import datetime, timedelta

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
    """Prépare la réponse produit en utilisant le CRUD pour le stock."""
    product_data = product_crud.get_with_stock(db, product.id)
    if not product_data:
        raise HTTPException(500, "Erreur lors de la récupération du produit")
    return schemas.ProductResponse(**product_data)

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

@router.get("/stats", response_model=schemas.ProductStats)
def get_product_stats(db: Session = Depends(get_db)):
    total_products = db.query(func.count(models.Product.id)).filter(models.Product.is_active == True).scalar()
    
    products = db.query(models.Product).filter(models.Product.is_active == True).all()
    stock_value = 0
    low_stock_count = 0
    out_of_stock_count = 0

    for p in products:
        current_stock = product_crud.calculate_current_stock(db, p.id)
        stock_value += current_stock * float(p.purchase_price)
        if current_stock <= 0:
            out_of_stock_count += 1
        elif current_stock <= p.alert_threshold:
            low_stock_count += 1

    return {
        "total_products": total_products,
        "stock_value": stock_value,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count
    }

@router.get("/{product_id}/movements/stats")
def get_product_movement_stats(product_id: str, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Produit non trouvé")

    one_year_ago = datetime.utcnow() - timedelta(days=365)
    movements = db.query(models.StockMovement).filter(
        models.StockMovement.product_id == product_id,
        models.StockMovement.created_at >= one_year_ago
    ).all()

    monthly_in = defaultdict(int)
    monthly_out = defaultdict(int)

    for m in movements:
        month_key = m.created_at.strftime("%Y-%m")
        if m.movement_type in ["IN", "RETURN", "ADJUSTMENT"]:
            monthly_in[month_key] += m.quantity
        elif m.movement_type in ["OUT", "DAMAGED"]:
            monthly_out[month_key] += m.quantity

    months = sorted(set(monthly_in.keys()) | set(monthly_out.keys()))
    in_data = [monthly_in[m] for m in months]
    out_data = [monthly_out[m] for m in months]

    from crud.product import product as product_crud
    current_stock = product_crud.calculate_current_stock(db, product_id)

    return {
        "months": months,
        "in": in_data,
        "out": out_data,
        "total_in": sum(monthly_in.values()),
        "total_out": sum(monthly_out.values()),
        "current_stock": current_stock
    }

# ================================
# GET ALL BRANDS
# ================================
@router.get("/brands", response_model=List[str])
def get_product_brands(db: Session = Depends(get_db)):
    """Récupère toutes les marques distinctes"""
    
    brands = db.query(models.Product.brand)\
        .filter(
            models.Product.brand.isnot(None),
            models.Product.brand != ""
        )\
        .distinct()\
        .order_by(models.Product.brand.asc())\
        .all()

    # Transformer [(‘L’Oréal’,), (‘Nivea’,)] → ['L’Oréal', 'Nivea']
    return [b[0] for b in brands]

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