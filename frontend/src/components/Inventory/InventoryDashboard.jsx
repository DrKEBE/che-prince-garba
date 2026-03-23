VOICI la structure du projet

├───backend
│   │   .env
│   │   app.db
│   │   che_prince_garba.db
│   │   database.py
│   │   main.py
│   │   models.py
│   │   schemas.py
│   │   __init__.py
│   │
│   ├───core
│   │   │   config.py
│   │   │   constants.py
│   │   │   dev-config.py
│   │   │   exceptions.py
│   ├───crud
│   │   │   base.py
│   │   │   client.py
│   │   │   product.py
│   │   │   sales_stats.py
│   │   │   sale_service.py
│   │   │   __init__.py
│   │
│   ├───middleware
│   │   │   auth.py
│   │   │   rate_limiter.py
│   │   │   dev_middleware.py
│   │   │   __init__.py
│   │   │
│   ├───routes
│   │   │   accounting.py
│   │   │   appointments.py
│   │   │   auth.py
│   │   │   clients.py
│   │   │   dashboard.py
│   │   │   dev.py
│   │   │   products.py
│   │   │   sales.py
│   │   │   stock.py
│   │   │   suppliers.py
│   │   │   __init__.py
│   │
│   ├───utils
│   │   │   alerts.py
│   │   │   export.py
│   │   │   optimization.py
│   │   │   pdf_generator.py
│   │   │   stock.py
│   
│   
|____frontend

│   .env
│   .env.local
│   index.html
│   package.json
│   README.md
│   vite.config.js
│
├───public
│   │   favicon.ico
│   │   manifest.json
│   │
│   └───assets
└───src
    │   App.jsx
    │   index.jsx
    │   routes.jsx
    │
    ├───components
    │   ├───clients
    │   │       ClientCard.jsx   
    │   │       ClientForm.jsx      
    │   │
    │   ├───common
    │   │       Badge.jsx
    │   │       ConfirmationModal.jsx
    │   │       DataTable.jsx       
    │   │       ErrorBoundary.jsx   
    │   │       LoadingSpinner.jsx  
    │   │       SearchBar.jsx       
    │   │       SimpleDataTable.jsx 
    │   │
    │   ├───dashboard
    │   │       ChartCard.jsx       
    │   │       InventoryAlerts.jsx 
    │   │       SalesChart.jsx      
    │   │       StatsCard.jsx       
    │   │       
    │   ├───dev
    │   │       DevPanel.jsx        
    │   │
    │   ├───layout
    │   │       Footer.jsx
    │   │       Layout.jsx
    │   │       Navbar.jsx
    │   │       Sidebar.jsx
    │   │
    │   ├───products
    │   │       ProductCard.jsx     
    │   │       ProductFilter.jsx   
    │   │       ProductForm.jsx     
    │   │       StockMovement.jsx   
    │   │
    │   └───sales
    │           Invoice.jsx
    │           RefundForm.jsx         
    │           SaleForm.jsx        
    │           SaleItem.jsx        
    │
    ├───constants
    │       config.js
    │       dev.js
    │
    ├───context
    │       AppContext.jsx
    │       AuthContext.jsx
    │
    ├───hooks
    │       useApi.js
    │       useAuth.js
    │
    ├───pages
    │       Accounting.jsx              
    │       Clients.jsx
    │       Dashboard.jsx
    │       Login.jsx
    │       Products.jsx
    │       Sales.jsx
    │
    ├───services
    │       api.js
    │       auth.js
    │       Accounting.js     
    │       clients.js
    │       dashboard.js
    │       products.js
    │       sales.js
    │
    ├───styles
    │       animations.css
    │       components.css
    │       global.css
    │       theme.js
    │
    └───utils
            formatters.js
            helpers.js
            validators.js

je souhaite la plateforme soit complet pour une meilleur gestion d'un plateforme de boutique de vente des produit cosmétique

il ya beaucoup d'eurrer lorsque manipile la partie stock de mon app

maintenant tu va réagir comme ingénieur en développement fullstack professionnelle POUR corriger les errer dans les partie stock que sa soit du backend et ou le frontend avec une excellent niveau UI/UX, interface élégant , dynamique, esthétique, attirant, impressionnant de façon professionnel, avec des couleur pour un plateforme de boutique de vente des produit cosmétique souvent dégradé pour rendre encore plus mon app meilleur et plus complet

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
    "Soins Capillaires",
    "Lait",
    "Crème",
    "Pommade",
    "Maquillage",
    "Déodorants",
    "Parfums",
    "Huiles",
    "Sérums",
    "Gommage",
    "Shampoing",
    "Mèches",
    "Accessoires",
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


# backend/routes/stock.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from typing import List, Optional
from utils.stock import compute_stock  # Import
from pydantic import BaseModel
class BulkStockAdjustment(BaseModel):
    product_id: str
    quantity: int
    movement_type: str
    reason: str = None

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
def read_stock_movements(
    product_id: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.StockMovement)
    if product_id:
        query = query.filter(models.StockMovement.product_id == product_id)
    movements = query.offset(skip).limit(limit).all()
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

@router.get("/trends")
def get_stock_trends(db: Session = Depends(get_db), days: int = 30):
    start_date = datetime.utcnow() - timedelta(days=days)
    movements = db.query(models.StockMovement).filter(
        models.StockMovement.created_at >= start_date
    ).all()

    daily_in = defaultdict(int)
    daily_out = defaultdict(int)
    for m in movements:
        day_key = m.created_at.strftime("%Y-%m-%d")
        if m.movement_type in ["IN", "RETURN", "ADJUSTMENT"]:
            daily_in[day_key] += m.quantity
        else:
            daily_out[day_key] += m.quantity

    all_days = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days+1)]
    in_trend = [daily_in.get(day, 0) for day in all_days]
    out_trend = [daily_out.get(day, 0) for day in all_days]

    return {
        "dates": all_days,
        "in": in_trend,
        "out": out_trend
    }

@router.post("/bulk")
def bulk_stock_adjustments(adjustments: List[BulkStockAdjustment], db: Session = Depends(get_db)):
    from crud.product import product as product_crud
    results = []
    for adj in adjustments:
        try:
            movement = product_crud.update_stock(
                db=db,
                product_id=adj.product_id,
                quantity=abs(adj.quantity),
                movement_type=adj.movement_type,
                reason=adj.reason
            )
            results.append({"product_id": adj.product_id, "success": True, "movement_id": movement.id})
        except Exception as e:
            db.rollback()  # important de rollback pour éviter des commits partiels
            results.append({"product_id": adj.product_id, "success": False, "error": str(e)})
    db.commit()
    return results

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

@router.get("/stats", response_model=schemas.ProductStats)
def get_product_stats(db: Session = Depends(get_db)):
    """Statistiques globales des produits"""
    total_products = db.query(func.count(models.Product.id)).filter(models.Product.is_active == True).scalar()
    
    products = db.query(models.Product).filter(models.Product.is_active == True).all()
    stock_value = 0
    low_stock_count = 0
    out_of_stock_count = 0

    from crud.product import product as product_crud
    for p in products:
        current_stock = product_crud.calculate_current_stock(db, p.id)
        stock_value += current_stock * float(p.purchase_price)  # attention: purchase_price est Numeric, convertir en float
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


# backend\models.py
import sys

# Empêcher la double exécution du module
if 'models_initialized' in sys.modules:
    # Si les modèles sont déjà initialisés, ne pas les redéfinir
    print("⚠️  Modèles déjà initialisés, évitement de la redéfinition")
else:
    sys.modules['models_initialized'] = True


from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text, ForeignKey, JSON, CheckConstraint, Index, Numeric, event, Computed
from sqlalchemy.orm import relationship, validates, Session
from sqlalchemy.sql import func
from datetime import datetime, date
import uuid
from database import Base
import re

def generate_uuid():
    return str(uuid.uuid4())

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Product(Base, TimestampMixin):
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    brand = Column(String(100))  # NOUVEAU: Marque du produit
    description = Column(Text)
    purchase_price = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    margin = Column(Numeric(5, 2))
    alert_threshold = Column(Integer, default=10, nullable=False)
    min_stock = Column(Integer, default=5)  # NOUVEAU: Stock minimum
    max_stock = Column(Integer)  # NOUVEAU: Stock maximum
    sku = Column(String(100), unique=True, index=True)
    barcode = Column(String(100), unique=True, index=True)
    images = Column(JSON, default=list)
    variants = Column(JSON, default=dict)
    weight = Column(Float)  # NOUVEAU: Poids en kg
    dimensions = Column(JSON)  # NOUVEAU: Dimensions {longueur, largeur, hauteur}
    expiration_date = Column(DateTime)  # NOUVEAU: Date d'expiration
    is_active = Column(Boolean, default=True, index=True)
    
    # Relations
    stock_movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")
    sale_items = relationship("SaleItem", back_populates="product")
    
    # Index composés
    __table_args__ = (
        Index('idx_product_category_active', 'category', 'is_active'),
        CheckConstraint('selling_price >= purchase_price', name='check_selling_price'),
        CheckConstraint('alert_threshold >= 0', name='check_alert_threshold')
    )
    
    @validates('purchase_price', 'selling_price')
    def validate_prices(self, key, value):
        if value < 0:
            raise ValueError(f"{key} ne peut pas être négatif")
        return value
    
    @validates('sku', 'barcode')
    def validate_codes(self, key, value):
        if value and len(value) > 100:
            raise ValueError(f"{key} trop long")
        return value

    @property
    def current_stock(self, db: Session = None) -> int:
        """Propriété pour obtenir le stock actuel"""
        if not db:
            # Si pas de session, retourner une estimation basée sur les relations chargées
            if hasattr(self, '_current_stock'):
                return self._current_stock
            
            # Si les mouvements sont chargés, calculer localement
            if hasattr(self, 'stock_movements') and self.stock_movements:
                stock_in = sum(m.quantity for m in self.stock_movements 
                             if m.movement_type in ["IN", "ADJUSTMENT"])
                stock_out = sum(m.quantity for m in self.stock_movements 
                              if m.movement_type in ["OUT", "DAMAGED", "RETURN"])
                return stock_in - stock_out
            
            return 0
        
        # Avec session, calculer précisément
        from crud.product import product as product_crud
        return product_crud.calculate_current_stock(db, self.id)
    
    @property
    def stock_status(self) -> str:
        """Statut du stock basé sur le seuil d'alerte"""
        stock = self.current_stock
        if stock <= 0:
            return "RUPTURE"
        elif stock <= self.alert_threshold:
            return "ALERTE"
        elif stock <= self.alert_threshold * 2:
            return "NORMAL"
        else:
            return "EXCÉDENT"

class Client(Base, TimestampMixin):
    __tablename__ = "clients"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    full_name = Column(String(200), nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, index=True)
    address = Column(Text, default= "ATT Bougou 320")
    city = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default="Côte d'Ivoire")
    loyalty_points = Column(Integer, default=0)
    client_type = Column(String(50), default="REGULAR", index=True)
    total_purchases = Column(Numeric(12, 2), default=0.0)
    total_transactions = Column(Integer, default=0)  
    last_purchase = Column(DateTime)
    notes = Column(Text)
    birth_date = Column(Date, nullable=True)  # NOUVEAU: Date de naissance
    gender = Column(String(20))  # NOUVEAU: Genre
    preferences = Column(JSON, default=dict)  # NOUVEAU: Préférences produit
    
    # Relations
    sales = relationship("Sale", back_populates="client")
    appointments = relationship("Appointment", back_populates="client")  # NOUVEAU
    
    @validates('phone')
    def validate_phone(self, key, value):
        # Validation basique de numéro de téléphone
        if not re.match(r'^\+?[\d\s\-\(\)]{8,20}$', value):
            raise ValueError("Numéro de téléphone invalide")
        return value
    
    @validates('email')
    def validate_email(self, key, value):
        if value and '@' not in value:
            raise ValueError("Email invalide")
        return value
    
    @validates("birth_date")
    def validate_birth_date(self, key, value):
        if value is None:
            return None
        if isinstance(value, str):
            return date.fromisoformat(value)  # ✅ conversion SAFE
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        raise ValueError("birth_date invalide")

class Sale(Base, TimestampMixin):
    __tablename__ = "sales"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    client_id = Column(String(36), ForeignKey("clients.id", ondelete="SET NULL"), index=True)
    sale_date = Column(DateTime, default=datetime.utcnow, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    total_amount = Column(Numeric(12, 2), nullable=False)
    total_cost = Column(Numeric(12, 2), default=0.0)  
    discount = Column(Numeric(10, 2), default=0.0)
    final_amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_status = Column(String(50), default="PAID", index=True)
    debt_amount = Column(Numeric(10, 2), default=0.0)
    tax_amount = Column(Numeric(10, 2), default=0.0)  # NOUVEAU: Taxes
    shipping_cost = Column(Numeric(10, 2), default=0.0)  # NOUVEAU: Frais de livraison
    notes = Column(Text)
    total_profit = Column(Numeric(12, 2), default=0.0)
    cashier_id = Column(String(36))  # NOUVEAU: ID du caissier
    is_refunded = Column(Boolean, default=False)  # NOUVEAU: Indicateur de remboursement
    client = relationship("Client", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sale")
    refunds = relationship("Refund", back_populates="sale", cascade="all, delete-orphan")  # Ajouté
    
    # Champs pour les remboursements
    refunded_amount = Column(Numeric(12, 2), default=0.0)
    is_refundable = Column(Boolean, default=True)
    refund_deadline = Column(DateTime)  # Date limite pour les remboursements
    
    __table_args__ = (
        CheckConstraint('final_amount >= 0', name='check_final_amount'),
        CheckConstraint('discount >= 0', name='check_discount'),
        Index('idx_sale_date_status', 'sale_date', 'payment_status'),
    )

class SaleItem(Base):
    __tablename__ = "sale_items"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    sale_id = Column(String(36), ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    purchase_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0.0)  # NOUVEAU: Remise par ligne
    profit = Column(Numeric(10, 2), default=0.0)
    cost = Column(Numeric(10, 2), default=0.0)  # Coût total de la ligne

    # Relations
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
    refunds = relationship("RefundItem", back_populates="sale_item")
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        Index('idx_sale_item_product', 'sale_id', 'product_id'),
    )

class StockMovement(Base, TimestampMixin):
    __tablename__ = "stock_movements"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    movement_type = Column(String(20), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2))  # NOUVEAU: Coût unitaire
    total_cost = Column(Numeric(10, 2))  # NOUVEAU: Coût total
    reason = Column(String(200))
    reference = Column(String(100), index=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"))  # NOUVEAU: Lien fournisseur
    notes = Column(Text)
    expiration_date = Column(DateTime)  # NOUVEAU: Pour suivi expiration
    movement_date = Column(DateTime, default=datetime.utcnow, nullable=False)  # AJOUTÉ

    # Relations
    product = relationship("Product", back_populates="stock_movements")
    supplier = relationship("Supplier")  # NOUVEAU
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_movement_quantity'),
        Index('idx_movement_product_date', 'product_id', 'created_at'),
    )

class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False, index=True)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text, default= "ATT Bougou 320")
    city = Column(String(100))
    country = Column(String(100), default="Côte d'Ivoire")
    tax_id = Column(String(100))  # NOUVEAU: Numéro d'identification fiscale
    payment_terms = Column(String(100))
    credit_limit = Column(Numeric(12, 2))  # NOUVEAU: Limite de crédit
    current_balance = Column(Numeric(12, 2), default=0.0)  # NOUVEAU: Solde courant
    products_supplied = Column(JSON, default=list)
    notes = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    
    # Relations
    stock_movements = relationship("StockMovement", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")  # NOUVEAU

class Expense(Base, TimestampMixin):
    __tablename__ = "expenses"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    expense_date = Column(DateTime, default=datetime.utcnow, index=True)
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100))  # NOUVEAU: Sous-catégorie
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(50))
    recipient = Column(String(200))  # NOUVEAU: Bénéficiaire
    reference_number = Column(String(100))  # NOUVEAU: Numéro de référence
    notes = Column(Text)
    is_recurring = Column(Boolean, default=False)  # NOUVEAU: Dépense récurrente
    recurring_frequency = Column(String(50))  # NOUVEAU: Fréquence
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User")
    
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_expense_amount'),
        Index('idx_expense_category_date', 'category', 'expense_date'),
    )

# --- NOUVELLES CLASSES POUR FONCTIONNALITÉS AVANCÉES ---

