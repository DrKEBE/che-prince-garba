"""
Fonctions de formatage pour l'affichage des données
"""
import streamlit as st
from datetime import datetime, date, timedelta
from decimal import Decimal
import re
from typing import Any, Dict, List, Optional, Union

def format_currency(amount: Union[float, Decimal, int], currency: str = "FCFA") -> str:
    """
    Formate un montant en devise
    """
    if amount is None:
        return f"0 {currency}"
    
    try:
        # Convertir en float
        if isinstance(amount, Decimal):
            amount = float(amount)
        elif isinstance(amount, int):
            amount = float(amount)
        
        # Formater avec séparateurs de milliers
        if amount >= 1000000:
            formatted = f"{amount/1000000:,.1f}M"
        elif amount >= 1000:
            formatted = f"{amount/1000:,.1f}K"
        else:
            formatted = f"{amount:,.0f}"
        
        # Supprimer .0 si c'est un entier
        formatted = re.sub(r'\.0([MK]?)$', r'\1', formatted)
        
        return f"{formatted} {currency}"
    except (ValueError, TypeError):
        return f"0 {currency}"

def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formate un pourcentage
    """
    if value is None:
        return "0%"
    
    try:
        return f"{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0%"

def format_date(date_obj: Union[datetime, date, str], format_str: str = "%d/%m/%Y") -> str:
    """
    Formate une date
    """
    if date_obj is None:
        return "N/A"
    
    try:
        if isinstance(date_obj, str):
            # Essayer de parser la date
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                try:
                    date_obj = datetime.strptime(date_obj, fmt)
                    break
                except ValueError:
                    continue
            
            if isinstance(date_obj, str):
                return date_obj
        
        if isinstance(date_obj, (datetime, date)):
            return date_obj.strftime(format_str)
        
        return str(date_obj)
    except (ValueError, TypeError):
        return "Date invalide"

def format_datetime(datetime_obj: datetime, include_seconds: bool = False) -> str:
    """
    Formate un datetime
    """
    if datetime_obj is None:
        return "N/A"
    
    try:
        if include_seconds:
            return datetime_obj.strftime("%d/%m/%Y %H:%M:%S")
        else:
            return datetime_obj.strftime("%d/%m/%Y %H:%M")
    except (ValueError, TypeError):
        return "Date/heure invalide"

def format_relative_time(date_obj: datetime) -> str:
    """
    Formate une date en temps relatif
    """
    if date_obj is None:
        return "Jamais"
    
    try:
        now = datetime.now()
        diff = now - date_obj
        
        if diff.days > 365:
            years = diff.days // 365
            return f"il y a {years} an{'s' if years > 1 else ''}"
        elif diff.days > 30:
            months = diff.days // 30
            return f"il y a {months} mois"
        elif diff.days > 0:
            return f"il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"il y a {hours} heure{'s' if hours > 1 else ''}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return "à l'instant"
    except (ValueError, TypeError):
        return "Date invalide"

def format_duration(seconds: int) -> str:
    """
    Formate une durée en secondes
    """
    if seconds is None:
        return "0s"
    
    try:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)
    except (ValueError, TypeError):
        return "0s"

def format_phone_number(phone: str) -> str:
    """
    Formate un numéro de téléphone
    """
    if not phone:
        return ""
    
    # Nettoyer le numéro
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Formater selon la longueur
    if len(cleaned) == 10 and cleaned.startswith('0'):
        return f"{cleaned[:2]} {cleaned[2:4]} {cleaned[4:6]} {cleaned[6:8]} {cleaned[8:]}"
    elif len(cleaned) == 12 and cleaned.startswith('+225'):
        return f"+225 {cleaned[4:6]} {cleaned[6:8]} {cleaned[8:10]} {cleaned[10:]}"
    elif len(cleaned) == 9 and cleaned.startswith('07'):
        return f"+225 {cleaned[1:3]} {cleaned[3:5]} {cleaned[5:7]} {cleaned[7:]}"
    else:
        return phone

def format_email(email: str) -> str:
    """
    Formate un email avec protection basique
    """
    if not email:
        return ""
    
    if '@' in email:
        # Masquer partiellement l'email
        local, domain = email.split('@')
        if len(local) > 2:
            masked_local = local[:2] + '*' * (len(local) - 2)
        else:
            masked_local = local
        
        return f"{masked_local}@{domain}"
    
    return email

def format_address(address: str, max_length: int = 50) -> str:
    """
    Formate une adresse
    """
    if not address:
        return "Non renseignée"
    
    if len(address) > max_length:
        return address[:max_length] + "..."
    
    return address

def format_stock_status(stock: int, threshold: int = 10) -> str:
    """
    Formate le statut du stock
    """
    if stock is None:
        return "Inconnu"
    
    if stock <= 0:
        return "🔴 Rupture"
    elif stock <= threshold:
        return "🟡 Faible"
    elif stock <= threshold * 3:
        return "🟢 Normal"
    else:
        return "🔵 Excédent"

def format_payment_method(method: str) -> str:
    """
    Formate une méthode de paiement
    """
    method_map = {
        "CASH": "💵 Espèces",
        "MOBILE_MONEY": "📱 Mobile Money",
        "Saraly": "📱 Saraly",
        "CARD": "💳 Carte Bancaire",
        "BANK_TRANSFER": "🏦 Virement",
        "CHECK": "📋 Chèque",
        "CREDIT": "💳 Crédit"
    }
    
    return method_map.get(method, method)

def format_client_type(client_type: str) -> str:
    """
    Formate un type de client
    """
    type_map = {
        "REGULAR": "🟢 Régulier",
        "VIP": "⭐ VIP",
        "FIDELITE": "👑 Fidélité",
        "WHOLESALER": "🏢 Grossiste",
        "NEW": "🆕 Nouveau"
    }
    
    return type_map.get(client_type, client_type)

def format_user_role(role: str) -> str:
    """
    Formate un rôle utilisateur
    """
    role_map = {
        "ADMIN": "👑 Administrateur",
        "MANAGER": "💼 Gestionnaire",
        "CASHIER": "💰 Caissier",
        "STOCK_MANAGER": "📦 Stock",
        "BEAUTICIAN": "💄 Esthéticienne"
    }
    
    return role_map.get(role, role)

def format_boolean(value: bool) -> str:
    """
    Formate une valeur booléenne
    """
    if value:
        return "✅ Oui"
    else:
        return "❌ Non"

def format_list(items: List[Any], max_items: int = 3, separator: str = ", ") -> str:
    """
    Formate une liste d'éléments
    """
    if not items:
        return ""
    
    if len(items) <= max_items:
        return separator.join(str(item) for item in items)
    else:
        displayed = items[:max_items]
        return separator.join(str(item) for item in displayed) + f" +{len(items) - max_items}"

def truncate_text(text: str, max_length: int = 100, ellipsis: str = "...") -> str:
    """
    Tronque un texte trop long
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(ellipsis)] + ellipsis

