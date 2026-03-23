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
        """Propriété pour obtenir le stock actuel, cohérente avec le CRUD."""
        # Si une session est fournie, on utilise le CRUD pour le calcul exact
        if db is not None:
            from crud.product import product as product_crud
            return product_crud.calculate_current_stock(db, self.id)
        
        # Sinon, on utilise les mouvements déjà chargés (moins précis, mais rapide)
        if hasattr(self, 'stock_movements') and self.stock_movements:
            stock_in = sum(m.quantity for m in self.stock_movements 
                           if m.movement_type in ["IN", "RETURN", "ADJUSTMENT"])
            stock_out = sum(m.quantity for m in self.stock_movements 
                            if m.movement_type in ["OUT", "DAMAGED"])
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