"""
Page de gestion des ventes
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

from services.api_client import APIClient
from services.sales_service import SalesService
from widgets.tables import create_sales_table
from widgets.cards import create_sale_card
from widgets.modals import create_sale_modal
from utils.formatters import format_currency, format_date
from utils.validators import Validators, display_validation_errors

def ventes_page():
    """Page de gestion des ventes"""
    
    st.title("💰 Gestion des Ventes")
    
    # Initialisation
    api_client = APIClient()
    sales_service = SalesService()
    
    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Ventes", 
        "🛒 Nouvelle Vente", 
        "💸 Remboursements",
        "📊 Analyse"
    ])
    
    # Onglet 1: Liste des ventes
    with tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 📦 Historique des Ventes")
        
        with col2:
            if st.button("🔄 Actualiser", use_container_width=True):
                st.rerun()
        
        # Filtres
        with st.expander("🔍 Filtres", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                start_date = st.date_input("Date début", datetime.now() - timedelta(days=30))
            
            with col2:
                end_date = st.date_input("Date fin", datetime.now())
            
            with col3:
                payment_status = st.selectbox(
                    "Statut paiement",
                    ["", "PAID", "PENDING", "PARTIAL"]
                )
            
            with col4:
                client_id = st.text_input("ID Client", "")
        
        # Récupérer les ventes
        with st.spinner("Chargement des ventes..."):
            sales = api_client.get_sales(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                payment_status=payment_status if payment_status else None,
                client_id=client_id if client_id else None
            )
        
        # Affichage
        if sales:
            create_sales_table(
                sales,
                title="Liste des ventes",
                page_size=15,
                show_search=True,
                show_export=True,
                selectable=True
            )
        else:
            st.info("Aucune vente trouvée")
    
    # Onglet 2: Nouvelle vente
    with tab2:
        st.markdown("### 🛒 Nouvelle Vente")
        
        # Panier dans session state
        if 'cart' not in st.session_state:
            st.session_state.cart = []
        
        # Colonnes gauche/droite
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Sélection des produits
            st.markdown("#### 📦 Produits")
            
            # Filtres produits
            col_a, col_b = st.columns(2)
            with col_a:
                search_product = st.text_input("Rechercher produit", "")
            with col_b:
                category_filter = st.selectbox(
                    "Catégorie",
                    ["", "Soins Visage", "Maquillage", "Parfums", "Accessoires"]
                )
            
            # Liste des produits
            products = api_client.get_products(
                search=search_product if search_product else None,
                category=category_filter if category_filter else None
            )
            
            if products:
                # Affichage en grille
                cols = st.columns(3)
                for idx, product in enumerate(products[:6]):  # Limiter à 6 produits pour la vue
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div style="
                            border: 1px solid #E9ECEF;
                            border-radius: 10px;
                            padding: 1rem;
                            margin-bottom: 1rem;
                            background: white;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div>
                                    <div style="font-weight: 600; color: #2C3E50; margin-bottom: 0.25rem;">
                                        {product.get('name', 'Produit')}
                                    </div>
                                    <div style="font-size: 0.875rem; color: #7F8C8D;">
                                        {product.get('category', '')}
                                    </div>
                                </div>
                                <div style="color: #FF6B9D; font-weight: 700;">
                                    {format_currency(product.get('selling_price', 0))}
                                </div>
                            </div>
                            
                            <div style="font-size: 0.875rem; color: #6C757D; margin: 0.5rem 0;">
                                Stock: {product.get('current_stock', 0)} unités
                            </div>
                            
                            <button onclick="addToCart('{product.get('id')}')" style="
                                width: 100%;
                                background: #FF6B9D;
                                color: white;
                                border: none;
                                padding: 0.5rem;
                                border-radius: 6px;
                                cursor: pointer;
                                font-weight: 500;
                            ">
                                Ajouter au panier
                            </button>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Aucun produit trouvé")
        
        with col2:
            # Panier et validation
            st.markdown("#### 🛒 Panier")
            
            cart = st.session_state.cart
            if not cart:
                st.info("Votre panier est vide")
            else:
                total = 0
                for item in cart:
                    st.markdown(f"""
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 0.5rem;
                        border-bottom: 1px solid #E9ECEF;
                    ">
                        <div>
                            <div style="font-weight: 500;">{item.get('name')}</div>
                            <div style="font-size: 0.875rem; color: #6C757D;">
                                {format_currency(item.get('unit_price'))} x {item.get('quantity')}
                            </div>
                        </div>
                        <div style="font-weight: 600;">
                            {format_currency(item.get('total'))}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    total += item.get('total', 0)
                
                st.markdown(f"""
                <div style="
                    margin-top: 1rem;
                    padding: 1rem;
                    background: #F8F9FA;
                    border-radius: 8px;
                ">
                    <div style="display: flex; justify-content: space-between; font-weight: 600;">
                        <span>Total:</span>
                        <span>{format_currency(total)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Informations client
            st.markdown("#### 👤 Client")
            
            client_options = ["Nouveau client", "Client existant"]
            client_type = st.radio("Type de client", client_options)
            
            if client_type == "Nouveau client":
                with st.form("new_client_form"):
                    client_name = st.text_input("Nom complet")
                    client_phone = st.text_input("Téléphone")
                    client_email = st.text_input("Email")
                    
                    if st.form_submit_button("Enregistrer client"):
                        # Validation client
                        pass
            else:
                # Recherche client existant
                client_search = st.text_input("Rechercher client")
                # Ici on aurait une liste de clients
            
            # Validation de la vente
            st.markdown("#### 💳 Paiement")
            
            payment_method = st.selectbox(
                "Méthode de paiement",
                ["CASH", "MOBILE_MONEY", "CARD", "BANK_TRANSFER"]
            )
            
            discount = st.number_input("Remise (FCFA)", min_value=0.0, value=0.0)
            
            if st.button("💾 Valider la vente", type="primary", use_container_width=True):
                if not cart:
                    st.error("Le panier est vide")
                else:
                    try:
                        # Préparation des données
                        sale_data = {
                            "items": [
                                {
                                    "product_id": item['product_id'],
                                    "quantity": item['quantity'],
                                    "unit_price": item['unit_price']
                                }
                                for item in cart
                            ],
                            "payment_method": payment_method,
                            "discount": discount,
                            "client_id": None  # À compléter avec le client sélectionné
                        }
                        
                        # Appel API
                        result = api_client.create_sale(sale_data)
                        if result:
                            st.success("✅ Vente enregistrée avec succès !")
                            st.balloons()
                            st.session_state.cart = []  # Vider le panier
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
    
    # Onglet 3: Remboursements
    with tab3:
        st.markdown("### 💸 Gestion des Remboursements")
        
        # Liste des remboursements
        refunds = api_client.get_all_refunds()
        
        if refunds:
            for refund in refunds:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{refund.get('refund_number')}**")
                        st.caption(f"Vente: {refund.get('invoice_number')}")
                    
                    with col2:
                        st.markdown(f"**{format_currency(refund.get('refund_amount'))}**")
                        st.caption(refund.get('refund_reason'))
                    
                    with col3:
                        status = refund.get('refund_status')
                        if status == "PENDING":
                            st.warning("⏳ En attente")
                        elif status == "APPROVED":
                            st.info("✅ Approuvé")
                        elif status == "COMPLETED":
                            st.success("💰 Traité")
                        else:
                            st.error("❌ Rejeté")
                    
                    with col4:
                        if st.button("Voir", key=f"view_refund_{refund.get('id')}"):
                            st.session_state.selected_refund = refund.get('id')
        else:
            st.info("Aucun remboursement trouvé")
    
    # Onglet 4: Analyse
    with tab4:
        st.markdown("### 📊 Analyse des Ventes")
        
        # Métriques
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("CA Total", format_currency(4500000))
        
        with col2:
            st.metric("Ventes Moyennes", format_currency(150000))
        
        with col3:
            st.metric("Panier Moyen", format_currency(25000))
        
        with col4:
            st.metric("Taux Conversion", "68%")
        
        # Graphiques
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Tendances Hebdomadaires")
            # Graphique des tendances
            pass
        
        with col2:
            st.markdown("#### 🏆 Meilleurs Vendeurs")
            # Top produits
            top_products = api_client.get_top_products(limit=5)
            if top_products:
                for product in top_products:
                    st.markdown(f"""
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 0.5rem;
                        border-bottom: 1px solid #E9ECEF;
                    ">
                        <div>{product.get('name')}</div>
                        <div style="font-weight: 600;">{format_currency(product.get('total_revenue'))}</div>
                    </div>
                    """, unsafe_allow_html=True)

# Fonction pour ajouter au panier
def add_to_cart(product_id: str):
    """Ajoute un produit au panier"""
    # Implémentation à compléter
    pass

if __name__ == "__main__":
    ventes_page()