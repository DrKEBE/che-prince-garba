"""
Page de gestion des clients
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any

from services.api_client import APIClient
from widgets.tables import create_clients_table
from widgets.cards import create_client_card
from utils.formatters import format_currency, format_date, format_phone_number
from utils.validators import Validators, display_validation_errors

def clients_page():
    """Page de gestion des clients"""
    
    st.title("👥 Gestion des Clients")
    
    # Initialisation
    api_client = APIClient()
    
    # Onglets
    tab1, tab2, tab3 = st.tabs([
        "📋 Liste Clients", 
        "➕ Nouveau Client", 
        "⭐ Clients VIP"
    ])
    
    # Onglet 1: Liste des clients
    with tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 📊 Liste des Clients")
        
        with col2:
            if st.button("🔄 Actualiser", use_container_width=True):
                st.rerun()
        
        # Filtres
        with st.expander("🔍 Filtres avancés", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                client_type = st.selectbox(
                    "Type de client",
                    ["", "REGULAR", "VIP", "FIDELITE", "WHOLESALER"]
                )
            
            with col2:
                min_purchases = st.number_input("Achats min (FCFA)", min_value=0, value=0)
            
            with col3:
                days_inactive = st.number_input("Inactif depuis (jours)", min_value=0, value=0)
        
        # Recherche rapide
        search_term = st.text_input(
            "🔍 Rechercher un client",
            placeholder="Nom, téléphone, email...",
            key="client_search"
        )
        
        # Récupérer les clients
        with st.spinner("Chargement des clients..."):
            clients = api_client.get_clients(
                search=search_term if search_term else None,
                client_type=client_type if client_type else None
            )
        
        # Affichage
        if clients:
            create_clients_table(
                clients,
                title="",
                page_size=15,
                show_search=False,
                show_export=True,
                selectable=True,
                key="clients_table"
            )
        else:
            st.info("Aucun client trouvé")
    
    # Onglet 2: Nouveau client
    with tab2:
        st.markdown("### ➕ Nouveau Client")
        
        with st.form("new_client_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Nom complet *", placeholder="Ex: Sophie Martin")
                email = st.text_input("Email", placeholder="sophie.martin@email.com")
                address = st.text_area("Adresse", placeholder="Adresse complète...", height=80)
            
            with col2:
                phone = st.text_input("Téléphone *", placeholder="+225 XX XX XX XX")
                client_type = st.selectbox(
                    "Type de client *",
                    ["REGULAR", "VIP", "FIDELITE", "WHOLESALER"],
                    format_func=lambda x: {
                        "REGULAR": "🟢 Régulier",
                        "VIP": "⭐ VIP", 
                        "FIDELITE": "👑 Fidélité",
                        "WHOLESALER": "🏢 Grossiste"
                    }[x]
                )
                notes = st.text_area("Notes", placeholder="Informations supplémentaires...", height=80)
            
            # Boutons
            col_a, col_b = st.columns([1, 3])
            with col_a:
                submit = st.form_submit_button(
                    "💾 Enregistrer",
                    type="primary",
                    use_container_width=True
                )
            
            if submit:
                # Validation
                client_data = {
                    "full_name": full_name,
                    "email": email,
                    "phone": phone,
                    "address": address,
                    "client_type": client_type,
                    "notes": notes
                }
                
                valid, errors = Validators.validate_client_data(client_data)
                
                if valid:
                    try:
                        # Appel API
                        result = api_client.create_client(client_data)
                        if result:
                            st.success("✅ Client créé avec succès !")
                            st.balloons()
                    except Exception as e:
                        st.error(f"❌ Erreur : {str(e)}")
                else:
                    display_validation_errors(errors)
    
    # Onglet 3: Clients VIP
    with tab3:
        st.markdown("### ⭐ Clients VIP")
        
        # Récupérer les meilleurs clients
        top_clients = api_client.get_top_clients(limit=10)
        
        if top_clients:
            # Métriques VIP
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_vip = sum(1 for client in top_clients if client.get('client_type') == 'VIP')
                st.metric("Clients VIP", total_vip)
            
            with col2:
                total_spent = sum(float(client.get('total_spent', 0)) for client in top_clients)
                st.metric("CA VIP", format_currency(total_spent))
            
            with col3:
                avg_spent = total_spent / len(top_clients) if top_clients else 0
                st.metric("Panier moyen", format_currency(avg_spent))
            
            with col4:
                avg_frequency = sum(client.get('purchase_count', 0) for client in top_clients) / len(top_clients) if top_clients else 0
                st.metric("Fréquence", f"{avg_frequency:.1f}x")
            
            # Liste des VIP
            st.markdown("---")
            st.markdown("#### 🏆 Classement VIP")
            
            for idx, client in enumerate(top_clients[:10], 1):
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                    
                    with col1:
                        st.markdown(f"### {medal}")
                    
                    with col2:
                        st.markdown(f"**{client.get('full_name', 'Client')}**")
                        st.caption(f"📱 {format_phone_number(client.get('phone', ''))}")
                    
                    with col3:
                        st.markdown(f"**{format_currency(client.get('total_spent', 0))}**")
                        st.caption(f"{client.get('purchase_count', 0)} achats")
                    
                    with col4:
                        if client.get('client_type') == 'VIP':
                            st.success("⭐ VIP")
                        else:
                            st.info("👑 Fidélité")
                    
                    st.divider()
        else:
            st.info("Aucun client VIP trouvé")

def view_client_details(client_id: str):
    """Affiche les détails d'un client"""
    api_client = APIClient()
    
    client = api_client.get_client(client_id)
    if not client:
        st.error("Client non trouvé")
        return
    
    st.title(f"👤 Profil Client: {client.get('full_name')}")
    
    # Onglets profil
    tab1, tab2, tab3 = st.tabs(["📋 Informations", "💰 Achats", "📊 Statistiques"])
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Avatar client
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="
                    width: 120px;
                    height: 120px;
                    background: linear-gradient(135deg, #FF6B9D 0%, #9B59B6 100%);
                    border-radius: 50%;
                    margin: 0 auto 1rem auto;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 3rem;
                    color: white;
                ">
                    {client.get('full_name', 'C')[0].upper()}
                </div>
                <div style="font-size: 1.5rem; font-weight: 600;">{client.get('full_name')}</div>
                <div style="color: #7F8C8D;">{client.get('client_type')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Informations détaillées
            st.markdown("#### 📋 Informations Personnelles")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**📱 Téléphone:** {format_phone_number(client.get('phone', ''))}")
                st.markdown(f"**📍 Adresse:** {client.get('address', 'Non renseignée')}")
            
            with col_b:
                st.markdown(f"**📧 Email:** {client.get('email', 'Non renseigné')}")
                st.markdown(f"**📅 Inscrit le:** {format_date(client.get('created_at'))}")
    
    with tab2:
        # Historique d'achat
        purchase_history = api_client.get_client_purchase_history(client_id)
        
        if purchase_history and purchase_history.get('sales'):
            st.markdown(f"#### 🛍️ Historique d'Achats ({len(purchase_history['sales'])})")
            
            for sale in purchase_history['sales']:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Facture {sale.get('invoice_number')}**")
                        st.caption(format_date(sale.get('sale_date')))
                    
                    with col2:
                        st.markdown(f"**{format_currency(sale.get('final_amount'))}**")
                        st.caption(f"{sale.get('items_count')} articles")
                    
                    with col3:
                        st.markdown(sale.get('payment_method', ''))
                    
                    with col4:
                        st.button("Voir", key=f"view_sale_{sale.get('id')}")
                    
                    st.divider()
        else:
            st.info("Aucun achat enregistré")
    
    with tab3:
        # Statistiques client
        stats = api_client.get_client_stats(client_id)
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Achats",
                    format_currency(stats.get('total_purchases', 0))
                )
            
            with col2:
                st.metric(
                    "Nombre d'Achats",
                    stats.get('total_transactions', 0)
                )
            
            with col3:
                st.metric(
                    "Panier Moyen",
                    format_currency(stats.get('average_purchase', 0))
                )
            
            with col4:
                last_purchase = stats.get('last_purchase')
                if last_purchase:
                    days_ago = (datetime.now() - last_purchase).days
                    st.metric("Dernier achat", f"Il y a {days_ago} jours")
                else:
                    st.metric("Dernier achat", "Jamais")

if __name__ == "__main__":
    clients_page()