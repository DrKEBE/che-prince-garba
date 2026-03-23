"""
Composants de cartes pour l'interface
"""
import streamlit as st
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import plotly.graph_objects as go

from config.theme import ThemeManager
from utils.formatters import format_currency, format_percentage, format_date

class CardComponents:
    """Composants de cartes"""
    
    @staticmethod
    def create_stat_card(
        title: str,
        value: Any,
        change: Optional[str] = None,
        icon: str = "📊",
        color: str = "primary",
        subtitle: Optional[str] = None,
        trend: Optional[str] = None
    ) -> str:
        """
        Crée une carte de statistique
        """
        colors = ThemeManager.get_color_palette()
        
        # Déterminer la couleur
        if color == "primary":
            bg_color = colors["primary"]
        elif color == "success":
            bg_color = colors["status"]["success"]
        elif color == "warning":
            bg_color = colors["status"]["warning"]
        elif color == "danger":
            bg_color = colors["status"]["error"]
        elif color == "info":
            bg_color = colors["status"]["info"]
        else:
            bg_color = color
        
        # Déterminer l'icône de tendance
        trend_icon = ""
        if trend:
            if trend == "up":
                trend_icon = "📈"
            elif trend == "down":
                trend_icon = "📉"
            elif trend == "stable":
                trend_icon = "📊"
        
        # Déterminer la couleur du changement
        change_color = "#7F8C8D"
        change_class = ""
        if change:
            if change.startswith("+"):
                change_color = "#28A745"
                change_class = "positive"
            elif change.startswith("-"):
                change_color = "#DC3545"
                change_class = "negative"
        
        card_html = f"""
        <div class="custom-card card-{color}">
            <div class="custom-card-header">
                <div>
                    <div class="custom-card-title">
                        <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                        {title}
                    </div>
                    {f'<div class="custom-card-subtitle">{subtitle}</div>' if subtitle else ''}
                </div>
                {f'<span style="font-size: 2rem;">{trend_icon}</span>' if trend_icon else ''}
            </div>
            
            <div class="custom-card-body">
                <div style="
                    font-size: 2rem;
                    font-weight: 700;
                    color: {bg_color};
                    margin: 0.5rem 0;
                ">{value}</div>
                
                {f'''
                <div class="stat-change {change_class}" style="
                    color: {change_color};
                    font-weight: 500;
                    display: flex;
                    align-items: center;
                    gap: 0.25rem;
                ">
                    <span>{change}</span>
                    {f'<span>{trend_icon}</span>' if trend_icon else ''}
                </div>
                ''' if change else ''}
            </div>
        </div>
        """
        
        return card_html
    
    @staticmethod
    def create_product_card(
        product: Dict[str, Any],
        show_actions: bool = True,
        compact: bool = False
    ) -> str:
        """
        Crée une carte de produit
        """
        # Récupérer les informations du produit
        name = product.get('name', 'Produit sans nom')
        category = product.get('category', 'Non catégorisé')
        price = format_currency(product.get('selling_price', 0))
        stock = product.get('current_stock', 0)
        threshold = product.get('alert_threshold', 10)
        images = product.get('images', [])
        
        # Déterminer le statut du stock
        if stock <= 0:
            stock_status = "🔴 Rupture"
            stock_class = "stock-out"
        elif stock <= threshold:
            stock_status = "🟡 Alerte"
            stock_class = "stock-low"
        else:
            stock_status = "🟢 En stock"
            stock_class = "stock-available"
        
        # Image du produit
        image_url = images[0] if images else ""
        image_html = f"""
        <div style="
            width: 100%;
            height: 150px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
            overflow: hidden;
        ">
            {f'<img src="{image_url}" style="width: 100%; height: 100%; object-fit: cover;">' if image_url else '<span style="font-size: 3rem;">💄</span>'}
        </div>
        """
        
        if compact:
            image_html = f"""
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 1rem;
                flex-shrink: 0;
            ">
                {f'<img src="{image_url}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;">' if image_url else '<span style="font-size: 1.5rem;">💄</span>'}
            </div>
            """
        
        # Actions
        actions_html = ""
        if show_actions:
            actions_html = f"""
            <div class="custom-card-footer">
                <button onclick="addToCart('{product.get('id')}')" style="
                    background: #FF6B9D;
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: 500;
                    transition: all 0.3s;
                " onmouseover="this.style.opacity='0.8'"
                onmouseout="this.style.opacity='1'">
                    Ajouter au panier
                </button>
                
                <button onclick="viewProduct('{product.get('id')}')" style="
                    background: transparent;
                    color: #6C757D;
                    border: 1px solid #DEE2E6;
                    padding: 0.5rem 1rem;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: 500;
                    transition: all 0.3s;
                " onmouseover="this.style.borderColor='#FF6B9D'; this.style.color='#FF6B9D'"
                onmouseout="this.style.borderColor='#DEE2E6'; this.style.color='#6C757D'">
                    Détails
                </button>
            </div>
            """
        
        if compact:
            card_html = f"""
            <div class="custom-card product-card" style="
                display: flex;
                align-items: center;
                padding: 1rem;
            ">
                {image_html}
                
                <div style="flex-grow: 1;">
                    <div style="
                        font-weight: 600;
                        color: #2C3E50;
                        margin-bottom: 0.25rem;
                    ">{name}</div>
                    
                    <div style="
                        font-size: 0.875rem;
                        color: #7F8C8D;
                        margin-bottom: 0.5rem;
                    ">{category}</div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="
                            font-weight: 700;
                            color: #FF6B9D;
                            font-size: 1.125rem;
                        ">{price}</div>
                        
                        <div class="{stock_class}" style="
                            padding: 0.25rem 0.75rem;
                            border-radius: 20px;
                            font-size: 0.75rem;
                            font-weight: 500;
                        ">{stock_status}</div>
                    </div>
                </div>
            </div>
            """
        else:
            card_html = f"""
            <div class="custom-card product-card">
                {image_html}
                
                <div style="
                    font-weight: 600;
                    color: #2C3E50;
                    margin-bottom: 0.5rem;
                    font-size: 1.125rem;
                ">{name}</div>
                
                <div style="
                    font-size: 0.875rem;
                    color: #7F8C8D;
                    margin-bottom: 0.5rem;
                ">{category}</div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <div style="
                        font-weight: 700;
                        color: #FF6B9D;
                        font-size: 1.25rem;
                    ">{price}</div>
                    
                    <div class="{stock_class}" style="
                        padding: 0.25rem 0.75rem;
                        border-radius: 20px;
                        font-size: 0.75rem;
                        font-weight: 500;
                    ">{stock_status}</div>
                </div>
                
                <div style="
                    font-size: 0.875rem;
                    color: #6C757D;
                    margin-bottom: 1rem;
                ">
                    Stock: <strong>{stock}</strong> unités • Seuil: {threshold}
                </div>
                
                {actions_html}
            </div>
            """
        
        return card_html
    
    @staticmethod
    def create_sale_card(sale: Dict[str, Any]) -> str:
        """
        Crée une carte de vente
        """
        invoice_number = sale.get('invoice_number', 'N/A')
        client_name = sale.get('client_name', 'Client non spécifié')
        amount = format_currency(sale.get('final_amount', 0))
        date = format_date(sale.get('sale_date'))
        status = sale.get('payment_status', 'PAID')
        items_count = sale.get('items_count', 0)
        
        # Couleur selon le statut
        if status == "PAID":
            status_color = "#28A745"
            status_icon = "✅"
        elif status == "PENDING":
            status_color = "#FFC107"
            status_icon = "⏳"
        elif status == "PARTIAL":
            status_color = "#17A2B8"
            status_icon = "💰"
        else:
            status_color = "#6C757D"
            status_icon = "📋"
        
        card_html = f"""
        <div class="custom-card">
            <div class="custom-card-header">
                <div>
                    <div class="custom-card-title">
                        {status_icon} Vente {invoice_number}
                    </div>
                    <div class="custom-card-subtitle">
                        {date} • {client_name}
                    </div>
                </div>
                <div style="
                    background: {status_color};
                    color: white;
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    font-size: 0.75rem;
                    font-weight: 500;
                ">
                    {status}
                </div>
            </div>
            
            <div class="custom-card-body">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="
                            font-size: 1.5rem;
                            font-weight: 700;
                            color: #2C3E50;
                        ">{amount}</div>
                        <div style="
                            font-size: 0.875rem;
                            color: #6C757D;
                            margin-top: 0.25rem;
                        ">
                            {items_count} article{'s' if items_count > 1 else ''}
                        </div>
                    </div>
                    
                    <button onclick="viewSale('{sale.get('id')}')" style="
                        background: transparent;
                        color: #FF6B9D;
                        border: 1px solid #FF6B9D;
                        padding: 0.5rem 1rem;
                        border-radius: 6px;
                        cursor: pointer;
                        font-weight: 500;
                        transition: all 0.3s;
                    " onmouseover="this.style.background='#FF6B9D'; this.style.color='white'"
                    onmouseout="this.style.background='transparent'; this.style.color='#FF6B9D'">
                        Voir détails
                    </button>
                </div>
            </div>
        </div>
        """
        
        return card_html
    
    @staticmethod
    def create_client_card(client: Dict[str, Any]) -> str:
        """
        Crée une carte de client
        """
        name = client.get('full_name', 'Client sans nom')
        phone = client.get('phone', 'Non renseigné')
        email = client.get('email', 'Non renseigné')
        client_type = client.get('client_type', 'REGULAR')
        total_purchases = format_currency(client.get('total_purchases', 0))
        last_purchase = format_date(client.get('last_purchase'))
        
        # Icône selon le type de client
        if client_type == "VIP":
            icon = "⭐"
            color = "#FFC107"
        elif client_type == "FIDELITE":
            icon = "👑"
            color = "#9B59B6"
        else:
            icon = "👤"
            color = "#6C757D"
        
        card_html = f"""
        <div class="custom-card">
            <div class="custom-card-header">
                <div>
                    <div class="custom-card-title">
                        <span style="font-size: 1.5rem; margin-right: 0.5rem; color: {color};">{icon}</span>
                        {name}
                    </div>
                    <div class="custom-card-subtitle">
                        {phone} • {email}
                    </div>
                </div>
                <div style="
                    background: {color};
                    color: white;
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    font-size: 0.75rem;
                    font-weight: 500;
                ">
                    {client_type}
                </div>
            </div>
            
            <div class="custom-card-body">
                <div style="margin-bottom: 1rem;">
                    <div style="
                        font-size: 1.25rem;
                        font-weight: 700;
                        color: #2C3E50;
                    ">{total_purchases}</div>
                    <div style="
                        font-size: 0.875rem;
                        color: #6C757D;
                    ">Total des achats</div>
                </div>
                
                <div style="
                    font-size: 0.875rem;
                    color: #6C757D;
                    margin-bottom: 1rem;
                ">
                    Dernier achat: <strong>{last_purchase if last_purchase != 'N/A' else 'Jamais'}</strong>
                </div>
                
                <div style="display: flex; gap: 0.5rem;">
                    <button onclick="viewClient('{client.get('id')}')" style="
                        background: #FF6B9D;
                        color: white;
                        border: none;
                        padding: 0.5rem 1rem;
                        border-radius: 6px;
                        cursor: pointer;
                        font-weight: 500;
                        flex-grow: 1;
                        transition: all 0.3s;
                    " onmouseover="this.style.opacity='0.8'"
                    onmouseout="this.style.opacity='1'">
                        Profil
                    </button>
                    
                    <button onclick="newSaleForClient('{client.get('id')}')" style="
                        background: #28A745;
                        color: white;
                        border: none;
                        padding: 0.5rem 1rem;
                        border-radius: 6px;
                        cursor: pointer;
                        font-weight: 500;
                        flex-grow: 1;
                        transition: all 0.3s;
                    " onmouseover="this.style.opacity='0.8'"
                    onmouseout="this.style.opacity='1'">
                        Nouvelle vente
                    </button>
                </div>
            </div>
        </div>
        """
        
        return card_html
    
    @staticmethod
    def create_info_card(
        title: str,
        content: str,
        icon: str = "ℹ️",
        color: str = "info",
        actions: List[Tuple[str, str]] = None
    ) -> str:
        """
        Crée une carte d'information
        """
        colors = ThemeManager.get_color_palette()
        
        if color == "info":
            bg_color = colors["status"]["info"]
        elif color == "warning":
            bg_color = colors["status"]["warning"]
        elif color == "success":
            bg_color = colors["status"]["success"]
        elif color == "danger":
            bg_color = colors["status"]["error"]
        else:
            bg_color = color
        
        # Actions
        actions_html = ""
        if actions:
            actions_html = '<div style="display: flex; gap: 0.5rem; margin-top: 1rem;">'
            for action_text, action_url in actions:
                actions_html += f"""
                <a href="{action_url}" style="
                    display: inline-block;
                    padding: 0.5rem 1rem;
                    background: {bg_color};
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 500;
                    transition: all 0.3s;
                " onmouseover="this.style.opacity='0.8'"
                onmouseout="this.style.opacity='1'">
                    {action_text}
                </a>
                """
            actions_html += '</div>'
        
        card_html = f"""
        <div class="custom-card card-{color}">
            <div style="
                display: flex;
                align-items: flex-start;
                gap: 1rem;
            ">
                <div style="
                    font-size: 2rem;
                    color: {bg_color};
                    flex-shrink: 0;
                ">
                    {icon}
                </div>
                
                <div style="flex-grow: 1;">
                    <div style="
                        font-weight: 600;
                        color: #2C3E50;
                        margin-bottom: 0.5rem;
                        font-size: 1.125rem;
                    ">
                        {title}
                    </div>
                    
                    <div style="
                        color: #6C757D;
                        line-height: 1.6;
                    ">
                        {content}
                    </div>
                    
                    {actions_html}
                </div>
            </div>
        </div>
        """
        
        return card_html

# Fonctions d'export
def create_stat_card(*args, **kwargs):
    """Crée une carte de statistique (fonction d'export)"""
    return CardComponents.create_stat_card(*args, **kwargs)

def create_metric_card(*args, **kwargs):
    """Alias pour create_stat_card (fonction d'export)"""
    return CardComponents.create_stat_card(*args, **kwargs)

def create_product_card(*args, **kwargs):
    """Crée une carte de produit (fonction d'export)"""
    return CardComponents.create_product_card(*args, **kwargs)

def create_sale_card(*args, **kwargs):
    """Crée une carte de vente (fonction d'export)"""
    return CardComponents.create_sale_card(*args, **kwargs)

def create_client_card(*args, **kwargs):
    """Crée une carte de client (fonction d'export)"""
    return CardComponents.create_client_card(*args, **kwargs)