class Appointment(Base, TimestampMixin):
    """Gestion des rendez-vous"""
    __tablename__ = "appointments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    client_id = Column(String(36), ForeignKey("clients.id"), nullable=False)
    employee_id = Column(String(36))  # ID de l'employé/estéticienne
    service_type = Column(String(100), nullable=False)
    appointment_date = Column(DateTime, nullable=False, index=True)
    duration = Column(Integer, default=60)  # Durée en minutes
    status = Column(String(50), default="SCHEDULED", index=True)  # SCHEDULED, CONFIRMED, COMPLETED, CANCELLED
    notes = Column(Text)
    total_amount = Column(Numeric(10, 2), default=0.0)
    paid_amount = Column(Numeric(10, 2), default=0.0)
    
    client = relationship("Client", back_populates="appointments")

class PurchaseOrder(Base, TimestampMixin):
    """Commandes fournisseurs"""
    __tablename__ = "purchase_orders"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=False)
    order_number = Column(String(100), unique=True, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    expected_delivery = Column(DateTime)
    status = Column(String(50), default="PENDING", index=True)  # PENDING, ORDERED, RECEIVED, CANCELLED
    total_amount = Column(Numeric(12, 2), default=0.0)
    notes = Column(Text)
    
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")



class PurchaseOrderItem(Base, TimestampMixin):
    """Articles des commandes fournisseurs"""
    __tablename__ = "purchase_order_items"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    purchase_order_id = Column(String(36), ForeignKey("purchase_orders.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    received_quantity = Column(Integer, default=0)
    status = Column(String(50), default="PENDING")  # PENDING, RECEIVED, CANCELLED
    
    # Relations
    order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<PurchaseOrderItem {self.id}>"
    
    @property
    def subtotal(self):
        return self.quantity * self.unit_price



class Payment(Base, TimestampMixin):
    """Gestion des paiements (pour ventes et dépenses)"""
    __tablename__ = "payments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    sale_id = Column(String(36), ForeignKey("sales.id"))
    expense_id = Column(String(36), ForeignKey("expenses.id"))
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    reference = Column(String(100))
    status = Column(String(50), default="COMPLETED")  # COMPLETED, FAILED, REFUNDED
    notes = Column(Text)
    
    sale = relationship("Sale", back_populates="payments")

# Ajouter ces classes après la classe Payment

class Refund(Base, TimestampMixin):
    """Modèle pour les remboursements"""
    __tablename__ = "refunds"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    sale_id = Column(String(36), ForeignKey("sales.id"), nullable=False, index=True)
    refund_number = Column(String(100), unique=True, nullable=False, index=True)
    refund_date = Column(DateTime, default=datetime.utcnow)
    refund_amount = Column(Numeric(12, 2), nullable=False)
    refund_reason = Column(String(200), nullable=False)
    refund_method = Column(String(50), nullable=False)  # CASH, BANK_TRANSFER, CREDIT_NOTE
    refund_status = Column(String(50), default="PENDING", index=True)  # PENDING, APPROVED, COMPLETED, CANCELLED
    approved_by = Column(String(36), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    notes = Column(Text)
    is_partial = Column(Boolean, default=False)
    previous_refund_id = Column(String(36), ForeignKey("refunds.id"))  # Pour les remboursements multiples
    sale = relationship("Sale", back_populates="refunds")  # Corrigé: singular
    items = relationship("RefundItem", back_populates="refund", cascade="all, delete-orphan")
    approver = relationship("User", foreign_keys=[approved_by])
    
    __table_args__ = (
        CheckConstraint('refund_amount > 0', name='check_refund_amount'),
        Index('idx_refund_sale_status', 'sale_id', 'refund_status'),
    )

class RefundItem(Base):
    """Articles remboursés"""
    __tablename__ = "refund_items"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    refund_id = Column(String(36), ForeignKey("refunds.id"), nullable=False)
    sale_item_id = Column(String(36), ForeignKey("sale_items.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    refund_price = Column(Numeric(10, 2), nullable=False)
    reason = Column(String(200))
    restocked = Column(Boolean, default=True)  # Si le produit retourne en stock
    
    # Relations
    refund = relationship("Refund", back_populates="items")
    sale_item = relationship("SaleItem")
    product = relationship("Product")
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_refund_quantity'),
        Index('idx_refund_item_product', 'refund_id', 'product_id'),
    )

class User(Base, TimestampMixin):
    """Utilisateurs système"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20))
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String(50), default="USER")  # ADMIN, MANAGER, CASHIER, STOCK_MANAGER
    permissions = Column(JSON, default=list)
    last_login = Column(DateTime)
    
    __table_args__ = (
        Index('idx_user_role_active', 'role', 'is_active'),
    )


# backend\schemas.py

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, EmailStr, ConfigDict
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# =========================
# ENUMS
# =========================
class PaymentMethod(str, Enum):
    CASH = "CASH"
    MOBILE_MONEY = "Saraly"
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    CHECK = "CHECK"

class PaymentStatus(str, Enum):
    PAID = "PAID"
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"

class StockMovementType(str, Enum):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"
    RETURN = "RETURN"
    DAMAGED = "DAMAGED"

class ClientType(str, Enum):
    REGULAR = "REGULAR"
    VIP = "VIP"
    FIDELITE = "FIDELITE"
    WHOLESALER = "WHOLESALER"

class AppointmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    CASHIER = "CASHIER"
    STOCK_MANAGER = "STOCK_MANAGER"
    BEAUTICIAN = "BEAUTICIAN"

class RefundStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class RefundMethod(str, Enum):
    CASH = "CASH"
    BANK_TRANSFER = "BANK_TRANSFER"
    CREDIT_NOTE = "CREDIT_NOTE"
    STORE_CREDIT = "STORE_CREDIT"
    ORIGINAL_PAYMENT = "ORIGINAL_PAYMENT"

class RefundReason(str, Enum):
    CUSTOMER_REQUEST = "CUSTOMER_REQUEST"
    DEFECTIVE_PRODUCT = "DEFECTIVE_PRODUCT"
    WRONG_ITEM = "WRONG_ITEM"
    LATE_DELIVERY = "LATE_DELIVERY"
    CHANGE_OF_MIND = "CHANGE_OF_MIND"
    SIZING_ISSUE = "SIZING_ISSUE"
    ALLERGY_REACTION = "ALLERGY_REACTION"
    QUALITY_ISSUE = "QUALITY_ISSUE"
    OTHER = "OTHER"

# =========================
# BASE MODELS
# =========================
class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={
            Decimal: lambda v: float(v) if v is not None else None,
            datetime: lambda v: v.isoformat() if v else None
        }
    )

# =========================
# PRODUCT SCHEMAS
# =========================
class ProductBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    purchase_price: int = Field(..., gt=0)
    selling_price: int = Field(..., gt=0)
    alert_threshold: int = Field(10, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    max_stock: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    weight: Optional[float] = Field(None, ge=0)
    dimensions: Optional[Dict[str, float]] = None
    expiration_date: Optional[datetime] = None
    is_active: bool = True

    @validator('selling_price')
    def selling_price_greater_than_purchase(cls, v, values):
        if 'purchase_price' in values and v <= values['purchase_price']:
            raise ValueError('Le prix de vente doit être supérieur au prix d\'achat')
        return v
    
    @validator('sku', 'barcode')
    def validate_unique_codes(cls, v, values):
        """Valider que les codes ne sont pas la valeur par défaut 'string'"""
        if v == "string":
            raise ValueError(f"Veuillez fournir une valeur unique pour ce champ, pas 'string'")
        return v

class ProductCreate(ProductBase):
    initial_stock: int = Field(0, ge=0)

class ProductUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    purchase_price: Optional[int] = Field(None, gt=0)
    selling_price: Optional[int] = Field(None, gt=0)
    alert_threshold: Optional[int] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    max_stock: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    weight: Optional[float] = Field(None, ge=0)
    dimensions: Optional[Dict[str, float]] = None
    expiration_date: Optional[datetime] = None
    is_active: Optional[bool] = None

    @validator('selling_price')
    def selling_price_greater_than_purchase(cls, v, values):
        if v is not None and 'purchase_price' in values and values['purchase_price'] is not None:
            if v <= values['purchase_price']:
                raise ValueError('Le prix de vente doit être supérieur au prix d\'achat')
        return v

class ProductResponse(ProductBase):
    id: str
    margin: Optional[float]
    current_stock: Optional[int] = None
    stock_status: Optional[str] = None
    images: List[str] = []
    variants: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

class ProductStats(BaseSchema):
    total_products: int
    stock_value: int  # ou Decimal
    low_stock_count: int
    out_of_stock_count: int

# =========================
# CLIENT SCHEMAS
# =========================
class ClientBase(BaseSchema):
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=8, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = "ATT Bougou 320"
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "Côte d'Ivoire"
    client_type: ClientType = ClientType.REGULAR
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    notes: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {}

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseSchema):
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = "ATT Bougou 320"
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    client_type: Optional[ClientType] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    notes: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class ClientResponse(ClientBase):
    id: str
    loyalty_points: int = 0
    total_purchases: Decimal = Decimal("0.00")
    total_transactions: int = 0  
    last_purchase: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

# =========================
# SALE SCHEMAS
# =========================
class SaleItemCreate(BaseSchema):
    product_id: str
    quantity: int = Field(..., gt=0)
    unit_price: Optional[int] = None  
    discount: Optional[int] = Field(0, ge=0)

class SaleCreate(BaseSchema):
    client_id: Optional[str] = None
    payment_method: PaymentMethod
    discount: int = Field(0, ge=0) 
    tax_amount: Optional[int] = Field(0, ge=0) 
    shipping_cost: Optional[int] = Field(0, ge=0)
    notes: Optional[str] = None
    items: List[SaleItemCreate] = Field(..., min_items=1)

class SaleItemResponse(BaseSchema):
    id: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    purchase_price: Decimal
    discount: Decimal
    total_price: Decimal
    profit: Decimal

class SaleResponse(BaseSchema):
    id: str
    invoice_number: str
    client_id: Optional[str]
    client_name: Optional[str]
    sale_date: datetime
    total_amount: Decimal
    discount: Decimal
    tax_amount: Decimal
    shipping_cost: Decimal
    final_amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    total_profit: Decimal
    notes: Optional[str]
    items: List[SaleItemResponse]
    created_at: datetime

# =========================
# STOCK MOVEMENT SCHEMAS
# =========================
class StockMovementCreate(BaseSchema):
    product_id: str
    movement_type: StockMovementType
    quantity: int = Field(..., gt=0)
    unit_cost: Optional[Decimal] = None
    reason: Optional[str] = None
    reference: Optional[str] = None
    supplier_id: Optional[str] = None
    notes: Optional[str] = None
    expiration_date: Optional[datetime] = None
    movement_date: Optional[datetime] = None 

    @validator('movement_date', pre=True, always=True)
    def set_default_movement_date(cls, v):
        if v is None:
            return datetime.utcnow()
        return v

class StockMovementResponse(BaseSchema):
    id: str
    product_id: str
    movement_type: StockMovementType
    quantity: int
    unit_cost: Optional[Decimal]
    total_cost: Optional[Decimal]
    reason: Optional[str]
    reference: Optional[str]
    supplier_id: Optional[str]
    notes: Optional[str]
    expiration_date: Optional[datetime]= None
    movement_date: datetime
    product_name: Optional[str] = None
    created_at: datetime

# =========================
# SUPPLIER SCHEMAS
# =========================
class SupplierBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = "ATT Bougou 320"
    city: Optional[str] = None
    country: Optional[str] = "Côte d'Ivoire"
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    products_supplied: List[str] = []
    notes: Optional[str] = None
    is_active: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = "ATT Bougou 320"
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    products_supplied: Optional[List[str]] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class SupplierResponse(SupplierBase):
    id: str
    current_balance: Decimal = Decimal("0.00")
    created_at: datetime
    updated_at: datetime

# =========================
# EXPENSE SCHEMAS
# =========================
class ExpenseBase(BaseSchema):
    category: str = Field(..., max_length=100)
    subcategory: Optional[str] = None
    description: str = Field(..., max_length=200)
    amount: int = Field(..., gt=0)
    payment_method: Optional[PaymentMethod] = None
    recipient: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    expense_date: Optional[datetime] = None

class ExpenseUpdate(BaseSchema):
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = None
    description: Optional[str] = Field(None, max_length=200)
    amount: Optional[int] = Field(None, gt=0)
    payment_method: Optional[PaymentMethod] = None
    recipient: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[str] = None

class ExpenseResponse(ExpenseBase):
    id: str
    expense_date: datetime
    created_by: str # 🔥 AJOUTE

    created_at: datetime

# =========================
# PAYMENT SCHEMAS
# =========================
class PaymentBase(BaseSchema):
    sale_id: Optional[str] = None
    expense_id: Optional[str] = None
    amount: int = Field(...)
    payment_method: PaymentMethod
    reference: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: str
    payment_date: datetime
    status: str
    processed_by: Optional[str] = None
    created_at: datetime

# =========================
# AUTH SCHEMAS
# =========================
class UserBase(BaseSchema):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = None
    role: UserRole = UserRole.CASHIER
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str | EmailStr
    password: str

class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# =========================
# DASHBOARD & REPORTS
# =========================
class DashboardStats(BaseSchema):
    total_products: int
    total_clients: int
    total_sales: int
    daily_revenue: Decimal
    monthly_revenue: Decimal
    out_of_stock: int
    low_stock: int
    total_profit: Decimal
    daily_profit: Decimal
    monthly_profit: Decimal
    pending_orders: int = 0
    pending_appointments: int = 0

class SalesTrendItem(BaseSchema):
    date: str
    amount: float
    profit: float
    count: int

class TopProductItem(BaseSchema):
    product_id: str
    name: str
    total_sold: int
    total_revenue: Decimal
    total_profit: Decimal
    margin_percentage: float

class ProfitAnalysis(BaseSchema):
    total_revenue: Decimal
    total_expenses: Decimal
    cogs: Decimal
    gross_profit: Decimal
    net_profit: Decimal
    margin_percentage: float

# =========================
# REFUND SCHEMAS
# =========================
class RefundItemCreate(BaseSchema):
    sale_item_id: str
    quantity: int = Field(..., gt=0)
    refund_price: int = Field(..., gt=0)
    reason: Optional[str] = None
    restocked: bool = True

class RefundItemResponse(BaseSchema):
    id: str
    product_id: str
    product_name: str
    quantity: int
    refund_price: int
    original_price: int
    reason: Optional[str]
    restocked: bool

class RefundCreate(BaseSchema):
    refund_amount: int = Field(..., gt=0)
    refund_reason: RefundReason
    refund_method: RefundMethod
    items: List[RefundItemCreate]
    notes: Optional[str] = None
    issue_credit_note: bool = False

class RefundResponse(BaseSchema):
    id: str
    refund_number: str
    sale_id: str
    invoice_number: str
    refund_date: datetime
    refund_amount: int
    refund_reason: RefundReason
    refund_method: RefundMethod
    refund_status: RefundStatus
    is_partial: bool
    items: List[RefundItemResponse]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

class RefundApprove(BaseSchema):
    approved: bool = True
    notes: Optional[str] = None

class RefundProcess(BaseSchema):
    transaction_id: Optional[str] = None
    bank_reference: Optional[str] = None
    notes: Optional[str] = None

class RefundStats(BaseSchema):
    total_refunds: int
    total_refund_amount: int
    avg_refund_amount: int
    refund_rate: float
    top_refund_reasons: Dict[str, int]
    monthly_refunds: List[Dict[str, Any]]

# =========================
# APPOINTMENT SCHEMAS
# =========================
class AppointmentBase(BaseSchema):
    client_id: str
    employee_id: str
    service_type: str = Field(..., max_length=100)
    appointment_date: datetime
    duration: int = Field(60, ge=15)
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None
    total_amount: int = Field(0, ge=0)  
    paid_amount: int = Field(0, ge=0)

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseSchema):
    employee_id: Optional[str] = None
    service_type: Optional[str] = Field(None, max_length=100)
    appointment_date: Optional[datetime] = None
    duration: Optional[int] = Field(None, ge=15)
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    total_amount: Optional[Decimal] = Field(None, ge=0)
    paid_amount: Optional[Decimal] = Field(None, ge=0)

class AppointmentResponse(AppointmentBase):
    id: str
    client_name: str
    created_at: datetime
    updated_at: datetime


// frontend\src\components\common\Badge.jsx
import React from 'react';

const Badge = ({ children, variant = "default", className = "", ...props }) => {
  const variantClasses = {
    default: "bg-gray-100 text-gray-800 border border-gray-200",
    primary: "bg-purple-100 text-purple-800 border border-purple-200",
    secondary: "bg-blue-100 text-blue-800 border border-blue-200",
    success: "bg-green-100 text-green-800 border border-green-200",
    warning: "bg-amber-100 text-amber-800 border border-amber-200",
    destructive: "bg-red-100 text-red-800 border border-red-200",
    outline: "border border-gray-300 text-gray-700"
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};

export default Badge;

// frontend\src\components\common\ConfirmationModal.jsx
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton,
  Alert,
} from '@mui/material';
import { Close, Warning, CheckCircle, Error } from '@mui/icons-material';

const ConfirmationModal = ({
  open,
  onClose,
  onConfirm,
  title = 'Confirmation',
  message = 'Êtes-vous sûr de vouloir effectuer cette action ?',
  confirmText = 'Confirmer',
  cancelText = 'Annuler',
  severity = 'warning',
  loading = false,
  maxWidth = 'sm',
  children,
}) => {
  const getIcon = () => {
    switch (severity) {
      case 'error':
        return <Error color="error" />;
      case 'success':
        return <CheckCircle color="success" />;
      case 'info':
        return <Error color="info" />;
      default:
        return <Warning color="warning" />;
    }
  };

  const getColor = () => {
    switch (severity) {
      case 'error':
        return 'error';
      case 'success':
        return 'success';
      case 'info':
        return 'info';
      default:
        return 'warning';
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={maxWidth}
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
        },
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getIcon()}
            <Typography variant="h6" fontWeight="bold">
              {title}
            </Typography>
          </Box>
          <IconButton
            onClick={onClose}
            size="small"
            disabled={loading}
          >
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Alert
          severity={severity}
          variant="outlined"
          sx={{ mb: 2, borderRadius: 2 }}
        >
          {message}
        </Alert>

        {children && (
          <Box sx={{ mt: 2 }}>
            {children}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button
          onClick={onClose}
          disabled={loading}
          variant="outlined"
          sx={{ minWidth: 100 }}
        >
          {cancelText}
        </Button>
        <Button
          onClick={onConfirm}
          disabled={loading}
          variant="contained"
          color={getColor()}
          sx={{ minWidth: 100 }}
        >
          {loading ? 'Chargement...' : confirmText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmationModal;

// frontend/src/components/common/DataTable.jsx
import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Paper,
  Skeleton,
  Box,
} from '@mui/material';

export default function DataTable({
  rows = [],
  columns = [],
  loading = false,
  defaultSortBy = '',
  defaultSortOrder = 'asc',
  onRowClick,
  pageSize = 10,
  rowsPerPageOptions = [5, 10, 25, 50],
}) {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(pageSize);
  const [orderBy, setOrderBy] = useState(defaultSortBy);
  const [order, setOrder] = useState(defaultSortOrder);

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const sortedRows = React.useMemo(() => {
    if (!orderBy) return rows;
    return rows.sort((a, b) => {
      const aVal = a[orderBy];
      const bVal = b[orderBy];
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return order === 'asc' ? aVal - bVal : bVal - aVal;
      }
      const aStr = String(aVal || '').toLowerCase();
      const bStr = String(bVal || '').toLowerCase();
      if (aStr < bStr) return order === 'asc' ? -1 : 1;
      if (aStr > bStr) return order === 'asc' ? 1 : -1;
      return 0;
    });
  }, [rows, orderBy, order]);

  const paginatedRows = sortedRows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  if (loading) {
    return (
      <TableContainer component={Paper} sx={{ borderRadius: 3, overflow: 'hidden' }}>
        <Table>
          <TableHead>
            <TableRow>
              {columns.map((col) => (
                <TableCell key={col.field}>
                  <Skeleton variant="text" width={80} />
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {[...Array(5)].map((_, i) => (
              <TableRow key={i}>
                {columns.map((col) => (
                  <TableCell key={col.field}>
                    <Skeleton variant="text" width="100%" />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  return (
    <Paper sx={{ borderRadius: 3, overflow: 'hidden', boxShadow: 3 }}>
      <TableContainer>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell
                  key={column.field}
                  sortDirection={orderBy === column.field ? order : false}
                  sx={{ fontWeight: 600, bgcolor: 'background.paper' }}
                >
                  {column.sortable ? (
                    <TableSortLabel
                      active={orderBy === column.field}
                      direction={orderBy === column.field ? order : 'asc'}
                      onClick={() => handleRequestSort(column.field)}
                    >
                      {column.headerName || column.field}
                    </TableSortLabel>
                  ) : (
                    column.headerName || column.field
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedRows.map((row, index) => (
              <TableRow
                key={row.id || index}
                hover
                onClick={() => onRowClick && onRowClick(row)}
                sx={{ cursor: onRowClick ? 'pointer' : 'default' }}
              >
                {columns.map((column) => (
                  <TableCell key={column.field}>
                    {column.renderCell ? column.renderCell({ row }) : row[column.field]}
                  </TableCell>
                ))}
              </TableRow>
            ))}
            {paginatedRows.length === 0 && (
              <TableRow>
                <TableCell colSpan={columns.length} align="center" sx={{ py: 6 }}>
                  Aucune donnée à afficher
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={rowsPerPageOptions}
        component="div"
        count={rows.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={(e, newPage) => setPage(newPage)}
        onRowsPerPageChange={(e) => {
          setRowsPerPage(parseInt(e.target.value, 10));
          setPage(0);
        }}
        labelRowsPerPage="Lignes par page"
        labelDisplayedRows={({ from, to, count }) => `${from}–${to} sur ${count}`}
      />
    </Paper>
  );
}

// frontend\src\components\common\ErrorBoundary.jsx
import React from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import { ErrorOutline, Refresh } from '@mui/icons-material';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo,
    });
    
    // Log error to external service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
    
    // Optionally reset app state
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <Container maxWidth="md">
          <Box
            sx={{
              minHeight: '100vh',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              p: 3,
              textAlign: 'center',
            }}
          >
            <Box
              sx={{
                width: 120,
                height: 120,
                borderRadius: '50%',
                backgroundColor: 'error.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 3,
              }}
            >
              <ErrorOutline sx={{ fontSize: 60, color: 'error.main' }} />
            </Box>

            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Oups ! Une erreur est survenue
            </Typography>
            
            <Typography variant="body1" color="text.secondary" paragraph>
              Nous rencontrons des difficultés techniques. Veuillez réessayer ou contacter le support si le problème persiste.
            </Typography>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <Box
                sx={{
                  mt: 3,
                  p: 2,
                  backgroundColor: 'background.paper',
                  borderRadius: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  maxWidth: '100%',
                  overflow: 'auto',
                  textAlign: 'left',
                }}
              >
                <Typography variant="caption" color="text.secondary">
                  <strong>Erreur:</strong> {this.state.error.toString()}
                </Typography>
                {this.state.errorInfo && (
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                    <strong>Stack:</strong> {this.state.errorInfo.componentStack}
                  </Typography>
                )}
              </Box>
            )}

            <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={this.handleReset}
              >
                Réessayer
              </Button>
              
              <Button
                variant="outlined"
                onClick={() => window.location.reload()}
              >
                Recharger la page
              </Button>
              
              <Button
                variant="text"
                onClick={() => window.location.href = '/'}
              >
                Retour à l'accueil
              </Button>
            </Box>

            <Typography variant="caption" color="text.secondary" sx={{ mt: 4 }}>
              Code d'erreur: ERR_{Date.now().toString(36).toUpperCase()}
            </Typography>
          </Box>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

// Functional component wrapper for easier use
export const withErrorBoundary = (Component, FallbackComponent) => {
  return (props) => (
    <ErrorBoundary FallbackComponent={FallbackComponent}>
      <Component {...props} />
    </ErrorBoundary>
  );
};

// frontend\src\components\common\LoadingSpinner.jsx
import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { motion } from 'framer-motion';

const LoadingSpinner = ({ message = 'Chargement...', size = 40 }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 200,
        gap: 2,
      }}
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      >
        <CircularProgress
          size={size}
          sx={{
            color: 'primary.main',
          }}
        />
      </motion.div>
      {message && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 1 }}
        >
          {message}
        </Typography>
      )}
    </Box>
  );
};

export const InlineLoader = () => (
  <Box
    sx={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 1,
    }}
  >
    <CircularProgress size={16} />
    <Typography variant="caption" color="text.secondary">
      Chargement...
    </Typography>
  </Box>
);

export default LoadingSpinner;

// frontend\src\components\common\SearchBar.jsx
import React, { useState } from 'react';
import {
  TextField,
  InputAdornment,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Box,
} from '@mui/material';
import {
  Search,
  Clear,
  FilterList,
  Tune,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const SearchBar = ({ onSearch, placeholder = "Rechercher..." }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [filters, setFilters] = useState([]);

  const handleSearch = (value) => {
    setSearchTerm(value);
    if (onSearch) {
      onSearch(value);
    }
  };

  const handleClear = () => {
    setSearchTerm('');
    if (onSearch) {
      onSearch('');
    }
  };

  const handleFilterClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setAnchorEl(null);
  };

  const availableFilters = [
    { label: 'En rupture', value: 'out_of_stock' },
    { label: 'Stock faible', value: 'low_stock' },
    { label: 'Promotions', value: 'discount' },
    { label: 'Nouveautés', value: 'new' },
  ];

  const toggleFilter = (filter) => {
    if (filters.includes(filter.value)) {
      setFilters(filters.filter(f => f !== filter.value));
    } else {
      setFilters([...filters, filter.value]);
    }
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <motion.div
        initial={{ width: 0, opacity: 0 }}
        animate={{ width: '100%', opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <TextField
          fullWidth
          size="small"
          placeholder={placeholder}
          value={searchTerm}
          onChange={(e) => handleSearch(e.target.value)}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              backgroundColor: 'background.paper',
              transition: 'all 0.2s',
              '&:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.02)',
              },
              '&.Mui-focused': {
                backgroundColor: 'white',
                boxShadow: '0 0 0 3px rgba(138, 43, 226, 0.1)',
              },
            },
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search color="action" />
              </InputAdornment>
            ),
            endAdornment: searchTerm && (
              <InputAdornment position="end">
                <IconButton
                  size="small"
                  onClick={handleClear}
                  edge="end"
                >
                  <Clear fontSize="small" />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      </motion.div>

      <IconButton
        size="small"
        onClick={handleFilterClick}
        sx={{
          backgroundColor: filters.length > 0 ? 'primary.light' : 'transparent',
          color: filters.length > 0 ? 'white' : 'text.secondary',
          '&:hover': {
            backgroundColor: filters.length > 0 ? 'primary.main' : 'action.hover',
          },
        }}
      >
        {filters.length > 0 ? <Tune /> : <FilterList />}
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleFilterClose}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: 200,
            borderRadius: 2,
          },
        }}
      >
        {availableFilters.map((filter) => (
          <MenuItem
            key={filter.value}
            onClick={() => toggleFilter(filter)}
            selected={filters.includes(filter.value)}
          >
            {filter.label}
          </MenuItem>
        ))}
      </Menu>

      {filters.length > 0 && (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          {filters.map((filterValue) => {
            const filter = availableFilters.find(f => f.value === filterValue);
            return (
              <Chip
                key={filterValue}
                label={filter?.label}
                size="small"
                onDelete={() => toggleFilter(filter)}
                color="primary"
                variant="outlined"
              />
            );
          })}
        </Box>
      )}
    </Box>
  );
};

export default SearchBar;

// frontend/src/components/products/StockMovement.jsx
import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Chip,
  Stack,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress,
  Grid,
  Tooltip,
  Paper,
  InputAdornment,
  Tabs,
  Tab,
  Fab,
  Zoom,
  Fade,
  Grow,
} from '@mui/material';
import {
  Add as AddIcon,
  Inventory as InventoryIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  SwapHoriz as SwapHorizIcon,
  History as HistoryIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  AttachMoney as MoneyIcon,
  FilterList as FilterListIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  Download as DownloadIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { DataGrid } from '@mui/x-data-grid';
import { frFR } from '@mui/x-data-grid/locales';
import { formatCurrency, formatDate } from '../../utils/formatters';
import { productService } from '../../services/products';
import { STOCK_MOVEMENT_TYPES } from '../../constants/config';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 24,
    },
  },
};

const COLORS = ['#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#8A2BE2'];

const StockMovement = ({ productId, productName, productPurchasePrice, onMovementCreated }) => {
  const queryClient = useQueryClient();
  const [openDialog, setOpenDialog] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [newMovement, setNewMovement] = useState({
    product_id: productId,
    movement_type: 'IN',
    quantity: 1,
    unit_cost: productPurchasePrice ? productPurchasePrice.toString() : '',
    reason: '',
    reference: '',
    supplier_id: '',
    notes: '',
    expiration_date: '',
  });

  // Effet pour mettre à jour le coût unitaire selon le type
  useEffect(() => {
    if (['IN', 'RETURN'].includes(newMovement.movement_type)) {
      setNewMovement(prev => ({
        ...prev,
        unit_cost: productPurchasePrice ? productPurchasePrice.toString() : ''
      }));
    } else {
      setNewMovement(prev => ({ ...prev, unit_cost: '' }));
    }
  }, [newMovement.movement_type, productPurchasePrice]);

  // Charger les mouvements
  const {
    data: movements = [],
    isLoading,
    error,
    refetch,
  } = useQuery(
    ['productMovements', productId],
    () => productService.getProductMovements(productId),
    {
      enabled: !!productId,
      refetchOnWindowFocus: false,
      select: (data) => {
        return data.sort((a, b) => new Date(b.movement_date) - new Date(a.movement_date));
      },
    }
  );

  // Mutation pour créer un mouvement
  const createMovementMutation = useMutation(
    (movementData) => productService.createStockMovement(movementData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['productMovements', productId]);
        toast.success('Mouvement enregistré avec succès');
        setOpenDialog(false);
        resetForm();
        if (onMovementCreated) onMovementCreated();
      },
      onError: (err) => {
        toast.error(err.response?.data?.detail || 'Erreur lors de la création');
      },
    }
  );

  // Calculs statistiques
  const stats = useMemo(() => {
    let stockIn = 0,
      stockOut = 0,
      totalValue = 0,
      lastMovement = null;
    const monthlyData = {};
    const typeCount = { IN: 0, OUT: 0, ADJUSTMENT: 0, RETURN: 0, DAMAGED: 0 };

    movements.forEach((m) => {
      const month = new Date(m.movement_date).toLocaleString('default', {
        month: 'short',
        year: 'numeric',
      });
      if (!monthlyData[month]) {
        monthlyData[month] = { month, IN: 0, OUT: 0, ADJUSTMENT: 0, RETURN: 0, DAMAGED: 0 };
      }
      monthlyData[month][m.movement_type] += m.quantity;

      if (['IN', 'RETURN', 'ADJUSTMENT'].includes(m.movement_type)) {
        stockIn += m.quantity;
        totalValue += m.total_cost || m.quantity * (m.unit_cost || 0);
      } else {
        stockOut += m.quantity;
        totalValue -= m.total_cost || m.quantity * (m.unit_cost || 0);
      }

      typeCount[m.movement_type]++;

      if (!lastMovement || new Date(m.movement_date) > new Date(lastMovement.movement_date)) {
        lastMovement = m;
      }
    });

    const currentStock = stockIn - stockOut;
    const stockValue = totalValue;

    return {
      currentStock,
      stockValue,
      stockIn,
      stockOut,
      lastMovement,
      monthlyData: Object.values(monthlyData).sort(
        (a, b) => new Date(a.month) - new Date(b.month)
      ),
      typeCount,
    };
  }, [movements]);

  // Mouvements filtrés
  const filteredMovements = useMemo(() => {
    return movements.filter((m) => {
      const matchesSearch =
        searchTerm === '' ||
        m.reason?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.reference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.notes?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = filterType === 'all' || m.movement_type === filterType;
      const matchesDate =
        (!dateRange.start || new Date(m.movement_date) >= new Date(dateRange.start)) &&
        (!dateRange.end || new Date(m.movement_date) <= new Date(dateRange.end));
      return matchesSearch && matchesType && matchesDate;
    });
  }, [movements, searchTerm, filterType, dateRange]);

  const resetForm = () => {
    setNewMovement({
      product_id: productId,
      movement_type: 'IN',
      quantity: 1,
      unit_cost: productPurchasePrice ? productPurchasePrice.toString() : '',
      reason: '',
      reference: '',
      supplier_id: '',
      notes: '',
      expiration_date: '',
    });
  };

const handleCreateMovement = () => {
  if (newMovement.quantity <= 0) {
    toast.error('La quantité doit être supérieure à 0');
    return;
  }
  
  // Préparer les données en supprimant les champs vides
  const movementData = {
    product_id: newMovement.product_id,
    movement_type: newMovement.movement_type,
    quantity: newMovement.quantity,
  };
  
  if (newMovement.unit_cost) {
    movementData.unit_cost = parseFloat(newMovement.unit_cost);
  }
  if (newMovement.reason) {
    movementData.reason = newMovement.reason;
  }
  if (newMovement.reference) {
    movementData.reference = newMovement.reference;
  }
  if (newMovement.supplier_id) {
    movementData.supplier_id = newMovement.supplier_id;
  }
  if (newMovement.notes) {
    movementData.notes = newMovement.notes;
  }
  if (newMovement.expiration_date) {
    movementData.expiration_date = newMovement.expiration_date;
  }
  
  createMovementMutation.mutate(movementData);
};

  const handleInputChange = (field, value) => {
    setNewMovement((prev) => ({ ...prev, [field]: value }));
  };

  const getStockStatusColor = (stock) => {
    if (stock <= 0) return 'error';
    if (stock <= 5) return 'warning';
    return 'success';
  };

  // Colonnes pour la DataGrid
  const columns = [
    {
      field: 'movement_date',
      headerName: 'Date',
      width: 160,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2">{formatDate(params.value, 'short')}</Typography>
          <Typography variant="caption" color="text.secondary">
            {formatDate(params.value, 'relative')}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'movement_type',
      headerName: 'Type',
      width: 130,
      renderCell: (params) => {
        const type = params.value;
        const config = {
          IN: { label: 'Entrée', color: 'success', icon: <ArrowUpwardIcon fontSize="small" /> },
          OUT: { label: 'Sortie', color: 'error', icon: <ArrowDownwardIcon fontSize="small" /> },
          ADJUSTMENT: { label: 'Ajustement', color: 'warning', icon: <SwapHorizIcon fontSize="small" /> },
          RETURN: { label: 'Retour', color: 'info', icon: <RefreshIcon fontSize="small" /> },
          DAMAGED: { label: 'Détérioré', color: 'error', icon: <DeleteIcon fontSize="small" /> },
        }[type] || { label: type, color: 'default', icon: <InventoryIcon fontSize="small" /> };

        return (
          <Chip
            icon={config.icon}
            label={config.label}
            size="small"
            color={config.color}
            variant="outlined"
            sx={{ fontWeight: 'medium', borderRadius: 2 }}
          />
        );
      },
    },
    {
      field: 'quantity',
      headerName: 'Quantité',
      width: 110,
      renderCell: (params) => {
        const isPositive = ['IN', 'RETURN', 'ADJUSTMENT'].includes(params.row.movement_type);
        return (
          <Typography
            variant="body2"
            color={isPositive ? 'success.main' : 'error.main'}
            fontWeight="bold"
          >
            {isPositive ? '+' : '-'}
            {params.value}
          </Typography>
        );
      },
    },
    {
      field: 'unit_cost',
      headerName: 'Coût unitaire',
      width: 130,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value ? formatCurrency(params.value) : '—'}
        </Typography>
      ),
    },
    {
      field: 'total_cost',
      headerName: 'Coût total',
      width: 130,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="medium">
          {params.value ? formatCurrency(params.value) : '—'}
        </Typography>
      ),
    },
    {
      field: 'reason',
      headerName: 'Raison',
      width: 200,
      renderCell: (params) => (
        <Tooltip title={params.value || ''}>
          <Typography variant="body2" noWrap>
            {params.value || '—'}
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: 'reference',
      headerName: 'Référence',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2" color="text.secondary">
          {params.value || '—'}
        </Typography>
      ),
    },
    {
      field: 'created_at',
      headerName: 'Enregistré le',
      width: 150,
      renderCell: (params) => (
        <Typography variant="caption" color="text.secondary">
          {formatDate(params.value, 'relative')}
        </Typography>
      ),
    },
  ];

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      {/* En-tête avec statistiques */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <motion.div variants={itemVariants}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                borderRadius: 4,
                background: 'linear-gradient(135deg, #8A2BE2 0%, #9D4EDD 100%)',
                color: 'white',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <Box sx={{ position: 'absolute', top: -10, right: -10, opacity: 0.1 }}>
                <InventoryIcon sx={{ fontSize: 100 }} />
              </Box>
              <Typography variant="overline" sx={{ opacity: 0.8 }}>
                Stock actuel
              </Typography>
              <Typography variant="h3" fontWeight="bold">
                {stats.currentStock}
              </Typography>
              <Chip
                label={stats.currentStock <= 0 ? 'Rupture' : stats.currentStock <= 5 ? 'Faible' : 'Normal'}
                size="small"
                color={getStockStatusColor(stats.currentStock)}
                sx={{ mt: 1, backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }}
              />
            </Paper>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div variants={itemVariants}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                borderRadius: 4,
                background: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
                color: 'white',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <Box sx={{ position: 'absolute', top: -10, right: -10, opacity: 0.1 }}>
                <MoneyIcon sx={{ fontSize: 100 }} />
              </Box>
              <Typography variant="overline" sx={{ opacity: 0.8 }}>
                Valeur du stock
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {formatCurrency(stats.stockValue)}
              </Typography>
            </Paper>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div variants={itemVariants}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                borderRadius: 4,
                background: 'linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)',
                color: 'white',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <Box sx={{ position: 'absolute', top: -10, right: -10, opacity: 0.1 }}>
                <ArrowUpwardIcon sx={{ fontSize: 100 }} />
              </Box>
              <Typography variant="overline" sx={{ opacity: 0.8 }}>
                Entrées totales
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {stats.stockIn}
              </Typography>
            </Paper>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div variants={itemVariants}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                borderRadius: 4,
                background: 'linear-gradient(135deg, #EF4444 0%, #F87171 100%)',
                color: 'white',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <Box sx={{ position: 'absolute', top: -10, right: -10, opacity: 0.1 }}>
                <ArrowDownwardIcon sx={{ fontSize: 100 }} />
              </Box>
              <Typography variant="overline" sx={{ opacity: 0.8 }}>
                Sorties totales
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {stats.stockOut}
              </Typography>
            </Paper>
          </motion.div>
        </Grid>
      </Grid>

      {/* Onglets : Historique / Graphiques avec bouton Nouveau mouvement */}
      <Card sx={{ mb: 3, borderRadius: 4, overflow: 'hidden' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', px: 3, pt: 2 }}>
          <Tabs
            value={activeTab}
            onChange={(e, v) => setActiveTab(v)}
            sx={{ '& .MuiTab-root': { minWidth: 120 } }}
          >
            <Tab icon={<HistoryIcon />} label="Historique" iconPosition="start" />
            <Tab icon={<TimelineIcon />} label="Tendances" iconPosition="start" />
            <Tab icon={<PieChart />} label="Répartition" iconPosition="start" />
          </Tabs>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
            sx={{ borderRadius: 8, px: 3 }}
          >
            Nouveau mouvement
          </Button>
        </Box>
        <Divider />

        <CardContent>
          {/* Onglet Historique */}
          {activeTab === 0 && (
            <Fade in timeout={500}>
              <Box>
                {/* Barre de filtres */}
                <Stack direction="row" spacing={2} sx={{ mb: 3 }} alignItems="center">
                  <TextField
                    size="small"
                    placeholder="Rechercher..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon fontSize="small" />
                        </InputAdornment>
                      ),
                      endAdornment: searchTerm && (
                        <InputAdornment position="end">
                          <IconButton size="small" onClick={() => setSearchTerm('')}>
                            <ClearIcon fontSize="small" />
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                    sx={{ minWidth: 250 }}
                  />

                  <FormControl size="small" sx={{ minWidth: 150 }}>
                    <InputLabel>Type</InputLabel>
                    <Select
                      value={filterType}
                      label="Type"
                      onChange={(e) => setFilterType(e.target.value)}
                    >
                      <MenuItem value="all">Tous</MenuItem>
                      {Object.entries(STOCK_MOVEMENT_TYPES).map(([key, label]) => (
                        <MenuItem key={key} value={key}>
                          {label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <TextField
                    size="small"
                    type="date"
                    label="Du"
                    value={dateRange.start}
                    onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                    InputLabelProps={{ shrink: true }}
                  />
                  <TextField
                    size="small"
                    type="date"
                    label="Au"
                    value={dateRange.end}
                    onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                    InputLabelProps={{ shrink: true }}
                  />

                  <Box sx={{ flex: 1 }} />

                  <Tooltip title="Exporter">
                    <IconButton onClick={() => {}}>
                      <DownloadIcon />
                    </IconButton>
                  </Tooltip>
                </Stack>

                {/* Tableau */}
                {isLoading ? (
                  <Box sx={{ p: 4, textAlign: 'center' }}>
                    <LinearProgress sx={{ mb: 2 }} />
                    <Typography variant="body2" color="text.secondary">
                      Chargement de l'historique...
                    </Typography>
                  </Box>
                ) : error ? (
                  <Alert severity="error" sx={{ borderRadius: 2 }}>
                    {error.message}
                  </Alert>
                ) : filteredMovements.length === 0 ? (
                  <Box sx={{ p: 6, textAlign: 'center' }}>
                    <InventoryIcon sx={{ fontSize: 80, color: 'grey.400', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      Aucun mouvement trouvé
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {searchTerm || filterType !== 'all' || dateRange.start
                        ? 'Essayez de modifier vos filtres'
                        : 'Commencez par créer un mouvement'}
                    </Typography>
                  </Box>
                ) : (
                  <Box sx={{ height: 450, width: '100%' }}>
                    <DataGrid
                      rows={filteredMovements}
                      columns={columns}
                      pageSize={10}
                      rowsPerPageOptions={[10, 25, 50, 100]}
                      disableSelectionOnClick
                      loading={isLoading}
                      localeText={frFR.components.MuiDataGrid.defaultProps.localeText}
                      sx={{
                        border: 'none',
                        '& .MuiDataGrid-columnHeaders': {
                          backgroundColor: 'background.paper',
                          borderBottom: '2px solid',
                          borderColor: 'divider',
                        },
                      }}
                    />
                  </Box>
                )}
              </Box>
            </Fade>
          )}

          {/* Onglet Tendances */}
          {activeTab === 1 && (
            <Fade in timeout={500}>
              <Box sx={{ height: 400 }}>
                {stats.monthlyData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={stats.monthlyData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="colorIn" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10B981" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorOut" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#EF4444" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <ChartTooltip />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="IN"
                        stroke="#10B981"
                        fillOpacity={1}
                        fill="url(#colorIn)"
                        name="Entrées"
                      />
                      <Area
                        type="monotone"
                        dataKey="OUT"
                        stroke="#EF4444"
                        fillOpacity={1}
                        fill="url(#colorOut)"
                        name="Sorties"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography color="text.secondary">
                      Pas assez de données pour afficher les tendances
                    </Typography>
                  </Box>
                )}
              </Box>
            </Fade>
          )}

          {/* Onglet Répartition */}
          {activeTab === 2 && (
            <Fade in timeout={500}>
              <Box sx={{ height: 400, display: 'flex', justifyContent: 'center' }}>
                {movements.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={Object.entries(stats.typeCount)
                          .filter(([_, count]) => count > 0)
                          .map(([type, count]) => ({
                            name: STOCK_MOVEMENT_TYPES[type] || type,
                            value: count,
                          }))}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(entry) => `${entry.name}: ${entry.value}`}
                        outerRadius={150}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {Object.entries(stats.typeCount)
                          .filter(([_, count]) => count > 0)
                          .map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                      </Pie>
                      <ChartTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography color="text.secondary">
                      Aucune donnée de répartition
                    </Typography>
                  </Box>
                )}
              </Box>
            </Fade>
          )}
        </CardContent>
      </Card>

      {/* Bouton flottant (optionnel - peut être supprimé) */}
      {/* <Zoom in timeout={500}>
        <Fab
          color="primary"
          aria-label="add"
          sx={{
            position: 'fixed',
            bottom: 32,
            right: 32,
            bgcolor: 'primary.main',
            '&:hover': { bgcolor: 'primary.dark', transform: 'scale(1.1)' },
            transition: 'all 0.2s ease',
          }}
          onClick={() => setOpenDialog(true)}
        >
          <AddIcon />
        </Fab>
      </Zoom> */}

      {/* Dialog pour créer un mouvement */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 4,
            overflow: 'hidden',
          },
        }}
        TransitionComponent={Grow}
      >
        <DialogTitle sx={{ bgcolor: 'primary.main', color: 'white', py: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AddIcon />
            <Typography variant="h6">Nouveau mouvement de stock</Typography>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ mt: 2 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Type de mouvement</InputLabel>
                <Select
                  value={newMovement.movement_type}
                  label="Type de mouvement"
                  onChange={(e) => handleInputChange('movement_type', e.target.value)}
                >
                  {Object.entries(STOCK_MOVEMENT_TYPES).map(([key, label]) => (
                    <MenuItem key={key} value={key}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {key === 'IN' && <ArrowUpwardIcon color="success" />}
                        {key === 'OUT' && <ArrowDownwardIcon color="error" />}
                        {key === 'ADJUSTMENT' && <SwapHorizIcon color="warning" />}
                        {key === 'RETURN' && <RefreshIcon color="info" />}
                        {key === 'DAMAGED' && <DeleteIcon color="error" />}
                        {label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                label="Quantité"
                type="number"
                fullWidth
                value={newMovement.quantity}
                onChange={(e) => handleInputChange('quantity', parseInt(e.target.value) || 0)}
                InputProps={{
                  inputProps: { min: 1 },
                  startAdornment: (
                    <InputAdornment position="start">
                      <InventoryIcon color="action" />
                    </InputAdornment>
                  ),
                }}
                helperText="Quantité à ajouter ou retirer"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                label="Coût unitaire (FCFA)"
                type="number"
                fullWidth
                value={newMovement.unit_cost}
                onChange={(e) => handleInputChange('unit_cost', parseFloat(e.target.value) || '')}
                InputProps={{
                  inputProps: { min: 0, step: 0.01 },
                  startAdornment: (
                    <InputAdornment position="start">
                      <MoneyIcon color="action" />
                    </InputAdornment>
                  ),
                }}
                helperText="Laissez vide pour utiliser le coût d'achat"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                label="Raison"
                fullWidth
                value={newMovement.reason}
                onChange={(e) => handleInputChange('reason', e.target.value)}
                placeholder="Ex: Réapprovisionnement, Vente, etc."
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <HistoryIcon color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                label="Référence"
                fullWidth
                value={newMovement.reference}
                onChange={(e) => handleInputChange('reference', e.target.value)}
                placeholder="Numéro de commande, facture..."
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <FilterListIcon color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                label="Date d'expiration"
                type="date"
                fullWidth
                value={newMovement.expiration_date}
                onChange={(e) => handleInputChange('expiration_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <TimelineIcon color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                label="Notes"
                fullWidth
                multiline
                rows={3}
                value={newMovement.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                placeholder="Informations complémentaires"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start" sx={{ alignSelf: 'flex-start', mt: 1 }}>
                      <HistoryIcon color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
          </Grid>

          {/* Résumé du mouvement */}
          {newMovement.quantity > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Alert
                severity="info"
                icon={<MoneyIcon />}
                sx={{
                  mt: 3,
                  borderRadius: 3,
                  border: '1px solid',
                  borderColor: 'info.light',
                }}
              >
                <Typography variant="subtitle2" gutterBottom>
                  Résumé du mouvement
                </Typography>
                <Stack direction="row" spacing={4} flexWrap="wrap">
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Type
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {STOCK_MOVEMENT_TYPES[newMovement.movement_type]}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Quantité
                    </Typography>
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color={
                        ['IN', 'RETURN', 'ADJUSTMENT'].includes(newMovement.movement_type)
                          ? 'success.main'
                          : 'error.main'
                      }
                    >
                      {['IN', 'RETURN', 'ADJUSTMENT'].includes(newMovement.movement_type) ? '+' : '-'}
                      {newMovement.quantity}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Coût total estimé
                    </Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatCurrency(newMovement.quantity * (newMovement.unit_cost || 0))}
                    </Typography>
                  </Box>
                </Stack>
              </Alert>
            </motion.div>
          )}
        </DialogContent>

        <DialogActions sx={{ p: 3, pt: 0 }}>
          <Button onClick={() => setOpenDialog(false)} disabled={createMovementMutation.isLoading}>
            Annuler
          </Button>
          <Button
            variant="contained"
            onClick={handleCreateMovement}
            disabled={createMovementMutation.isLoading || newMovement.quantity <= 0}
            startIcon={
              createMovementMutation.isLoading ? (
                <LinearProgress size={20} color="inherit" />
              ) : newMovement.movement_type === 'IN' ? (
                <ArrowUpwardIcon />
              ) : (
                <ArrowDownwardIcon />
              )
            }
            sx={{
              bgcolor: 'primary.main',
              '&:hover': { bgcolor: 'primary.dark' },
            }}
          >
            {createMovementMutation.isLoading ? 'Enregistrement...' : 'Enregistrer le mouvement'}
          </Button>
        </DialogActions>
      </Dialog>
    </motion.div>
  );
};

export default StockMovement;

// frontend/src/components/products/ProductStockModal.jsx
import React from 'react';
import { Dialog, DialogTitle, DialogContent, IconButton, Box, Typography } from '@mui/material';
import { Close as CloseIcon, Inventory as InventoryIcon } from '@mui/icons-material'; // ✅ Import manquant ajouté
import StockMovement from './StockMovement';
import { motion } from 'framer-motion';

const ProductStockModal = ({ open, onClose, product }) => {
  if (!product) return null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 4,
          overflow: 'hidden',
        },
      }}
      TransitionComponent={motion.div}
      transitionDuration={400}
    >
      <DialogTitle sx={{ bgcolor: 'background.paper', borderBottom: 1, borderColor: 'divider', py: 2 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h5" fontWeight="bold" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <InventoryIcon color="primary" />
            Gestion du stock - {product.name}
          </Typography>
          <IconButton onClick={onClose} edge="end">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent dividers sx={{ p: 3, bgcolor: 'background.default' }}>
        <StockMovement
          productId={product.id}
          productName={product.name}
          productPurchasePrice={product.purchase_price} // <-- Ajout
          onMovementCreated={onClose}
        />
      </DialogContent>
    </Dialog>
  );
};

export default ProductStockModal;

import React from 'react';
import { Grid, Card, CardContent, Typography, Box } from '@mui/material';
import { Inventory, Warning, Error, AttachMoney } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { formatCurrency } from '../../utils/formatters';

const StatCard = ({ icon, label, value, color, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.5 }}
  >
    <Card
      sx={{
        height: '100%',
        background: (theme) => `linear-gradient(135deg, ${theme.palette[color].light} 0%, ${theme.palette[color].main} 100%)`,
        color: 'white',
        borderRadius: 3,
        boxShadow: (theme) => `0 8px 16px ${theme.palette[color].light}40`,
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="caption" sx={{ opacity: 0.8 }}>
              {label}
            </Typography>
            <Typography variant="h4" fontWeight="bold">
              {value}
            </Typography>
          </Box>
          <Box
            sx={{
              p: 1.5,
              borderRadius: '50%',
              bgcolor: 'rgba(255,255,255,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  </motion.div>
);

export default function ProductStatsCards({ stats }) {
  return (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={<Inventory fontSize="large" />}
          label="Total produits"
          value={stats.totalProducts}
          color="primary"
          delay={0.1}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={<AttachMoney fontSize="large" />}
          label="Valeur du stock"
          value={formatCurrency(stats.stockValue)}
          color="success"
          delay={0.2}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={<Warning fontSize="large" />}
          label="Stock faible"
          value={stats.lowStockCount}
          color="warning"
          delay={0.3}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={<Error fontSize="large" />}
          label="Rupture"
          value={stats.outOfStockCount}
          color="error"
          delay={0.4}
        />
      </Grid>
    </Grid>
  );
}


// src/components/products/ProductForm.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  TextField,
  Button,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Chip,
  IconButton,
  Avatar,
  Autocomplete,
  LinearProgress,
  Alert,
  FormHelperText,
} from '@mui/material';
import Typography from '@mui/material/Typography';
import {
  AddPhotoAlternate,
  Delete,
  LocalOffer,
  Category,
  Inventory,
  AttachMoney,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { productService } from '../../services/products';
import toast from 'react-hot-toast';

const categories = [
    "Soins Visage",
    "Soins Corps",
    "Soins Capillaires",
    "Lait",
    "Crème",
    "Pommade",
    "Maquillage",
    "Déodorants",
    "Parfums",
    "Huiles",
    "Sérums",
    "Gommage",
    "Shampoing",
    "Mèches",
    "Accessoires",
];


const validationSchema = Yup.object({
  name: Yup.string().required('Le nom est requis'),
  category: Yup.string().required('La catégorie est requise'),
  brand: Yup.string(),
  purchase_price: Yup.number()
    .required('Le prix d\'achat est requis')
    .min(0, 'Le prix doit être positif'),
  selling_price: Yup.number()
    .required('Le prix de vente est requis')
    .min(0, 'Le prix doit être positif')
    .test(
      'greater-than-purchase',
      'Le prix de vente doit être supérieur au prix d\'achat',
      function (value) {
        const { purchase_price } = this.parent;
        return value > purchase_price;
      }
    ),
  alert_threshold: Yup.number()
    .required('Le seuil d\'alerte est requis')
    .min(0, 'Le seuil doit être positif'),
  sku: Yup.string(),
  barcode: Yup.string(),
  description: Yup.string(),
});

export default function ProductForm({ product, onSuccess, onCancel }) {
  const [uploading, setUploading] = useState(false);
  const [uploadedImages, setUploadedImages] = useState([]);
  const queryClient = useQueryClient();

  const { data: brands = [] } = useQuery(
    'product-brands',
    productService.getBrands,
    {
      staleTime: 1000 * 60 * 5,
    }
  );

  const isEdit = !!product;

  const createMutation = useMutation(
    (data) => productService.createProduct(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('products');
        toast.success('Produit créé avec succès');
        onSuccess();
      },
      onError: (error) => {
        toast.error('Erreur lors de la création');
      },
    }
  );

  const updateMutation = useMutation(
    (data) => productService.updateProduct(product.id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('products');
        toast.success('Produit mis à jour avec succès');
        onSuccess();
      },
      onError: (error) => {
        toast.error('Erreur lors de la mise à jour');
      },
    }
  );

  const formik = useFormik({
    initialValues: {
      name: product?.name || '',
      category: product?.category || '',
      brand: product?.brand || '',
      purchase_price: product?.purchase_price || '',
      selling_price: product?.selling_price || '',
      alert_threshold: product?.alert_threshold || 10,
      sku: product?.sku || '',
      barcode: product?.barcode || '',
      description: product?.description || '',
      initial_stock: product?.current_stock || 0,
    },
    validationSchema,
    onSubmit: (values) => {
      if (isEdit) {
        updateMutation.mutate(values);
      } else {
        createMutation.mutate(values);
      }
    },
  });

  useEffect(() => {
    if (product?.images) {
      setUploadedImages(product.images);
    }
  }, [product]);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const productId = product?.id || 'new';
      const response = await productService.uploadProductImage(productId, formData);
      
      setUploadedImages([...uploadedImages, response.image]);
      toast.success('Image téléchargée avec succès');
    } catch (error) {
      toast.error('Erreur lors du téléchargement de l\'image');
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveImage = (index) => {
    setUploadedImages(uploadedImages.filter((_, i) => i !== index));
  };

  const calculateMargin = () => {
    const purchase = parseFloat(formik.values.purchase_price) || 0;
    const selling = parseFloat(formik.values.selling_price) || 0;
    
    if (purchase <= 0 || selling <= 0) return 0;
    
    const margin = ((selling - purchase) / purchase) * 100;
    return margin.toFixed(1);
  };

  const margin = calculateMargin();

  return (
    <Box component="form" onSubmit={formik.handleSubmit}>
      <Grid container spacing={3}>
        {/* Left Column - Basic Info */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nom du produit"
                name="name"
                value={formik.values.name}
                onChange={formik.handleChange}
                error={formik.touched.name && Boolean(formik.errors.name)}
                helperText={formik.touched.name && formik.errors.name}
                InputProps={{
                  startAdornment: (
                    <Inventory sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Catégorie</InputLabel>
                <Select
                  name="category"
                  value={formik.values.category}
                  onChange={formik.handleChange}
                  label="Catégorie"
                  startAdornment={
                    <Category sx={{ mr: 1, color: 'text.secondary' }} />
                  }
                >
                  {categories.map((category) => (
                    <MenuItem key={category} value={category}>
                      {category}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Autocomplete
                freeSolo
                options={brands}
                value={formik.values.brand || ''}
                onChange={(event, newValue) => {
                  formik.setFieldValue('brand', newValue || '');
                }}
                onInputChange={(event, newInputValue) => {
                  formik.setFieldValue('brand', newInputValue);
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Marque"
                    fullWidth
                    helperText="Choisissez ou tapez une nouvelle marque"
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Prix d'achat (FCFA)"
                name="purchase_price"
                type="number"
                value={formik.values.purchase_price}
                onChange={formik.handleChange}
                error={
                  formik.touched.purchase_price &&
                  Boolean(formik.errors.purchase_price)
                }
                helperText={
                  formik.touched.purchase_price && formik.errors.purchase_price
                }
                InputProps={{
                  startAdornment: (
                    <AttachMoney sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Prix de vente (FCFA)"
                name="selling_price"
                type="number"
                value={formik.values.selling_price}
                onChange={formik.handleChange}
                error={
                  formik.touched.selling_price &&
                  Boolean(formik.errors.selling_price)
                }
                helperText={
                  formik.touched.selling_price && formik.errors.selling_price
                }
                InputProps={{
                  startAdornment: (
                    <LocalOffer sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                }}
              />
            </Grid>

            {margin > 0 && (
              <Grid item xs={12}>
                <Alert
                  severity={margin >= 30 ? 'success' : margin >= 20 ? 'info' : 'warning'}
                  sx={{ borderRadius: 2 }}
                >
                  Marge bénéficiaire: <strong>{margin}%</strong>
                  {margin >= 30
                    ? ' - Excellente marge!'
                    : margin >= 20
                    ? ' - Bonne marge'
                    : ' - Marge faible, à revoir'}
                </Alert>
              </Grid>
            )}

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Seuil d'alerte stock"
                name="alert_threshold"
                type="number"
                value={formik.values.alert_threshold}
                onChange={formik.handleChange}
                error={
                  formik.touched.alert_threshold &&
                  Boolean(formik.errors.alert_threshold)
                }
                helperText={
                  formik.touched.alert_threshold && formik.errors.alert_threshold
                }
              />
            </Grid>

            {!isEdit && (
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Stock initial"
                  name="initial_stock"
                  type="number"
                  value={formik.values.initial_stock}
                  onChange={formik.handleChange}
                />
              </Grid>
            )}

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="SKU"
                name="sku"
                value={formik.values.sku}
                onChange={formik.handleChange}
                helperText="Code produit unique"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Code-barres"
                name="barcode"
                value={formik.values.barcode}
                onChange={formik.handleChange}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                name="description"
                multiline
                rows={4}
                value={formik.values.description}
                onChange={formik.handleChange}
                helperText="Description détaillée du produit"
              />
            </Grid>
          </Grid>
        </Grid>

        {/* Right Column - Images */}
        <Grid item xs={12} md={4}>
          <Box
            sx={{
              border: '2px dashed',
              borderColor: 'divider',
              borderRadius: 3,
              p: 3,
              textAlign: 'center',
              height: '100%',
            }}
          >
            <Typography variant="h6" gutterBottom>
              Images du produit
            </Typography>

            {uploading && <LinearProgress sx={{ mb: 2 }} />}

            {/* Upload Button */}
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button
                component="label"
                variant="outlined"
                startIcon={<AddPhotoAlternate />}
                sx={{ mb: 3 }}
                disabled={uploading}
              >
                Ajouter une image
                <input
                  type="file"
                  hidden
                  accept="image/*"
                  onChange={handleImageUpload}
                />
              </Button>
            </motion.div>

            {/* Image Previews */}
            <Grid container spacing={1}>
              {uploadedImages.map((image, index) => (
                <Grid item xs={6} key={index}>
                  <Box
                    sx={{
                      position: 'relative',
                      borderRadius: 2,
                      overflow: 'hidden',
                    }}
                  >
                    <Avatar
                      src={`http://localhost:8000/uploads/products/${image}`}
                      variant="rounded"
                      sx={{ width: '100%', height: 100 }}
                    />
                    <IconButton
                      size="small"
                      sx={{
                        position: 'absolute',
                        top: 4,
                        right: 4,
                        bgcolor: 'rgba(0,0,0,0.5)',
                        color: 'white',
                        '&:hover': {
                          bgcolor: 'rgba(0,0,0,0.7)',
                        },
                      }}
                      onClick={() => handleRemoveImage(index)}
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                  </Box>
                </Grid>
              ))}
            </Grid>

            {uploadedImages.length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Aucune image ajoutée. Ajoutez des images pour mieux présenter votre produit.
              </Typography>
            )}
          </Box>
        </Grid>
      </Grid>

      {/* Form Actions */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'flex-end',
          gap: 2,
          mt: 4,
          pt: 2,
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <Button onClick={onCancel} disabled={createMutation.isLoading}>
          Annuler
        </Button>
        <Button
          type="submit"
          variant="contained"
          disabled={createMutation.isLoading || updateMutation.isLoading}
          sx={{
            bgcolor: 'primary.main',
            minWidth: 120,
          }}
        >
          {createMutation.isLoading || updateMutation.isLoading
            ? 'Enregistrement...'
            : isEdit
            ? 'Mettre à jour'
            : 'Créer'}
        </Button>
      </Box>
    </Box>
  );
}

// frontend\src\components\products\ProductFilter.jsx
import React, { useState, useEffect } from 'react';
import {
  Paper,
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Button,
  Chip,
  Stack,
  Grid,
  Typography,
  IconButton,
  Collapse,
  Divider,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterListIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Category as CategoryIcon,
  BrandingWatermark as BrandIcon,
  AttachMoney as MoneyIcon,
  Inventory as InventoryIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { PRODUCT_CATEGORIES, PRODUCT_BRANDS } from '../../constants/config';

const ProductFilter = ({
  onFilterChange,
  initialFilters = {},
  categories = PRODUCT_CATEGORIES,
  brands = PRODUCT_BRANDS,
  compact = false,
}) => {
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    brand: '',
    minPrice: 0,
    maxPrice: 100000,
    stockStatus: '',
    ...initialFilters,
  });

  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [priceRange, setPriceRange] = useState([0, 100000]);

  // Mettre à jour les filtres
  const updateFilter = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    if (onFilterChange) {
      onFilterChange(newFilters);
    }
  };

  // Réinitialiser les filtres
  const resetFilters = () => {
    const defaultFilters = {
      search: '',
      category: '',
      brand: '',
      minPrice: 0,
      maxPrice: 100000,
      stockStatus: '',
    };
    setFilters(defaultFilters);
    setPriceRange([0, 100000]);
    if (onFilterChange) {
      onFilterChange(defaultFilters);
    }
  };

  // Appliquer la gamme de prix
  const handlePriceChange = (event, newValue) => {
    setPriceRange(newValue);
  };

  const handlePriceChangeCommitted = (event, newValue) => {
    updateFilter('minPrice', newValue[0]);
    updateFilter('maxPrice', newValue[1]);
  };

  // Filtres actifs
  const activeFilters = Object.entries(filters).filter(
    ([key, value]) => 
      value && 
      key !== 'minPrice' && 
      key !== 'maxPrice' &&
      !(key === 'search' && value === '')
  ).length;

  const formatPrice = (value) => {
    return `${value.toLocaleString('fr-CI')} F`;
  };

  if (compact) {
    return (
      <Paper
        sx={{
          p: 2,
          mb: 3,
          borderRadius: 3,
          bgcolor: 'background.paper',
          boxShadow: (theme) => theme.shadows[2],
        }}
      >
        <Grid container spacing={2} alignItems="center">
          {/* Barre de recherche */}
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              size="small"
              placeholder="Rechercher un produit..."
              value={filters.search}
              onChange={(e) => updateFilter('search', e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />,
                endAdornment: filters.search && (
                  <IconButton
                    size="small"
                    onClick={() => updateFilter('search', '')}
                    edge="end"
                  >
                    <ClearIcon fontSize="small" />
                  </IconButton>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                },
              }}
            />
          </Grid>

          {/* Filtres rapides */}
          <Grid item xs={12} md={8}>
            <Stack direction="row" spacing={2} alignItems="center">
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Catégorie</InputLabel>
                <Select
                  value={filters.category}
                  label="Catégorie"
                  onChange={(e) => updateFilter('category', e.target.value)}
                  startAdornment={<CategoryIcon sx={{ mr: 1, color: 'text.secondary' }} />}
                >
                  <MenuItem value="">
                    <em>Toutes les catégories</em>
                  </MenuItem>
                  {categories.map((cat) => (
                    <MenuItem key={cat} value={cat}>
                      {cat}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Marque</InputLabel>
                <Select
                  value={filters.brand}
                  label="Marque"
                  onChange={(e) => updateFilter('brand', e.target.value)}
                  startAdornment={<BrandIcon sx={{ mr: 1, color: 'text.secondary' }} />}
                >
                  <MenuItem value="">
                    <em>Toutes les marques</em>
                  </MenuItem>
                  {brands.map((brand) => (
                    <MenuItem key={brand} value={brand}>
                      {brand}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Button
                variant="outlined"
                startIcon={<FilterListIcon />}
                onClick={() => setAdvancedOpen(!advancedOpen)}
                endIcon={advancedOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                sx={{ whiteSpace: 'nowrap' }}
              >
                Plus de filtres
                {activeFilters > 0 && (
                  <Chip
                    label={activeFilters}
                    size="small"
                    color="primary"
                    sx={{ ml: 1 }}
                  />
                )}
              </Button>

              {(activeFilters > 0 || filters.search) && (
                <Button
                  variant="outlined"
                  color="secondary"
                  onClick={resetFilters}
                  startIcon={<ClearIcon />}
                >
                  Réinitialiser
                </Button>
              )}
            </Stack>
          </Grid>
        </Grid>

        {/* Filtres avancés */}
        <Collapse in={advancedOpen}>
          <Box sx={{ mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography gutterBottom variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <MoneyIcon fontSize="small" />
                  Gamme de prix
                </Typography>
                <Box sx={{ px: 2 }}>
                  <Slider
                    value={priceRange}
                    onChange={handlePriceChange}
                    onChangeCommitted={handlePriceChangeCommitted}
                    valueLabelDisplay="auto"
                    valueLabelFormat={formatPrice}
                    min={0}
                    max={100000}
                    step={1000}
                    marks={[
                      { value: 0, label: '0 F' },
                      { value: 50000, label: '50k F' },
                      { value: 100000, label: '100k F' },
                    ]}
                    sx={{ mt: 3 }}
                  />
                </Box>
                <Stack direction="row" justifyContent="space-between" sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Min: {formatPrice(priceRange[0])}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Max: {formatPrice(priceRange[1])}
                  </Typography>
                </Stack>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography gutterBottom variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <InventoryIcon fontSize="small" />
                  Statut du stock
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {[
                    { value: '', label: 'Tous' },
                    { value: 'EN_STOCK', label: 'En stock', color: 'success' },
                    { value: 'ALERTE', label: 'Stock faible', color: 'warning' },
                    { value: 'RUPTURE', label: 'Rupture', color: 'error' },
                  ].map((status) => (
                    <Chip
                      key={status.value}
                      label={status.label}
                      color={filters.stockStatus === status.value ? status.color : 'default'}
                      variant={filters.stockStatus === status.value ? 'filled' : 'outlined'}
                      onClick={() => updateFilter('stockStatus', status.value)}
                      clickable
                    />
                  ))}
                </Stack>
              </Grid>
            </Grid>
          </Box>
        </Collapse>

        {/* Filtres actifs */}
        <AnimatePresence>
          {activeFilters > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
                  Filtres actifs:
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {filters.search && (
                    <Chip
                      label={`Recherche: "${filters.search}"`}
                      size="small"
                      onDelete={() => updateFilter('search', '')}
                    />
                  )}
                  {filters.category && (
                    <Chip
                      label={`Catégorie: ${filters.category}`}
                      size="small"
                      onDelete={() => updateFilter('category', '')}
                    />
                  )}
                  {filters.brand && (
                    <Chip
                      label={`Marque: ${filters.brand}`}
                      size="small"
                      onDelete={() => updateFilter('brand', '')}
                    />
                  )}
                  {filters.stockStatus && (
                    <Chip
                      label={`Stock: ${filters.stockStatus === 'EN_STOCK' ? 'En stock' : filters.stockStatus === 'ALERTE' ? 'Faible' : 'Rupture'}`}
                      size="small"
                      onDelete={() => updateFilter('stockStatus', '')}
                    />
                  )}
                  {(filters.minPrice > 0 || filters.maxPrice < 100000) && (
                    <Chip
                      label={`Prix: ${formatPrice(filters.minPrice)} - ${formatPrice(filters.maxPrice)}`}
                      size="small"
                      onDelete={() => {
                        updateFilter('minPrice', 0);
                        updateFilter('maxPrice', 100000);
                        setPriceRange([0, 100000]);
                      }}
                    />
                  )}
                </Stack>
              </Box>
            </motion.div>
          )}
        </AnimatePresence>
      </Paper>
    );
  }

  // Version étendue (pour page dédiée)
  return (
    <Paper
      sx={{
        p: 3,
        mb: 4,
        borderRadius: 3,
        bgcolor: 'background.paper',
        boxShadow: (theme) => theme.shadows[3],
      }}
    >
      <Stack spacing={3}>
        {/* En-tête */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterListIcon />
            Filtres avancés
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {activeFilters > 0 && (
              <Button
                variant="outlined"
                color="secondary"
                onClick={resetFilters}
                startIcon={<ClearIcon />}
              >
                Tout effacer
              </Button>
            )}
            <Button
              variant="outlined"
              onClick={() => setAdvancedOpen(!advancedOpen)}
              endIcon={advancedOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            >
              {advancedOpen ? 'Moins de filtres' : 'Plus de filtres'}
            </Button>
          </Box>
        </Box>

        {/* Filtres principaux */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Rechercher un produit"
              value={filters.search}
              onChange={(e) => updateFilter('search', e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />,
              }}
              helperText="Recherche par nom, description, SKU ou code-barres"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Stack direction="row" spacing={2}>
              <FormControl fullWidth>
                <InputLabel>Catégorie</InputLabel>
                <Select
                  value={filters.category}
                  label="Catégorie"
                  onChange={(e) => updateFilter('category', e.target.value)}
                >
                  <MenuItem value="">
                    <em>Toutes les catégories</em>
                  </MenuItem>
                  {categories.map((cat) => (
                    <MenuItem key={cat} value={cat}>
                      {cat}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Marque</InputLabel>
                <Select
                  value={filters.brand}
                  label="Marque"
                  onChange={(e) => updateFilter('brand', e.target.value)}
                >
                  <MenuItem value="">
                    <em>Toutes les marques</em>
                  </MenuItem>
                  {brands.map((brand) => (
                    <MenuItem key={brand} value={brand}>
                      {brand}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Stack>
          </Grid>
        </Grid>

        <Divider />

        {/* Filtres avancés */}
        <Collapse in={advancedOpen}>
          <Stack spacing={3}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography gutterBottom variant="subtitle1">
                  Gamme de prix
                </Typography>
                <Box sx={{ px: 2 }}>
                  <Slider
                    value={priceRange}
                    onChange={handlePriceChange}
                    onChangeCommitted={handlePriceChangeCommitted}
                    valueLabelDisplay="auto"
                    valueLabelFormat={formatPrice}
                    min={0}
                    max={100000}
                    step={1000}
                    marks={[
                      { value: 0, label: '0 F' },
                      { value: 25000, label: '25k F' },
                      { value: 50000, label: '50k F' },
                      { value: 75000, label: '75k F' },
                      { value: 100000, label: '100k F' },
                    ]}
                    sx={{ mt: 3 }}
                  />
                </Box>
                <Stack direction="row" justifyContent="space-between" sx={{ mt: 2 }}>
                  <Typography variant="body2" fontWeight="medium">
                    {formatPrice(priceRange[0])}
                  </Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {formatPrice(priceRange[1])}
                  </Typography>
                </Stack>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography gutterBottom variant="subtitle1">
                  Statut du stock
                </Typography>
                <Stack direction="row" spacing={2} flexWrap="wrap">
                  {[
                    { value: '', label: 'Tous les produits', color: 'primary' },
                    { value: 'EN_STOCK', label: 'En stock', color: 'success' },
                    { value: 'ALERTE', label: 'Stock faible', color: 'warning' },
                    { value: 'RUPTURE', label: 'Rupture de stock', color: 'error' },
                  ].map((status) => (
                    <Button
                      key={status.value}
                      variant={filters.stockStatus === status.value ? 'contained' : 'outlined'}
                      color={status.color}
                      onClick={() => updateFilter('stockStatus', status.value)}
                      startIcon={<InventoryIcon />}
                      sx={{ mb: 1 }}
                    >
                      {status.label}
                    </Button>
                  ))}
                </Stack>
              </Grid>
            </Grid>

            {/* Options supplémentaires */}
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography gutterBottom variant="subtitle1">
                  Options supplémentaires
                </Typography>
                <Stack spacing={2}>
                  <Button
                    variant={filters.lowStock ? 'contained' : 'outlined'}
                    color="warning"
                    onClick={() => updateFilter('lowStock', !filters.lowStock)}
                    fullWidth
                  >
                    Afficher uniquement les produits avec stock faible
                  </Button>
                  <Button
                    variant={filters.includeInactive ? 'contained' : 'outlined'}
                    color="secondary"
                    onClick={() => updateFilter('includeInactive', !filters.includeInactive)}
                    fullWidth
                  >
                    Inclure les produits désactivés
                  </Button>
                </Stack>
              </Grid>
            </Grid>
          </Stack>
        </Collapse>

        {/* Résumé des filtres */}
        <AnimatePresence>
          {activeFilters > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  bgcolor: 'primary.contrastText',
                  borderColor: 'primary.main',
                }}
              >
                <Stack direction="row" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="subtitle2" color="primary.main" gutterBottom>
                      {activeFilters} filtre{activeFilters > 1 ? 's' : ''} actif{activeFilters > 1 ? 's' : ''}
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      {filters.search && (
                        <Chip
                          label={`"${filters.search}"`}
                          size="small"
                          onDelete={() => updateFilter('search', '')}
                          color="primary"
                        />
                      )}
                      {filters.category && (
                        <Chip
                          label={filters.category}
                          size="small"
                          onDelete={() => updateFilter('category', '')}
                          color="primary"
                        />
                      )}
                      {filters.brand && (
                        <Chip
                          label={filters.brand}
                          size="small"
                          onDelete={() => updateFilter('brand', '')}
                          color="primary"
                        />
                      )}
                      {filters.stockStatus && (
                        <Chip
                          label={`Stock: ${filters.stockStatus}`}
                          size="small"
                          onDelete={() => updateFilter('stockStatus', '')}
                          color="primary"
                        />
                      )}
                      {(filters.minPrice > 0 || filters.maxPrice < 100000) && (
                        <Chip
                          label={`Prix: ${formatPrice(filters.minPrice)}-${formatPrice(filters.maxPrice)}`}
                          size="small"
                          onDelete={() => {
                            updateFilter('minPrice', 0);
                            updateFilter('maxPrice', 100000);
                            setPriceRange([0, 100000]);
                          }}
                          color="primary"
                        />
                      )}
                    </Stack>
                  </Box>
                  <Button
                    size="small"
                    onClick={resetFilters}
                    startIcon={<ClearIcon />}
                  >
                    Tout effacer
                  </Button>
                </Stack>
              </Paper>
            </motion.div>
          )}
        </AnimatePresence>
      </Stack>
    </Paper>
  );
};

export default ProductFilter;

// frontend\src\components\products\ProductCard.jsx
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  CardActions,
  CardHeader,
  Typography,
  Box,
  Chip,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  LinearProgress,
  Avatar,
  Badge,
  Stack,
  Divider,
} from '@mui/material';
import {
  Edit as EditIcon,
  Inventory as InventoryIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  ShoppingCart as ShoppingCartIcon,
  LocalOffer as LocalOfferIcon,
  Category as CategoryIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { formatCurrency, formatDate, formatStockStatus } from '../../utils/formatters';
import { productService } from '../../services/products';
import { useNavigate } from 'react-router-dom';

const ProductCard = ({ product, onEdit, onDelete, onStockUpdate, compact = false }) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);

  const open = Boolean(anchorEl);

  const handleMenuClick = (event) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleEdit = () => {
    handleMenuClose();
    if (onEdit) onEdit(product);
  };

  const handleDelete = async () => {
    handleMenuClose();
    if (window.confirm(`Êtes-vous sûr de vouloir désactiver ${product.name} ?`)) {
      setLoading(true);
      try {
        await productService.deleteProduct(product.id);
        if (onDelete) onDelete(product.id);
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleStockUpdate = () => {
    handleMenuClose();
    if (onStockUpdate) onStockUpdate(product);
  };

  const handleViewDetails = () => {
    navigate(`/products/${product.id}`);
  };

  const getStockStatusColor = (status) => {
    switch (status) {
      case 'RUPTURE':
        return 'error';
      case 'ALERTE':
        return 'warning';
      case 'EN_STOCK':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStockStatusIcon = (status) => {
    switch (status) {
      case 'RUPTURE':
        return <ErrorIcon />;
      case 'ALERTE':
        return <WarningIcon />;
      case 'EN_STOCK':
        return <CheckCircleIcon />;
      default:
        return <InventoryIcon />;
    }
  };

  const getStockPercentage = () => {
    if (product.stock <= 0) return 0;
    return Math.min(100, (product.stock / product.alert_threshold) * 100);
  };

  const getPriceMargin = () => {
    const margin = product.selling_price - product.purchase_price;
    const marginPercentage = (margin / product.purchase_price) * 100;
    return { margin, marginPercentage };
  };

  const priceMargin = getPriceMargin();

  if (compact) {
    return (
      <motion.div
        whileHover={{ y: -4, transition: { duration: 0.2 } }}
        whileTap={{ scale: 0.98 }}
      >
        <Card
          sx={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            cursor: 'pointer',
            '&:hover': {
              boxShadow: (theme) => theme.shadows[8],
            },
          }}
          onClick={handleViewDetails}
        >
          {/* Image avec badge de statut */}
          <Box sx={{ position: 'relative' }}>
            <CardMedia
              component="div"
              sx={{
                pt: '100%',
                position: 'relative',
                bgcolor: 'grey.100',
                backgroundImage: product.images && product.images.length > 0 
                  ? `url(/uploads/products/${product.images[0]})`
                  : 'none',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
              }}
            >
              {(!product.images || product.images.length === 0) && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <InventoryIcon sx={{ fontSize: 48, color: 'grey.400' }} />
                </Box>
              )}
            </CardMedia>
            <Box sx={{ position: 'absolute', top: 8, left: 8 }}>
              <Chip
                icon={getStockStatusIcon(product.status)}
                label={product.status}
                size="small"
                color={getStockStatusColor(product.status)}
                sx={{ fontWeight: 'bold', backdropFilter: 'blur(4px)' }}
              />
            </Box>
            <Box sx={{ position: 'absolute', top: 8, right: 8 }}>
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsFavorite(!isFavorite);
                }}
                sx={{
                  backgroundColor: 'white',
                  '&:hover': { backgroundColor: 'grey.100' },
                }}
              >
                {isFavorite ? (
                  <StarIcon sx={{ color: 'warning.main' }} />
                ) : (
                  <StarBorderIcon />
                )}
              </IconButton>
            </Box>
          </Box>

          <CardContent sx={{ flexGrow: 1, p: 2 }}>
            <Typography
              variant="subtitle2"
              color="text.secondary"
              gutterBottom
              sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
            >
              <CategoryIcon fontSize="small" />
              {product.category}
            </Typography>
            
            <Typography variant="h6" component="h3" noWrap gutterBottom>
              {product.name}
            </Typography>

            {product.brand && (
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                Marque: {product.brand}
              </Typography>
            )}

            <Box sx={{ mt: 2 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="h6" color="primary.main" fontWeight="bold">
                  {formatCurrency(product.selling_price)}
                </Typography>
                <Chip
                  label={`${priceMargin.marginPercentage.toFixed(1)}%`}
                  size="small"
                  color="success"
                  variant="outlined"
                  sx={{ fontWeight: 'medium' }}
                />
              </Stack>

              <Typography variant="caption" color="text.secondary">
                Coût: {formatCurrency(product.purchase_price)}
              </Typography>
            </Box>

            <Box sx={{ mt: 2 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={1}>
                <Typography variant="body2" color="text.secondary">
                  Stock: {product.stock}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Seuil: {product.alert_threshold}
                </Typography>
              </Stack>
              <LinearProgress
                variant="determinate"
                value={getStockPercentage()}
                color={getStockStatusColor(product.status)}
                sx={{ mt: 0.5, height: 4, borderRadius: 2 }}
              />
            </Box>
          </CardContent>

          <Divider />
          <CardActions sx={{ p: 1, justifyContent: 'space-between' }}>
            <Button
              size="small"
              startIcon={<ShoppingCartIcon />}
              onClick={(e) => {
                e.stopPropagation();
                // Ajouter au panier
              }}
            >
              Vendre
            </Button>
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                handleMenuClick(e);
              }}
            >
              <MoreVertIcon />
            </IconButton>
          </CardActions>
        </Card>

        {/* Menu contextuel */}
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleMenuClose}
          onClick={(e) => e.stopPropagation()}
        >
          <MenuItem onClick={handleEdit}>
            <EditIcon fontSize="small" sx={{ mr: 1 }} />
            Modifier
          </MenuItem>
          <MenuItem onClick={handleStockUpdate}>
            <InventoryIcon fontSize="small" sx={{ mr: 1 }} />
            Gérer le stock
          </MenuItem>
          <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
            <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
            Désactiver
          </MenuItem>
        </Menu>
      </motion.div>
    );
  }

  // Version complète
  return (
    <motion.div
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      whileTap={{ scale: 0.98 }}
    >
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'visible',
          '&:hover': {
            boxShadow: (theme) => theme.shadows[8],
          },
        }}
      >
        {/* Header avec actions */}
        <CardHeader
          avatar={
            <Avatar
              sx={{
                bgcolor: (theme) => theme.palette[getStockStatusColor(product.status)].main,
              }}
            >
              {getStockStatusIcon(product.status)}
            </Avatar>
          }
          action={
            <>
              <IconButton
                aria-label="favorite"
                onClick={() => setIsFavorite(!isFavorite)}
                size="small"
              >
                {isFavorite ? (
                  <StarIcon sx={{ color: 'warning.main' }} />
                ) : (
                  <StarBorderIcon />
                )}
              </IconButton>
              <IconButton
                aria-label="settings"
                onClick={handleMenuClick}
                size="small"
              >
                <MoreVertIcon />
              </IconButton>
            </>
          }
          title={
            <Typography variant="h6" component="h3" noWrap>
              {product.name}
            </Typography>
          }
          subheader={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
              <Chip
                label={product.category}
                size="small"
                icon={<CategoryIcon />}
                variant="outlined"
              />
              {product.brand && (
                <Chip
                  label={product.brand}
                  size="small"
                  variant="outlined"
                />
              )}
            </Box>
          }
        />

        {/* Image principale */}
        <Box sx={{ position: 'relative', mx: 2, borderRadius: 2, overflow: 'hidden' }}>
          <CardMedia
            component="div"
            sx={{
              pt: '56.25%', // 16:9
              position: 'relative',
              bgcolor: 'grey.100',
              backgroundImage: product.images && product.images.length > 0 
                ? `url(/uploads/products/${product.images[0]})`
                : 'none',
              backgroundSize: 'cover',
              backgroundPosition: 'center',
            }}
          >
            {(!product.images || product.images.length === 0) && (
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <InventoryIcon sx={{ fontSize: 64, color: 'grey.400' }} />
              </Box>
            )}
            <Box sx={{ position: 'absolute', top: 16, left: 16 }}>
              <Badge
                badgeContent={product.images?.length || 0}
                color="primary"
                showZero
              >
                <Chip
                  icon={getStockStatusIcon(product.status)}
                  label={product.status}
                  size="small"
                  color={getStockStatusColor(product.status)}
                  sx={{ fontWeight: 'bold', backdropFilter: 'blur(4px)' }}
                />
              </Badge>
            </Box>
          </CardMedia>
        </Box>

        <CardContent sx={{ flexGrow: 1 }}>
          {/* Description */}
          {product.description && (
            <Typography variant="body2" color="text.secondary" paragraph>
              {product.description.length > 100
                ? `${product.description.substring(0, 100)}...`
                : product.description}
            </Typography>
          )}

          {/* Informations produit */}
          <Box sx={{ mb: 2 }}>
            <Stack direction="row" spacing={2} sx={{ mb: 1 }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  SKU
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {product.sku || 'N/A'}
                </Typography>
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Code-barres
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {product.barcode || 'N/A'}
                </Typography>
              </Box>
            </Stack>
          </Box>

          {/* Prix et marge */}
          <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Box>
                <Typography variant="caption" color="text.secondary" display="block">
                  Prix de vente
                </Typography>
                <Typography variant="h5" color="primary.main" fontWeight="bold">
                  {formatCurrency(product.selling_price)}
                </Typography>
              </Box>
              <Box sx={{ textAlign: 'right' }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Prix d'achat
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  {formatCurrency(product.purchase_price)}
                </Typography>
              </Box>
            </Stack>
            <Box sx={{ textAlign: 'center' }}>
              <Chip
                icon={<LocalOfferIcon />}
                label={`Marge: ${priceMargin.marginPercentage.toFixed(1)}% (${formatCurrency(priceMargin.margin)})`}
                color="success"
                variant="outlined"
                sx={{ fontWeight: 'medium' }}
              />
            </Box>
          </Box>

          {/* Stock */}
          <Box sx={{ mb: 2 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle2">
                Stock actuel
              </Typography>
              <Typography variant="h6" color={getStockStatusColor(product.status)}>
                {product.stock} unités
              </Typography>
            </Stack>
            <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Seuil d'alerte: {product.alert_threshold}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {Math.round((product.stock / product.alert_threshold) * 100)}% du seuil
              </Typography>
            </Stack>
            <LinearProgress
              variant="determinate"
              value={getStockPercentage()}
              color={getStockStatusColor(product.status)}
              sx={{ height: 6, borderRadius: 3 }}
            />
          </Box>

          {/* Informations supplémentaires */}
          <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
            {product.expiration_date && (
              <Box sx={{ flex: 1 }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Expiration
                </Typography>
                <Typography variant="body2">
                  {formatDate(product.expiration_date)}
                </Typography>
              </Box>
            )}
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary" display="block">
                Dernière mise à jour
              </Typography>
              <Typography variant="body2">
                {formatDate(product.updated_at, 'relative')}
              </Typography>
            </Box>
          </Stack>
        </CardContent>

        <Divider />

        <CardActions sx={{ p: 2, justifyContent: 'space-between' }}>
          <Button
            variant="outlined"
            size="small"
            onClick={handleViewDetails}
          >
            Détails
          </Button>
          <Stack direction="row" spacing={1}>
            <Button
              variant="contained"
              size="small"
              startIcon={<ShoppingCartIcon />}
              onClick={() => {
                // Ajouter au panier
              }}
            >
              Vendre
            </Button>
            <Button
              variant="outlined"
              size="small"
              startIcon={<InventoryIcon />}
              onClick={handleStockUpdate}
            >
              Stock
            </Button>
          </Stack>
        </CardActions>
      </Card>

      {/* Menu contextuel */}
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEdit}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          Modifier le produit
        </MenuItem>
        <MenuItem onClick={handleStockUpdate}>
          <InventoryIcon fontSize="small" sx={{ mr: 1 }} />
          Gérer le stock
        </MenuItem>
        <MenuItem onClick={() => navigate(`/products/${product.id}/movements`)}>
          <InventoryIcon fontSize="small" sx={{ mr: 1 }} />
          Historique des mouvements
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Désactiver le produit
        </MenuItem>
      </Menu>
    </motion.div>
  );
};

export default ProductCard;

//che-prince-garba\frontend\src\constants\config.js


/**
 * Application configuration constants
 */

export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
};

export const APP_CONFIG = {
  NAME: 'Luxe Beauté Management',
  VERSION: '2.0.0',
  DESCRIPTION: 'Système complet de gestion pour institut de beauté luxe',
  AUTHOR: 'Équipe Luxe Beauté',
  YEAR: new Date().getFullYear(),
};

export const ROLES = {
  ADMIN: 'ADMIN',
  MANAGER: 'MANAGER',
  CASHIER: 'CASHIER',
  STOCK_MANAGER: 'STOCK_MANAGER',
  BEAUTICIAN: 'BEAUTICIAN',
};

export const PERMISSIONS = {
  // Dashboard
  VIEW_DASHBOARD: 'view_dashboard',
  
  // Products
  VIEW_PRODUCTS: 'view_products',
  MANAGE_PRODUCTS: 'manage_products',
  MANAGE_PRODUCT_CATEGORIES: 'manage_product_categories',
  
  // Sales
  VIEW_SALES: 'view_sales',
  MANAGE_SALES: 'manage_sales',
  PROCESS_REFUNDS: 'process_refunds',
  VIEW_INVOICES: 'view_invoices',
  
  // Clients
  VIEW_CLIENTS: 'view_clients',
  MANAGE_CLIENTS: 'manage_clients',
  VIEW_CLIENT_HISTORY: 'view_client_history',
  
  // Stock
  VIEW_STOCK: 'view_stock',
  MANAGE_STOCK: 'manage_stock',
  MANAGE_SUPPLIERS: 'manage_suppliers',
  MANAGE_PURCHASE_ORDERS: 'manage_purchase_orders',
  
  // Accounting
  VIEW_ACCOUNTING: 'view_accounting',
  MANAGE_ACCOUNTING: 'manage_accounting',
  VIEW_FINANCIAL_REPORTS: 'view_financial_reports',
  MANAGE_EXPENSES: 'manage_expenses',
  
  // Appointments
  VIEW_APPOINTMENTS: 'view_appointments',
  MANAGE_APPOINTMENTS: 'manage_appointments',
  
  // Users
  VIEW_USERS: 'view_users',
  MANAGE_USERS: 'manage_users',
  
  // Reports
  VIEW_REPORTS: 'view_reports',
  EXPORT_DATA: 'export_data',
  
  // Settings
  MANAGE_SETTINGS: 'manage_settings',
  VIEW_AUDIT_LOG: 'view_audit_log',
};

export const ROLE_PERMISSIONS = {
  [ROLES.ADMIN]: Object.values(PERMISSIONS),
  
  [ROLES.MANAGER]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.MANAGE_PRODUCTS,
    PERMISSIONS.MANAGE_SALES,
    PERMISSIONS.MANAGE_CLIENTS,
    PERMISSIONS.MANAGE_STOCK,
    PERMISSIONS.MANAGE_ACCOUNTING,
    PERMISSIONS.VIEW_FINANCIAL_REPORTS,
    PERMISSIONS.MANAGE_EXPENSES,
    PERMISSIONS.MANAGE_APPOINTMENTS,
    PERMISSIONS.VIEW_REPORTS,
    PERMISSIONS.EXPORT_DATA,
  ],
  
  [ROLES.CASHIER]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_PRODUCTS,
    PERMISSIONS.MANAGE_SALES,
    PERMISSIONS.MANAGE_CLIENTS,
    PERMISSIONS.PROCESS_REFUNDS,
    PERMISSIONS.VIEW_INVOICES,
    PERMISSIONS.VIEW_REPORTS,
  ],
  
  [ROLES.STOCK_MANAGER]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.MANAGE_PRODUCTS,
    PERMISSIONS.MANAGE_STOCK,
    PERMISSIONS.MANAGE_SUPPLIERS,
    PERMISSIONS.MANAGE_PURCHASE_ORDERS,
    PERMISSIONS.VIEW_SALES,
    PERMISSIONS.VIEW_REPORTS,
    PERMISSIONS.EXPORT_DATA,
  ],
  
  [ROLES.BEAUTICIAN]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.MANAGE_APPOINTMENTS,
    PERMISSIONS.VIEW_CLIENTS,
    PERMISSIONS.VIEW_PRODUCTS,
  ],
};

export const PRODUCT_CATEGORIES = [
    "Soins Visage",
    "Soins Corps",
    "Soins Capillaires",
    "Lait",
    "Crème",
    "Pommade",
    "Maquillage",
    "Déodorants",
    "Parfums",
    "Huiles",
    "Sérums",
    "Gommage",
    "Shampoing",
    "Mèches",
    "Accessoires",
];

export const PRODUCT_BRANDS = [
  'L\'Oréal',
  'Estée Lauder',
  'Lancôme',
  'Chanel',
  'Dior',
  'Clarins',
  'Shiseido',
  'La Roche-Posay',
  'Vichy',
  'Nuxe',
  'Bioderma',
  'Avène',
  'Caudalie',
  'Sisley',
  'Guerlain',
  'Yves Saint Laurent',
  'MAC',
  'Sephora',
  'Kiehl\'s',
  'The Body Shop',
];

export const PAYMENT_METHODS = {
  CASH: 'Espèces',
  Saraly: 'Saraly',
  CARD: 'Carte bancaire',
  BANK_TRANSFER: 'Virement bancaire',
  CHECK: 'Chèque',
  CREDIT: 'Crédit',
  MOBILE_MONEY: 'Mobile Money',
};

export const STOCK_MOVEMENT_TYPES = {
  IN: 'Entrée',
  OUT: 'Sortie',
  ADJUSTMENT: 'Ajustement',
  RETURN: 'Retour',
  DAMAGED: 'Détérioré',
  EXPIRE: 'Expiré',
};

export const CLIENT_TYPES = {
  REGULAR: 'Standard',
  VIP: 'VIP',
  FIDELITE: 'Fidélité',
  WHOLESALER: 'Revendeur',
  CORPORATE: 'Entreprise',
};

export const APPOINTMENT_STATUS = {
  SCHEDULED: 'Planifié',
  CONFIRMED: 'Confirmé',
  IN_PROGRESS: 'En cours',
  COMPLETED: 'Terminé',
  CANCELLED: 'Annulé',
  NO_SHOW: 'Non venu',
};

export const REFUND_STATUS = {
  PENDING: 'En attente',
  APPROVED: 'Approuvé',
  COMPLETED: 'Terminé',
  CANCELLED: 'Annulé',
  REJECTED: 'Rejeté',
};

export const EXPENSE_CATEGORIES = [
  'Loyer',
  'Salaires',
  'Électricité',
  'Eau',
  'Téléphone/Internet',
  'Marketing',
  'Fournitures bureau',
  'Entretien',
  'Transport',
  'Assurance',
  'Impôts',
  'Frais bancaires',
  'Formation',
  'Équipement',
  'Autres',
];

export const DATE_FORMATS = {
  DISPLAY: 'dd/MM/yyyy HH:mm',
  DATE_ONLY: 'dd/MM/yyyy',
  TIME_ONLY: 'HH:mm',
  API: 'yyyy-MM-dd',
  API_FULL: 'yyyy-MM-dd HH:mm:ss',
};

export const CURRENCY_CONFIG = {
  SYMBOL: 'F',
  CODE: 'XOF',
  NAME: 'Franc CFA',
  LOCALE: 'fr-ML',
  DECIMALS: 0,
};

export const STOCK_ALERT_LEVELS = {
  CRITICAL: 30,  // 10% of threshold
  WARNING: 50,   // 30% of threshold
  NORMAL: 100,    // 50% of threshold
};

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
  MAX_PAGE_SIZE: 100,
};

export const UPLOAD_CONFIG = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  ALLOWED_DOCUMENT_TYPES: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
};

export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};

export const THEME_COLORS = {
  PRIMARY: '#8A2BE2',
  SECONDARY: '#FF4081',
  SUCCESS: '#10B981',
  WARNING: '#F59E0B',
  ERROR: '#EF4444',
  WARNING2: '#1bdb9b',
  INFO: '#3B82F6',
  BACKGROUND: '#F8FAFC',
  PAPER: '#FFFFFF',
  TEXT_PRIMARY: '#1F2937',
  TEXT_SECONDARY: '#6B7280',
};

export default {
  API_CONFIG,
  APP_CONFIG,
  ROLES,
  PERMISSIONS,
  ROLE_PERMISSIONS,
  PRODUCT_CATEGORIES,
  PRODUCT_BRANDS,
  PAYMENT_METHODS,
  STOCK_MOVEMENT_TYPES,
  CLIENT_TYPES,
  APPOINTMENT_STATUS,
  REFUND_STATUS,
  EXPENSE_CATEGORIES,
  DATE_FORMATS,
  CURRENCY_CONFIG,
  STOCK_ALERT_LEVELS,
  PAGINATION,
  UPLOAD_CONFIG,
  NOTIFICATION_TYPES,
  THEME_COLORS,
};


// frontend/src/pages/Products.jsx
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  InputAdornment,
  Fab,
  Tooltip,
  Alert,
  Badge,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Inventory,
  Search,
  FilterList,
  TrendingUp,
  TrendingDown,
  LocalOffer,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import DataTable from '../components/common/DataTable.jsx';
import ProductForm from '../components/products/ProductForm';
import ProductFilter from '../components/products/ProductFilter';
import ProductStockModal from '../components/products/ProductStockModal'; // Import ajouté
import { productService } from '../services/products';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Products() {
  const [openForm, setOpenForm] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [productToDelete, setProductToDelete] = useState(null);

  // Nouveaux états pour la gestion du stock
  const [stockModalOpen, setStockModalOpen] = useState(false);
  const [selectedForStock, setSelectedForStock] = useState(null);

  const { isAdmin, isManager } = useAuth();
  const queryClient = useQueryClient();

  const { data: products, isLoading } = useQuery(
    ['products', { search: searchTerm, ...filters }],
    () => productService.getProducts({ search: searchTerm, ...filters }),
    { refetchOnWindowFocus: false }
  );

  const deleteMutation = useMutation(
    (id) => productService.deleteProduct(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('products');
        toast.success('Produit créé avec succès', {
          icon: '✅',
          duration: 4000,
          style: { borderRadius: '10px', background: '#333', color: '#fff' }
        });              
        setDeleteDialog(false);
      },
      onError: (error) => {
        toast.error('Erreur lors de la suppression');
      },
    }
  );

  const handleOpenForm = (product = null) => {
    setSelectedProduct(product);
    setOpenForm(true);
  };

  const handleCloseForm = () => {
    setOpenForm(false);
    setSelectedProduct(null);
  };

  const handleDeleteClick = (product) => {
    setProductToDelete(product);
    setDeleteDialog(true);
  };

  const handleConfirmDelete = () => {
    if (productToDelete) {
      deleteMutation.mutate(productToDelete.id);
    }
  };

  // Nouveaux handlers pour le stock
  const handleOpenStockModal = (product) => {
    setSelectedForStock(product);
    setStockModalOpen(true);
  };

  const handleCloseStockModal = () => {
    setStockModalOpen(false);
    setSelectedForStock(null);
  };

  const handleSearch = (value) => {
    setSearchTerm(value);
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-CI', {
      style: 'currency',
      currency: 'XOF',
      minimumFractionDigits: 0,
    }).format(value);
  };

  const getStockStatus = (stock, threshold) => {
    if (stock <= 0) return { label: 'Rupture', color: 'error' };
    if (stock <= threshold) return { label: 'Faible', color: 'warning' };
    return { label: 'En stock', color: 'success' };
  };

  const columns = [
    {
      field: 'name',
      headerName: 'Produit',
      flex: 2,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {params.row.images?.[0] ? (
            <Box
              component="img"
              src={`http://localhost:8000/uploads/products/${params.row.images[0]}`}
              sx={{
                width: 40,
                height: 40,
                borderRadius: 1,
                objectFit: 'cover',
                mr: 2,
              }}
            />
          ) : (
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 1,
                bgcolor: 'primary.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mr: 2,
              }}
            >
              <Inventory sx={{ color: 'white' }} />
            </Box>
          )}
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {params.row.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {params.row.category} • {params.row.sku}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'stock',
      headerName: 'Stock',
      flex: 1,
      renderCell: (params) => {
        const status = getStockStatus(
          params.row.current_stock || 0,
          params.row.alert_threshold
        );
        return (
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {params.row.current_stock || 0}
              <Typography
                component="span"
                variant="caption"
                color="text.secondary"
                sx={{ ml: 0.5 }}
              >
                /{params.row.alert_threshold}
              </Typography>
            </Typography>
            <Chip
              label={status.label}
              size="small"
              color={status.color}
              sx={{ height: 20, fontSize: '0.7rem' }}
            />
          </Box>
        );
      },
    },
    {
      field: 'prices',
      headerName: 'Prix',
      flex: 1,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2" fontWeight="medium">
            {formatCurrency(params.row.selling_price)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Achat: {formatCurrency(params.row.purchase_price)}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'margin',
      headerName: 'Marge',
      flex: 1,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {params.row.margin >= 30 ? (
            <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
          ) : (
            <TrendingDown sx={{ color: 'warning.main', mr: 0.5 }} />
          )}
          <Typography
            variant="body2"
            color={params.row.margin >= 30 ? 'success.main' : 'warning.main'}
            fontWeight="medium"
          >
            {params.row.margin?.toFixed(1) || 0}%
          </Typography>
        </Box>
      ),
    },
    {
      field: 'status',
      headerName: 'Statut',
      flex: 1,
      renderCell: (params) => (
        <Chip
          label={params.row.is_active ? 'Actif' : 'Inactif'}
          color={params.row.is_active ? 'success' : 'default'}
          size="small"
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      flex: 1,
      renderCell: (params) => (
        <Box>
          <Tooltip title="Voir">
            <IconButton size="small" onClick={() => handleOpenForm(params.row)}>
              <Visibility fontSize="small" />
            </IconButton>
          </Tooltip>
          {(isAdmin || isManager) && (
            <>
              <Tooltip title="Modifier">
                <IconButton size="small" onClick={() => handleOpenForm(params.row)}>
                  <Edit fontSize="small" />
                </IconButton>
              </Tooltip>
              {/* Nouveau bouton Gérer le stock */}
              <Tooltip title="Gérer le stock">
                <IconButton size="small" onClick={() => handleOpenStockModal(params.row)}>
                  <Inventory fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Supprimer">
                <IconButton
                  size="small"
                  onClick={() => handleDeleteClick(params.row)}
                  color="error"
                >
                  <Delete fontSize="small" />
                </IconButton>
              </Tooltip>
            </>
          )}
        </Box>
      ),
    },
  ];

  return (
    <Box>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
        }}
      >
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Gestion des produits
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {products?.length || 0} produits enregistrés
          </Typography>
        </Box>
        {(isAdmin || isManager) && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenForm()}
            sx={{
              bgcolor: 'primary.main',
              '&:hover': {
                bgcolor: 'primary.dark',
              },
            }}
          >
            Nouveau produit
          </Button>
        )}
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <ProductFilter
            onSearch={handleSearch}
            onFilterChange={handleFilterChange}
          />
        </CardContent>
      </Card>

      {/* Products Grid */}
      <AnimatePresence>
        {isLoading ? (
          <Grid container spacing={3}>
            {[1, 2, 3, 4].map((i) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={i}>
                <Card>
                  <Box sx={{ p: 2 }}>
                    <Box className="skeleton" sx={{ height: 200, borderRadius: 1 }} />
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : products && products.length > 0 ? (
          <>
            <DataTable
              rows={products}
              columns={columns}
              loading={isLoading}
              getRowId={(row) => row.id}
              pageSize={10}
              rowsPerPageOptions={[10, 25, 50]}
              checkboxSelection={false}
              sx={{ height: 600 }}
            />
          </>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 8 }}>
                <Inventory sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Aucun produit trouvé
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  {searchTerm || Object.keys(filters).length > 0
                    ? 'Essayez de modifier vos critères de recherche'
                    : 'Commencez par ajouter votre premier produit'}
                </Typography>
                {(isAdmin || isManager) && (
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => handleOpenForm()}
                  >
                    Ajouter un produit
                  </Button>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quick Action FAB */}
      {(isAdmin || isManager) && (
        <Fab
          color="primary"
          aria-label="add"
          sx={{
            position: 'fixed',
            bottom: 32,
            right: 32,
            bgcolor: 'primary.main',
            '&:hover': {
              bgcolor: 'primary.dark',
              transform: 'scale(1.1)',
            },
            transition: 'all 0.2s ease',
          }}
          onClick={() => handleOpenForm()}
        >
          <Add />
        </Fab>
      )}

      {/* Product Form Dialog */}
      <Dialog
        open={openForm}
        onClose={handleCloseForm}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle>
          {selectedProduct ? 'Modifier le produit' : 'Nouveau produit'}
        </DialogTitle>
        <DialogContent dividers>
          <ProductForm
            product={selectedProduct}
            onSuccess={handleCloseForm}
            onCancel={handleCloseForm}
          />
        </DialogContent>
      </Dialog>

      {/* Stock Management Modal - Nouveau */}
      <ProductStockModal
        open={stockModalOpen}
        onClose={handleCloseStockModal}
        product={selectedForStock}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog}
        onClose={() => setDeleteDialog(false)}
        PaperProps={{
          sx: {
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle>Confirmer la suppression</DialogTitle>
        <DialogContent>
          <Typography>
            Êtes-vous sûr de vouloir supprimer le produit "
            {productToDelete?.name}" ?
          </Typography>
          <Alert severity="warning" sx={{ mt: 2 }}>
            Cette action est irréversible. Toutes les données associées seront
            également supprimées.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>Annuler</Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={deleteMutation.isLoading}
          >
            {deleteMutation.isLoading ? 'Suppression...' : 'Supprimer'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

// frontend/src/services/products.js
import api from './api';

export const productService = {
  // Get all products
  async getProducts(params = {}) {
    const response = await api.get('/products/', { params });
    return response.data;
  },

  // Get product by ID
  async getProductById(id) {
    const response = await api.get(`/products/${id}`);
    return response.data;
  },

  // Create product
  async createProduct(productData) {
    const response = await api.post('/products/', productData);
    return response.data;
  },

  // Update product
  async updateProduct(id, productData) {
    const response = await api.put(`/products/${id}`, productData);
    return response.data;
  },

  // Delete product
  async deleteProduct(id) {
    await api.delete(`/products/${id}`);
  },

  // Search products
  async searchProducts(searchParams) {
    const response = await api.get('/products/', { params: searchParams });
    return response.data;
  },

  // Get low stock products
  async getLowStockProducts() {
    const response = await api.get('/dashboard/inventory-alerts');
    return response.data;
  },

  // Update stock
  async updateStock(movementData) {
    const response = await api.post('/stock/movements/', movementData);
    return response.data;
  },

  // Get product statistics
  async getProductStats(productId) {
    const response = await api.get(`/products/${productId}/stats`);
    return response.data;
  },

  // Upload product image
  async uploadProductImage(productId, file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/products/${productId}/image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // Get product movements
  async getProductMovements(productId, params = {}) {
    const response = await api.get('/stock/movements/', {
      params: { product_id: productId, ...params }
    });
    return response.data;
  },

  // Create stock movement (alias for updateStock)
  async createStockMovement(movementData) {
    return this.updateStock(movementData);
  },

  // Get stock alerts
  async getStockAlerts() {
    const response = await api.get('/stock/alerts/');
    return response.data;
  },

  // Get product categories
  async getCategories() {
    const response = await api.get('/products/categories');
    return response.data;
  },

  // Get product brands
  async getBrands() {
    const response = await api.get('/products/brands');
    return response.data;
  },

  
  // Après les méthodes existantes, par exemple après getBrands
  async getProductStats() {
    const response = await api.get('/products/stats');
    return response.data;
  },

  async getProductMovementStats(productId) {
    const response = await api.get(`/products/${productId}/movements/stats`);
    return response.data;
  },

    // Bulk update products
    async bulkUpdateProducts(updates) {
      const response = await api.put('/products/bulk', updates);
      return response.data;
    },
  };

import api from './api';

export const stockService = {
  /**
   * Récupère tous les mouvements de stock
   */
  async getStockMovements(params = {}) {
    const response = await api.get('/stock/movements/', { params });
    return response.data;
  },

  /**
   * Crée un nouveau mouvement de stock
   */
  async createStockMovement(movementData) {
    const response = await api.post('/stock/movements/', movementData);
    return response.data;
  },

  /**
   * Récupère les alertes de stock
   */
  async getStockAlerts() {
    const response = await api.get('/stock/alerts/');
    return response.data;
  },

  /**
   * Récupère les statistiques de stock
   */
  async getStockStats() {
    // Utilise l'endpoint dashboard pour les stats
    const response = await api.get('/dashboard/stats');
    return response.data;
  },

  /**
   * Récupère l'historique des mouvements par produit
   */
  async getProductStockHistory(productId, params = {}) {
    const response = await api.get(`/products/${productId}/movements`, { params });
    return response.data;
  },

  /**
   * Récupère les produits avec stock faible
   */
  async getLowStockProducts(thresholdPercentage = 0.3) {
    const response = await api.get('/dashboard/inventory-alerts', {
      params: { threshold_percentage: thresholdPercentage }
    });
    return response.data;
  },

  /**
   * Met à jour le stock d'un produit
   */
  async updateProductStock(productId, quantity, movementType, reason = '') {
    const movementData = {
      product_id: productId,
      movement_type: movementType,
      quantity: quantity,
      reason: reason,
      movement_date: new Date().toISOString()
    };
    return this.createStockMovement(movementData);
  },

  /**
   * Récupère les produits expirant bientôt
   */
  async getExpiringProducts(days = 30) {
    // Cette fonctionnalité pourrait être ajoutée au backend
    // Pour l'instant, nous filtrons côté frontend
    const products = await this.getAllProductsWithStock();
    const today = new Date();
    const expiryDate = new Date();
    expiryDate.setDate(today.getDate() + days);
    
    return products.filter(product => {
      if (!product.expiration_date) return false;
      const expDate = new Date(product.expiration_date);
      return expDate <= expiryDate && expDate >= today;
    });
  },

  /**
   * Récupère tous les produits avec leur stock actuel
   */
  async getAllProductsWithStock() {
    const response = await api.get('/products/', {
      params: { include_inactive: false }
    });
    return response.data;
  },

  /**
   * Génère un rapport de stock
   */
  async generateStockReport(format = 'pdf') {
    const response = await api.get('/reports/stock', {
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  },

  /**
   * Importe un fichier CSV de stock
   */
  async importStockCSV(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/stock/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Exporte les données de stock en CSV
   */
  async exportStockCSV() {
    const response = await api.get('/stock/export', {
      responseType: 'blob'
    });
    return response.data;
  }
};

export default stockService;
/* frontend\src\styles\global.css */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: 100vh;
  color: #1f2937;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* Gradient text */
.gradient-text {
  background: linear-gradient(135deg, #8A2BE2 0%, #FF4081 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Glass morphism */
.glass-effect {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    transform: translateX(-20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.fade-in {
  animation: fadeIn 0.5s ease-out;
}

.slide-in {
  animation: slideIn 0.3s ease-out;
}

/* Loading skeleton */
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Status badges */
.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-success {
  background-color: #d1fae5;
  color: #065f46;
}

.status-warning {
  background-color: #fef3c7;
  color: #92400e;
}

.status-error {
  background-color: #fee2e2;
  color: #991b1b;
}

.status-info {
  background-color: #dbeafe;
  color: #1e40af;
}

/* Card hover effects */
.hover-lift {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

// frontend\src\styles\theme.js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#8A2BE2',
      light: '#9D4EDD',
      dark: '#7B1FA2',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#FF4081',
      light: '#FF79B0',
      dark: '#C60055',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#F8FAFC',
      paper: '#FFFFFF',
    },
    success: {
      main: '#10B981',
      light: '#34D399',
      dark: '#059669',
    },
    warning: {
      main: '#F59E0B',
      light: '#FBBF24',
      dark: '#D97706',
    },
    error: {
      main: '#EF4444',
      light: '#F87171',
      dark: '#DC2626',
    },
    info: {
      main: '#3B82F6',
      light: '#60A5FA',
      dark: '#2563EB',
    },
    text: {
      primary: '#1F2937',
      secondary: '#6B7280',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0px 2px 4px rgba(0, 0, 0, 0.05)',
    '0px 4px 6px rgba(0, 0, 0, 0.07)',
    '0px 10px 15px rgba(0, 0, 0, 0.1)',
    '0px 20px 25px rgba(0, 0, 0, 0.1)',
    ...Array(20).fill('none'),
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 8,
          padding: '8px 24px',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.15)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.08)',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0px 8px 30px rgba(0, 0, 0, 0.12)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: 16,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontWeight: 600,
          backgroundColor: '#F9FAFB',
        },
      },
    },
  },
});

export default theme;

