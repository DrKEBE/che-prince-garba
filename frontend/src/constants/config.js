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

