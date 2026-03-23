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