def format_file_size(size_bytes: int) -> str:
    """
    Formate une taille de fichier
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def format_progress_bar(value: float, max_value: float = 100) -> str:
    """
    Crée une barre de progression textuelle
    """
    width = 20
    filled = int((value / max_value) * width)
    empty = width - filled
    
    bar = "█" * filled + "░" * empty
    percentage = (value / max_value) * 100
    
    return f"{bar} {percentage:.1f}%"

def format_color_hex(color_name: str) -> str:
    """
    Convertit un nom de couleur en code hex
    """
    color_map = {
        "primary": "#FF6B9D",
        "secondary": "#9B59B6",
        "success": "#2ECC71",
        "warning": "#F1C40F",
        "danger": "#E74C3C",
        "info": "#3498DB",
        "light": "#F8F9FA",
        "dark": "#2C3E50"
    }
    
    return color_map.get(color_name, color_name)

def format_margin_color(margin: float) -> str:
    """
    Retourne une couleur basée sur la marge
    """
    if margin >= 50:
        return "#2ECC71"  # Vert
    elif margin >= 30:
        return "#F1C40F"  # Jaune
    elif margin >= 10:
        return "#E67E22"  # Orange
    else:
        return "#E74C3C"  # Rouge

def format_rating_stars(rating: float, max_stars: int = 5) -> str:
    """
    Formate une note avec des étoiles
    """
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = max_stars - full_stars - (1 if half_star else 0)
    
    stars = "⭐" * full_stars
    if half_star:
        stars += "⭐"
    stars += "☆" * empty_stars
    
    return f"{stars} ({rating:.1f}/5)"

def format_social_number(number: int) -> str:
    """
    Formate un nombre pour les réseaux sociaux
    """
    if number >= 1000000:
        return f"{number/1000000:.1f}M"
    elif number >= 1000:
        return f"{number/1000:.1f}K"
    else:
        return str(number)

def create_badge(text: str, color: str = "primary") -> str:
    """
    Crée un badge HTML
    """
    color_hex = format_color_hex(color)
    
    badge_html = f"""
    <span style="
        display: inline-block;
        padding: 0.25em 0.75em;
        font-size: 0.75em;
        font-weight: 600;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 10px;
        background-color: {color_hex};
        color: white;
    ">{text}</span>
    """
    
    return badge_html

def format_table_cell(value: Any, column_type: str = "text") -> Any:
    """
    Formate une cellule de tableau selon son type
    """
    if value is None:
        return "-"
    
    if column_type == "currency":
        return format_currency(value)
    elif column_type == "percentage":
        return format_percentage(value)
    elif column_type == "date":
        return format_date(value)
    elif column_type == "datetime":
        return format_datetime(value)
    elif column_type == "boolean":
        return format_boolean(value)
    elif column_type == "phone":
        return format_phone_number(value)
    elif column_type == "email":
        return format_email(value)
    elif column_type == "status":
        return format_stock_status(value)
    else:
        return str(value)