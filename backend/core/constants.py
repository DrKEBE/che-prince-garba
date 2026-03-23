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