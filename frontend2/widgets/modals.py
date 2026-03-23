"""
Widgets de modales élégantes pour l'application
"""
import streamlit as st
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import pandas as pd

from config.constants import COLORS
from utils.formatters import format_currency, format_date, format_boolean
from utils.validators import validate_form, display_validation_errors

class ModalWidgets:
    """Widgets de modales stylisées"""
    
    @staticmethod
    def confirmation_modal(
        title: str,
        message: str,
        on_confirm: Callable,
        on_cancel: Optional[Callable] = None,
        confirm_text: str = "Confirmer",
        cancel_text: str = "Annuler",
        confirm_color: str = "danger",
        size: str = "md"
    ):
        """Modal de confirmation élégante"""
        
        modal_html = f"""
        <style>
        .confirmation-modal {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            backdrop-filter: blur(4px);
            animation: fadeIn 0.3s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .modal-content {{
            background: white;
            border-radius: 16px;
            padding: 2rem;
            width: { '500px' if size == 'md' else '400px' if size == 'sm' else '600px' };
            max-width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            transform: translateY(0);
            animation: slideUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}
        
        @keyframes slideUp {{
            from {{ transform: translateY(30px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
        
        .modal-header {{
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .modal-title {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #2C3E50;
            flex-grow: 1;
        }}
        
        .modal-icon {{
            font-size: 2rem;
            margin-right: 1rem;
            color: {COLORS[confirm_color]};
        }}
        
        .modal-body {{
            margin-bottom: 2rem;
            color: #5D6D7E;
            line-height: 1.6;
            font-size: 1.1rem;
        }}
        
        .modal-actions {{
            display: flex;
            justify-content: flex-end;
            gap: 1rem;
            margin-top: 2rem;
        }}
        
        .modal-btn {{
            padding: 0.75rem 2rem;
            border-radius: 10px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            font-size: 1rem;
        }}
        
        .btn-confirm {{
            background: {COLORS[confirm_color]};
            color: white;
            box-shadow: 0 4px 15px {COLORS[confirm_color]}40;
        }}
        
        .btn-confirm:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px {COLORS[confirm_color]}60;
        }}
        
        .btn-cancel {{
            background: #F8F9FA;
            color: #5D6D7E;
            border: 1px solid #E9ECEF;
        }}
        
        .btn-cancel:hover {{
            background: #E9ECEF;
        }}
        </style>
        
        <div class="confirmation-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="modal-icon">⚠️</div>
                    <div class="modal-title">{title}</div>
                </div>
                <div class="modal-body">
                    {message}
                </div>
                <div class="modal-actions">
                    <button class="modal-btn btn-cancel" onclick="document.getElementById('cancel-btn').click()">
                        {cancel_text}
                    </button>
                    <button class="modal-btn btn-confirm" onclick="document.getElementById('confirm-btn').click()">
                        {confirm_text}
                    </button>
                </div>
            </div>
        </div>
        """
        
        st.markdown(modal_html, unsafe_allow_html=True)
        
        # Boutons réels pour gérer les actions
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button(cancel_text, key=f"cancel_{title}", type="secondary"):
                if on_cancel:
                    on_cancel()
                st.session_state[f"modal_{title}"] = False
        with col3:
            if st.button(confirm_text, key=f"confirm_{title}", type="primary"):
                on_confirm()
                st.session_state[f"modal_{title}"] = False
    
    @staticmethod
    def product_modal(product: Dict[str, Any], on_close: Callable):
        """Modal de détail produit élégante"""
        
        # Calculer le statut du stock
        stock_status = ""
        if product.get('current_stock', 0) <= 0:
            stock_status = "🔴 Rupture"
        elif product.get('current_stock', 0) <= product.get('alert_threshold', 10):
            stock_status = "🟡 Faible stock"
        else:
            stock_status = "🟢 En stock"
        
        modal_html = f"""
        <style>
        .product-modal {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            backdrop-filter: blur(4px);
        }}
        
        .product-modal-content {{
            background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
            border-radius: 20px;
            width: 700px;
            max-width: 90%;
            max-height: 90%;
            overflow-y: auto;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
            animation: productModalSlide 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}
        
        @keyframes productModalSlide {{
            from {{ transform: translateY(40px) scale(0.95); opacity: 0; }}
            to {{ transform: translateY(0) scale(1); opacity: 1; }}
        }}
        
        .product-header {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
            padding: 2rem;
            border-radius: 20px 20px 0 0;
            color: white;
            position: relative;
        }}
        
        .product-title {{
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .product-category {{
            background: rgba(255, 255, 255, 0.2);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
            font-size: 0.9rem;
        }}
        
        .product-close {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .product-close:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: rotate(90deg);
        }}
        
        .product-body {{
            padding: 2rem;
        }}
        
        .product-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .product-image {{
            width: 100%;
            height: 300px;
            object-fit: cover;
            border-radius: 12px;
            background: linear-gradient(45deg, #f0f0f0, #ffffff);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 4rem;
            color: {COLORS['primary']};
        }}
        
        .product-info {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #5D6D7E;
        }}
        
        .info-value {{
            color: #2C3E50;
            font-weight: 500;
        }}
        
        .price-badge {{
            background: linear-gradient(135deg, {COLORS['success']} 0%, #27ae60 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 10px;
            font-size: 1.2rem;
            font-weight: 700;
            display: inline-block;
            margin-top: 1rem;
        }}
        
        .stock-badge {{
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 10px;
            font-weight: 600;
            margin-top: 0.5rem;
        }}
        
        .stock-good {{ background: #d4edda; color: #155724; }}
        .stock-warning {{ background: #fff3cd; color: #856404; }}
        .stock-danger {{ background: #f8d7da; color: #721c24; }}
        
        .product-description {{
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            margin-top: 1rem;
            border-left: 4px solid {COLORS['primary']};
        }}
        </style>
        
        <div class="product-modal">
            <div class="product-modal-content">
                <div class="product-header">
                    <button class="product-close" onclick="document.getElementById('close-btn').click()">×</button>
                    <div class="product-title">{product.get('name', 'Produit')}</div>
                    <div class="product-category">{product.get('category', 'Non catégorisé')}</div>
                </div>
                
                <div class="product-body">
                    <div class="product-grid">
                        <div class="product-image">
                            💄
                        </div>
                        
                        <div class="product-info">
                            <div class="info-row">
                                <span class="info-label">SKU</span>
                                <span class="info-value">{product.get('sku', 'N/A')}</span>
                            </div>
                            
                            <div class="info-row">
                                <span class="info-label">Code-barres</span>
                                <span class="info-value">{product.get('barcode', 'N/A')}</span>
                            </div>
                            
                            <div class="info-row">
                                <span class="info-label">Marque</span>
                                <span class="info-value">{product.get('brand', 'N/A')}</span>
                            </div>
                            
                            <div class="info-row">
                                <span class="info-label">Prix d'achat</span>
                                <span class="info-value">{format_currency(product.get('purchase_price', 0))}</span>
                            </div>
                            
                            <div class="info-row">
                                <span class="info-label">Prix de vente</span>
                                <span class="info-value price-badge">{format_currency(product.get('selling_price', 0))}</span>
                            </div>
                            
                            <div class="info-row">
                                <span class="info-label">Marge</span>
                                <span class="info-value" style="color: {COLORS['success']};">{product.get('margin', 0)}%</span>
                            </div>
                            
                            <div class="info-row">
                                <span class="info-label">Stock actuel</span>
                                <span class="info-value">
                                    <span class="stock-badge {'stock-danger' if product.get('current_stock', 0) <= 0 else 'stock-warning' if product.get('current_stock', 0) <= product.get('alert_threshold', 10) else 'stock-good'}">
                                        {product.get('current_stock', 0)} unités
                                    </span>
                                </span>
                            </div>
                            
                            <div class="info-row">
                                <span class="info-label">Seuil d'alerte</span>
                                <span class="info-value">{product.get('alert_threshold', 10)} unités</span>
                            </div>
                        </div>
                    </div>
                    
                    {f'<div class="product-description">{product.get("description", "Aucune description")}</div>' if product.get('description') else ''}
                </div>
            </div>
        </div>
        """
        
        st.markdown(modal_html, unsafe_allow_html=True)
        
        # Bouton pour fermer la modal
        if st.button("✕", key="close-btn", help="Fermer"):
            on_close()
    
    @staticmethod
    def quick_sale_modal(products: List[Dict[str, Any]], on_sale: Callable):
        """Modal de vente rapide élégante"""
        
        modal_html = """
        <style>
        .quick-sale-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            backdrop-filter: blur(4px);
        }
        
        .quick-sale-content {
            background: white;
            border-radius: 20px;
            width: 800px;
            max-width: 90%;
            max-height: 90%;
            overflow-y: auto;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
            animation: quickSaleSlide 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        @keyframes quickSaleSlide {
            from { transform: translateY(40px) scale(0.95); opacity: 0; }
            to { transform: translateY(0) scale(1); opacity: 1; }
        }
        
        .quick-sale-header {
            background: linear-gradient(135deg, #2ECC71 0%, #27ae60 100%);
            padding: 2rem;
            border-radius: 20px 20px 0 0;
            color: white;
            text-align: center;
        }
        
        .quick-sale-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .quick-sale-subtitle {
            opacity: 0.9;
            font-size: 1rem;
        }
        
        .quick-sale-body {
            padding: 2rem;
        }
        
        .product-select-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .product-select-card {
            border: 2px solid #E9ECEF;
            border-radius: 12px;
            padding: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            background: white;
        }
        
        .product-select-card:hover {
            border-color: #FF6B9D;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(255, 107, 157, 0.1);
        }
        
        .product-select-card.selected {
            border-color: #2ECC71;
            background: linear-gradient(135deg, #f8fff9 0%, #e8f5e9 100%);
        }
        
        .product-select-name {
            font-weight: 600;
            color: #2C3E50;
            margin-bottom: 0.5rem;
        }
        
        .product-select-price {
            color: #2ECC71;
            font-weight: 700;
            font-size: 1.2rem;
        }
        
        .product-select-stock {
            font-size: 0.8rem;
            color: #7F8C8D;
        }
        
        .cart-section {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            margin-top: 2rem;
        }
        
        .cart-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid #E9ECEF;
        }
        
        .cart-total {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2C3E50;
            text-align: right;
            margin-top: 1rem;
        }
        
        .quantity-controls {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .quantity-btn {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            border: 2px solid #FF6B9D;
            background: white;
            color: #FF6B9D;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .quantity-btn:hover {
            background: #FF6B9D;
            color: white;
        }
        
        .quantity-display {
            min-width: 40px;
            text-align: center;
            font-weight: 600;
        }
        </style>
        """
        
        st.markdown(modal_html, unsafe_allow_html=True)
        
        # Interface de sélection des produits
        st.markdown('<div class="quick-sale-modal"><div class="quick-sale-content">', unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div class="quick-sale-header">
            <div class="quick-sale-title">💳 Vente Rapide</div>
            <div class="quick-sale-subtitle">Sélectionnez les produits à vendre</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Body
        with st.container():
            st.markdown('<div class="quick-sale-body">', unsafe_allow_html=True)
            
            # Sélection des produits
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📦 Produits disponibles")
                
                # Affichage des produits sous forme de cartes
                for product in products:
                    if st.button(
                        f"**{product.get('name')}**\n\n"
                        f"💰 {format_currency(product.get('selling_price', 0))}\n"
                        f"📦 Stock: {product.get('current_stock', 0)}",
                        key=f"product_{product.get('id')}",
                        use_container_width=True
                    ):
                        # Ajouter au panier
                        st.session_state.setdefault('cart', []).append({
                            **product,
                            'quantity': 1
                        })
                        st.rerun()
            
            with col2:
                st.subheader("🛒 Panier")
                
                # Affichage du panier
                cart = st.session_state.get('cart', [])
                
                if cart:
                    total = 0
                    for item in cart:
                        col_qty, col_name, col_price = st.columns([1, 2, 1])
                        with col_qty:
                            new_qty = st.number_input(
                                "Qty",
                                min_value=1,
                                max_value=item.get('current_stock', 100),
                                value=item.get('quantity', 1),
                                key=f"qty_{item.get('id')}",
                                label_visibility="collapsed"
                            )
                            item['quantity'] = new_qty
                        
                        with col_name:
                            st.write(item.get('name'))
                        
                        with col_price:
                            price = item.get('selling_price', 0) * new_qty
                            total += price
                            st.write(format_currency(price))
                    
                    st.divider()
                    st.markdown(f"### Total: {format_currency(total)}")
                    
                    # Bouton de vente
                    if st.button("💳 Finaliser la vente", type="primary", use_container_width=True):
                        on_sale(cart)
                        st.session_state.cart = []
                        st.success("Vente effectuée avec succès!")
                        st.rerun()
                else:
                    st.info("🛒 Panier vide")
                    st.markdown("Sélectionnez des produits à gauche pour les ajouter au panier.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    @staticmethod
    def client_modal(client: Dict[str, Any], on_close: Callable):
        """Modal de détail client élégante"""
        
        modal_html = f"""
        <style>
        .client-modal {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            backdrop-filter: blur(4px);
        }}
        
        .client-modal-content {{
            background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
            border-radius: 20px;
            width: 600px;
            max-width: 90%;
            max-height: 90%;
            overflow-y: auto;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
            animation: clientModalSlide 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}
        
        @keyframes clientModalSlide {{
            from {{ transform: translateY(40px) scale(0.95); opacity: 0; }}
            to {{ transform: translateY(0) scale(1); opacity: 1; }}
        }}
        
        .client-header {{
            background: linear-gradient(135deg, {COLORS['secondary']} 0%, #8e44ad 100%);
            padding: 2rem;
            border-radius: 20px 20px 0 0;
            color: white;
            position: relative;
        }}
        
        .client-avatar {{
            width: 100px;
            height: 100px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            margin: 0 auto 1rem;
            border: 4px solid rgba(255, 255, 255, 0.3);
        }}
        
        .client-title {{
            font-size: 1.8rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.5rem;
        }}
        
        .client-type {{
            background: rgba(255, 255, 255, 0.2);
            padding: 0.5rem 1.5rem;
            border-radius: 20px;
            display: inline-block;
            font-size: 0.9rem;
            margin: 0 auto;
        }}
        
        .client-body {{
            padding: 2rem;
        }}
        
        .client-info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .info-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #E9ECEF;
        }}
        
        .info-card-title {{
            font-size: 0.9rem;
            color: #7F8C8D;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }}
        
        .info-card-value {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #2C3E50;
        }}
        
        .loyalty-badge {{
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            color: #856404;
            padding: 0.75rem 1.5rem;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1.1rem;
            display: inline-block;
            margin-top: 0.5rem;
        }}
        
        .stats-section {{
            margin-top: 2rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-top: 1rem;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: {COLORS['primary']};
        }}
        
        .stat-label {{
            font-size: 0.8rem;
            color: #7F8C8D;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        </style>
        
        <div class="client-modal">
            <div class="client-modal-content">
                <div class="client-header">
                    <div class="client-avatar">
                        👤
                    </div>
                    <div class="client-title">{client.get('full_name', 'Client')}</div>
                    <div class="client-type">{client.get('client_type', 'REGULAR')}</div>
                </div>
                
                <div class="client-body">
                    <div class="client-info-grid">
                        <div class="info-card">
                            <div class="info-card-title">📞 Contact</div>
                            <div class="info-card-value">{client.get('phone', 'N/A')}</div>
                            <div class="info-card-value" style="font-size: 1rem;">{client.get('email', 'N/A')}</div>
                        </div>
                        
                        <div class="info-card">
                            <div class="info-card-title">🏠 Adresse</div>
                            <div class="info-card-value">{client.get('city', 'N/A')}</div>
                            <div class="info-card-value" style="font-size: 1rem;">{client.get('address', 'N/A')}</div>
                        </div>
                    </div>
                    
                    <div class="info-card">
                        <div class="info-card-title">🎯 Fidélité</div>
                        <div class="loyalty-badge">
                            ⭐ {client.get('loyalty_points', 0)} Points
                        </div>
                    </div>
                    
                    <div class="stats-section">
                        <h3>📊 Statistiques</h3>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-value">{client.get('total_purchases', 0)}</div>
                                <div class="stat-label">Achats</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{format_currency(client.get('total_spent', 0))}</div>
                                <div class="stat-label">Dépensé</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{format_date(client.get('last_purchase', 'N/A'))}</div>
                                <div class="stat-label">Dernier achat</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        
        st.markdown(modal_html, unsafe_allow_html=True)
        
        # Bouton pour fermer la modal
        if st.button("✕", key="close_client_modal", help="Fermer"):
            on_close()
    
    @staticmethod
    def filter_modal(filters: Dict[str, Any], on_apply: Callable, on_reset: Callable):
        """Modal de filtres avancés"""
        
        modal_html = f"""
        <style>
        .filter-modal {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            backdrop-filter: blur(4px);
        }}
        
        .filter-modal-content {{
            background: white;
            border-radius: 20px;
            width: 500px;
            max-width: 90%;
            max-height: 90%;
            overflow-y: auto;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
            animation: filterModalSlide 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}
        
        @keyframes filterModalSlide {{
            from {{ transform: translateY(40px) scale(0.95); opacity: 0; }}
            to {{ transform: translateY(0) scale(1); opacity: 1; }}
        }}
        
        .filter-header {{
            background: linear-gradient(135deg, {COLORS['info']} 0%, #2980b9 100%);
            padding: 1.5rem 2rem;
            border-radius: 20px 20px 0 0;
            color: white;
        }}
        
        .filter-title {{
            font-size: 1.5rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .filter-body {{
            padding: 2rem;
        }}
        
        .filter-group {{
            margin-bottom: 2rem;
        }}
        
        .filter-group-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #2C3E50;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .filter-actions {{
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid #E9ECEF;
        }}
        
        .filter-btn {{
            flex: 1;
            padding: 0.75rem;
            border-radius: 10px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            font-size: 1rem;
        }}
        
        .btn-apply {{
            background: linear-gradient(135deg, {COLORS['success']} 0%, #27ae60 100%);
            color: white;
        }}
        
        .btn-reset {{
            background: #F8F9FA;
            color: #5D6D7E;
            border: 1px solid #E9ECEF;
        }}
        
        .btn-apply:hover, .btn-reset:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        </style>
        
        <div class="filter-modal">
            <div class="filter-modal-content">
                <div class="filter-header">
                    <div class="filter-title">
                        🔍 Filtres Avancés
                    </div>
                </div>
                
                <div class="filter-body">
        """
        
        st.markdown(modal_html, unsafe_allow_html=True)
        
        # Formulaire de filtres
        with st.form("advanced_filters"):
            # Filtres par date
            st.subheader("📅 Date")
            date_cols = st.columns(2)
            with date_cols[0]:
                start_date = st.date_input("Du", value=filters.get('start_date'))
            with date_cols[1]:
                end_date = st.date_input("Au", value=filters.get('end_date'))
            
            # Filtres par montant
            st.subheader("💰 Montant")
            amount_cols = st.columns(2)
            with amount_cols[0]:
                min_amount = st.number_input("Minimum", value=filters.get('min_amount', 0))
            with amount_cols[1]:
                max_amount = st.number_input("Maximum", value=filters.get('max_amount', 1000000))
            
            # Filtres par statut
            st.subheader("📊 Statut")
            status_options = ["Tous", "Actif", "Inactif", "En attente", "Terminé"]
            selected_status = st.selectbox("Statut", options=status_options, 
                                         index=status_options.index(filters.get('status', 'Tous')))
            
            # Boutons d'action
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("🔄 Réinitialiser", type="secondary", use_container_width=True):
                    on_reset()
            with col2:
                if st.form_submit_button("✅ Appliquer les filtres", type="primary", use_container_width=True):
                    on_apply({
                        'start_date': start_date,
                        'end_date': end_date,
                        'min_amount': min_amount,
                        'max_amount': max_amount,
                        'status': selected_status
                    })
        
        st.markdown("""
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Instance globale
modal = ModalWidgets()