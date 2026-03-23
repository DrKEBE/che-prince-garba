"""
Fonctions de validation pour les formulaires et données
"""
import re
import phonenumbers
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple, Dict, Any
import streamlit as st

class Validators:
    """Classe de validation des données"""
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> Tuple[bool, str]:
        """Valide qu'un champ est requis"""
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"Le champ {field_name} est requis"
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Valide un email"""
        if not email:
            return True, ""  # Email optionnel
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Format d'email invalide"
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str, country: str = "CI") -> Tuple[bool, str]:
        """Valide un numéro de téléphone"""
        if not phone:
            return True, ""  # Téléphone optionnel
        
        try:
            # Nettoyer le numéro
            cleaned = re.sub(r'[^\d+]', '', phone)
            
            # Pour la Côte d'Ivoire
            if country == "CI":
                # Formats acceptés: +225XXXXXXXX, 0XXXXXXXX, 07XXXXXXXX
                if cleaned.startswith('+225') and len(cleaned) == 13:
                    return True, ""
                elif cleaned.startswith('0') and len(cleaned) == 10:
                    return True, ""
                elif cleaned.startswith('7') and len(cleaned) == 9:
                    return True, ""
                else:
                    return False, "Format de téléphone invalide pour la Côte d'Ivoire"
            
            # Validation générique avec phonenumbers
            parsed = phonenumbers.parse(phone, country)
            if phonenumbers.is_valid_number(parsed):
                return True, ""
            else:
                return False, "Numéro de téléphone invalide"
                
        except Exception:
            return False, "Format de téléphone invalide"
    
    @staticmethod
    def validate_numeric(value: Any, min_val: float = None, max_val: float = None) -> Tuple[bool, str]:
        """Valide une valeur numérique"""
        if value is None:
            return True, ""  # Optionnel
        
        try:
            num = float(value)
            
            if min_val is not None and num < min_val:
                return False, f"La valeur doit être supérieure ou égale à {min_val}"
            
            if max_val is not None and num > max_val:
                return False, f"La valeur doit être inférieure ou égale à {max_val}"
            
            return True, ""
        except (ValueError, TypeError):
            return False, "Valeur numérique invalide"
    
    @staticmethod
    def validate_integer(value: Any, min_val: int = None, max_val: int = None) -> Tuple[bool, str]:
        """Valide un entier"""
        if value is None:
            return True, ""  # Optionnel
        
        try:
            num = int(value)
            
            if min_val is not None and num < min_val:
                return False, f"La valeur doit être supérieure ou égale à {min_val}"
            
            if max_val is not None and num > max_val:
                return False, f"La valeur doit être inférieure ou égale à {max_val}"
            
            return True, ""
        except (ValueError, TypeError):
            return False, "Nombre entier invalide"
    
    @staticmethod
    def validate_decimal(value: Any, min_val: Decimal = None, max_val: Decimal = None, 
                         precision: int = 2) -> Tuple[bool, str]:
        """Valide un décimal"""
        if value is None:
            return True, ""  # Optionnel
        
        try:
            if isinstance(value, str):
                # Remplacer les virgules par des points
                value = value.replace(',', '.')
            
            num = Decimal(str(value))
            
            # Vérifier la précision
            if precision is not None:
                decimal_places = abs(num.as_tuple().exponent)
                if decimal_places > precision:
                    return False, f"Maximum {precision} décimales autorisées"
            
            if min_val is not None and num < min_val:
                return False, f"La valeur doit être supérieure ou égale à {min_val}"
            
            if max_val is not None and num > max_val:
                return False, f"La valeur doit être inférieure ou égale à {max_val}"
            
            return True, ""
        except (InvalidOperation, ValueError, TypeError):
            return False, "Valeur décimale invalide"
    
    @staticmethod
    def validate_date(date_str: str, min_date: date = None, max_date: date = None, 
                      format: str = "%Y-%m-%d") -> Tuple[bool, str]:
        """Valide une date"""
        if not date_str:
            return True, ""  # Optionnel
        
        try:
            date_obj = datetime.strptime(date_str, format).date()
            
            if min_date and date_obj < min_date:
                return False, f"La date doit être postérieure au {min_date.strftime('%d/%m/%Y')}"
            
            if max_date and date_obj > max_date:
                return False, f"La date doit être antérieure au {max_date.strftime('%d/%m/%Y')}"
            
            return True, ""
        except ValueError:
            return False, f"Format de date invalide. Utilisez {format}"
    
    @staticmethod
    def validate_string_length(text: str, min_len: int = None, max_len: int = None) -> Tuple[bool, str]:
        """Valide la longueur d'une chaîne"""
        if text is None:
            text = ""
        
        length = len(text.strip())
        
        if min_len is not None and length < min_len:
            return False, f"Minimum {min_len} caractères requis"
        
        if max_len is not None and length > max_len:
            return False, f"Maximum {max_len} caractères autorisés"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str, min_length: int = 8) -> Tuple[bool, str]:
        """Valide un mot de passe"""
        if not password:
            return False, "Le mot de passe est requis"
        
        if len(password) < min_length:
            return False, f"Le mot de passe doit contenir au moins {min_length} caractères"
        
        # Vérifier la complexité
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        errors = []
        if not has_upper:
            errors.append("une majuscule")
        if not has_lower:
            errors.append("une minuscule")
        if not has_digit:
            errors.append("un chiffre")
        if not has_special:
            errors.append("un caractère spécial")
        
        if errors:
            return False, f"Le mot de passe doit contenir au moins {', '.join(errors)}"
        
        return True, ""
    
    @staticmethod
    def validate_sku(sku: str) -> Tuple[bool, str]:
        """Valide un SKU produit"""
        if not sku:
            return True, ""  # Optionnel
        
        # Format: lettres, chiffres, tirets, underscores
        pattern = r'^[A-Za-z0-9_-]+$'
        if not re.match(pattern, sku):
            return False, "SKU invalide. Utilisez seulement lettres, chiffres, tirets et underscores"
        
        if len(sku) > 50:
            return False, "SKU trop long (max 50 caractères)"
        
        return True, ""
    
    @staticmethod
    def validate_barcode(barcode: str) -> Tuple[bool, str]:
        """Valide un code-barres"""
        if not barcode:
            return True, ""  # Optionnel
        
        # Formats courants: EAN-13 (13 chiffres), UPC-A (12 chiffres)
        if not barcode.isdigit():
            return False, "Le code-barres doit contenir uniquement des chiffres"
        
        length = len(barcode)
        if length not in [8, 12, 13, 14]:
            return False, "Longueur de code-barres invalide (8, 12, 13 ou 14 chiffres attendus)"
        
        return True, ""
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """Valide une URL"""
        if not url:
            return True, ""  # Optionnel
        
        pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        if not re.match(pattern, url):
            return False, "URL invalide"
        
        return True, ""
    
    @staticmethod
    def validate_percentage(value: float) -> Tuple[bool, str]:
        """Valide un pourcentage"""
        return Validators.validate_numeric(value, 0, 100)
    
    @staticmethod
    def validate_price(price: Any) -> Tuple[bool, str]:
        """Valide un prix"""
        return Validators.validate_decimal(price, Decimal('0'), None, 2)
    
    @staticmethod
    def validate_quantity(quantity: Any) -> Tuple[bool, str]:
        """Valide une quantité"""
        return Validators.validate_integer(quantity, 1, 10000)
    
    @staticmethod
    def validate_product_data(product_data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """Valide les données d'un produit"""
        errors = {}
        
        # Nom
        valid, message = Validators.validate_required(product_data.get('name'), "nom")
        if not valid:
            errors['name'] = message
        
        # Prix d'achat
        valid, message = Validators.validate_price(product_data.get('purchase_price'))
        if not valid:
            errors['purchase_price'] = message
        
        # Prix de vente
        valid, message = Validators.validate_price(product_data.get('selling_price'))
        if not valid:
            errors['selling_price'] = message
        
        # Vérifier que prix vente > prix achat
        try:
            purchase = Decimal(str(product_data.get('purchase_price', 0)))
            selling = Decimal(str(product_data.get('selling_price', 0)))
            if selling <= purchase:
                errors['selling_price'] = "Le prix de vente doit être supérieur au prix d'achat"
        except:
            pass
        
        # Seuil d'alerte
        valid, message = Validators.validate_integer(product_data.get('alert_threshold', 10), 0, 10000)
        if not valid:
            errors['alert_threshold'] = message
        
        # SKU (optionnel)
        valid, message = Validators.validate_sku(product_data.get('sku', ''))
        if not valid:
            errors['sku'] = message
        
        # Code-barres (optionnel)
        valid, message = Validators.validate_barcode(product_data.get('barcode', ''))
        if not valid:
            errors['barcode'] = message
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_client_data(client_data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """Valide les données d'un client"""
        errors = {}
        
        # Nom complet
        valid, message = Validators.validate_required(client_data.get('full_name'), "nom complet")
        if not valid:
            errors['full_name'] = message
        
        # Téléphone
        valid, message = Validators.validate_phone(client_data.get('phone', ''))
        if not valid:
            errors['phone'] = message
        
        # Email (optionnel)
        valid, message = Validators.validate_email(client_data.get('email', ''))
        if not valid:
            errors['email'] = message
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_sale_data(sale_data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """Valide les données d'une vente"""
        errors = {}
        
        # Articles
        items = sale_data.get('items', [])
        if not items or len(items) == 0:
            errors['items'] = "Au moins un article est requis"
        else:
            for i, item in enumerate(items):
                if not item.get('product_id'):
                    errors[f'items_{i}'] = f"Article {i+1}: produit requis"
                if not item.get('quantity') or item.get('quantity', 0) <= 0:
                    errors[f'items_{i}_quantity'] = f"Article {i+1}: quantité invalide"
        
        # Méthode de paiement
        valid, message = Validators.validate_required(sale_data.get('payment_method'), "méthode de paiement")
        if not valid:
            errors['payment_method'] = message
        
        # Remise (optionnel)
        discount = sale_data.get('discount', 0)
        if discount:
            valid, message = Validators.validate_decimal(discount, Decimal('0'), None, 2)
            if not valid:
                errors['discount'] = message
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_expense_data(expense_data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """Valide les données d'une dépense"""
        errors = {}
        
        # Description
        valid, message = Validators.validate_required(expense_data.get('description'), "description")
        if not valid:
            errors['description'] = message
        
        # Montant
        valid, message = Validators.validate_price(expense_data.get('amount'))
        if not valid:
            errors['amount'] = message
        
        # Catégorie
        valid, message = Validators.validate_required(expense_data.get('category'), "catégorie")
        if not valid:
            errors['category'] = message
        
        return len(errors) == 0, errors

def display_validation_errors(errors: Dict[str, str]):
    """Affiche les erreurs de validation"""
    if errors:
        st.error("❌ Des erreurs ont été détectées :")
        for field, error in errors.items():
            st.write(f"• **{field}** : {error}")

def validate_form(form_data: Dict[str, Any], form_type: str) -> Tuple[bool, Dict[str, str]]:
    """Valide un formulaire selon son type"""
    if form_type == "product":
        return Validators.validate_product_data(form_data)
    elif form_type == "client":
        return Validators.validate_client_data(form_data)
    elif form_type == "sale":
        return Validators.validate_sale_data(form_data)
    elif form_type == "expense":
        return Validators.validate_expense_data(form_data)
    else:
        return True, {}