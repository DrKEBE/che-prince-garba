# frontend/app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Optional
import uuid

# Configuration
st.set_page_config(
    page_title="Luxe Beauté Management",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration API
API_BASE_URL = "http://localhost:8000/api/v1"
DEV_MODE = True  # Mode développement avec authentification simulée

# Styles CSS personnalisés
st.markdown("""
<style>
    /* Style global */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header */
    .header {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Cartes */
    .card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(45deg, #6a11cb, #2575fc);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #2575fc, #6a11cb);
        transform: scale(1.05);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Stats */
    .stat-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Tables */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Alertes */
    .alert-warning {
        background: linear-gradient(45deg, #ff9a9e, #fad0c4);
        color: #856404;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .alert-danger {
        background: linear-gradient(45deg, #ff416c, #ff4b2b);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .alert-success {
        background: linear-gradient(45deg, #00b09b, #96c93d);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Badges */
    .badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .badge-success {
        background: linear-gradient(45deg, #00b09b, #96c93d);
        color: white;
    }
    
    .badge-warning {
        background: linear-gradient(45deg, #ff9a9e, #fad0c4);
        color: #856404;
    }
    
    .badge-danger {
        background: linear-gradient(45deg, #ff416c, #ff4b2b);
        color: white;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Fonctions d'authentification
def init_session_state():
    """Initialise l'état de session"""
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    if 'cart' not in st.session_state:
        st.session_state.cart = []

def login():
    """Authentification utilisateur"""
    if DEV_MODE:
        # Mode développement - authentification simulée
        st.session_state.user = {
            "id": 1,
            "username": "admin",
            "role": "ADMIN",
            "full_name": "Administrateur"
        }
        st.session_state.token = "dev-token"
        return True
    
    with st.sidebar.form("login_form"):
        st.markdown("### 🔐 Connexion")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        
        if st.form_submit_button("Se connecter", use_container_width=True):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/auth/token",
                    data={"username": username, "password": password}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.user = data["user"]
                    st.success("✅ Connexion réussie!")
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
            except Exception as e:
                st.error(f"⚠️ Erreur de connexion: {str(e)}")
                return False
    return False

# Fonctions API avec gestion du token
def make_request(method, endpoint, **kwargs):
    """Effectue une requête API avec gestion du token"""
    headers = kwargs.get('headers', {})
    if st.session_state.token:
        headers['Authorization'] = f"Bearer {st.session_state.token}"
    kwargs['headers'] = headers
    
    try:
        response = requests.request(method, f"{API_BASE_URL}{endpoint}", **kwargs)
        if response.status_code == 401:
            st.error("Session expirée. Veuillez vous reconnecter.")
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
        return response
    except Exception as e:
        st.error(f"⚠️ Erreur API: {str(e)}")
        return None

# Fonctions de récupération de données
def get_dashboard_stats():
    """Récupère les statistiques du dashboard"""
    response = make_request("GET", "/dashboard/stats")
    if response and response.status_code == 200:
        return response.json()
    return None

def get_products(search=None, category=None):
    """Récupère la liste des produits"""
    params = {}
    if search:
        params['search'] = search
    if category:
        params['category'] = category
    
    response = make_request("GET", "/products", params=params)
    if response and response.status_code == 200:
        return response.json()
    return []

def get_sales(start_date=None, end_date=None):
    """Récupère les ventes"""
    params = {}
    if start_date:
        params['start_date'] = start_date.isoformat()
    if end_date:
        params['end_date'] = end_date.isoformat()
    
    response = make_request("GET", "/sales", params=params)
    if response and response.status_code == 200:
        return response.json()
    return []

def get_clients():
    """Récupère la liste des clients"""
    response = make_request("GET", "/clients")
    if response and response.status_code == 200:
        return response.json()
    return []

def get_stock_alerts():
    """Récupère les alertes de stock"""
    response = make_request("GET", "/stock/alerts")
    if response and response.status_code == 200:
        return response.json()
    return {"low_stock": [], "out_of_stock": []}

# Pages de l'application
def show_dashboard():
    """Page Dashboard"""
    st.markdown('<div class="header fade-in">', unsafe_allow_html=True)
    st.title("📊 Tableau de Bord")
    st.markdown("**Vue d'ensemble de votre boutique**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Charger les statistiques
    stats = get_dashboard_stats()
    
    if stats:
        # Cartes de statistiques
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Chiffre d'affaires", f"{stats.get('daily_revenue', 0):,.0f} FCFA")
            st.caption("Aujourd'hui")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Produits", stats.get('total_products', 0))
            stock_status = f"⚠️ {stats.get('low_stock', 0)} faible"
            st.caption(stock_status)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Clients", stats.get('total_clients', 0))
            new_clients = f"↑ {stats.get('new_clients_month', 0)} ce mois"
            st.caption(new_clients)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Ventes", stats.get('total_sales', 0))
            profit = f"💰 {stats.get('daily_profit', 0):,.0f} FCFA"
            st.caption(profit)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
            st.subheader("📈 Tendances des ventes")
            
            # Données simulées (à remplacer par des données réelles)
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
            sales_data = pd.DataFrame({
                'Date': dates,
                'Ventes': [1000000, 1200000, 900000, 1500000, 1300000, 
                          1400000, 1600000, 1800000, 1700000, 2000000, 
                          1900000, 2200000]
            })
            
            fig = px.line(sales_data, x='Date', y='Ventes', 
                         title="Évolution mensuelle",
                         color_discrete_sequence=['#6a11cb'])
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
            st.subheader("🏷️ Top Catégories")
            
            # Données simulées
            categories = ['Soin Visage', 'Maquillage', 'Parfums', 'Corps', 'Cheveux']
            values = [35, 25, 20, 15, 5]
            
            fig = px.pie(values=values, names=categories, 
                        color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_layout(height=300, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Alertes de stock
        st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
        st.subheader("🚨 Alertes")
        
        alerts = get_stock_alerts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if alerts.get('out_of_stock'):
                st.markdown('<div class="alert-danger">', unsafe_allow_html=True)
                st.write("**Rupture de stock:**")
                for product in alerts['out_of_stock'][:3]:
                    st.write(f"• {product.get('name', 'Produit')}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if alerts.get('low_stock'):
                st.markdown('<div class="alert-warning">', unsafe_allow_html=True)
                st.write("**Stock faible:**")
                for product in alerts['low_stock'][:3]:
                    st.write(f"• {product.get('name', 'Produit')}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Dernières ventes
        st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
        st.subheader("🛒 Dernières ventes")
        
        sales = get_sales()
        if sales:
            df_sales = pd.DataFrame(sales)[:5]
            st.dataframe(
                df_sales[['invoice_number', 'client_name', 'final_amount', 'sale_date']],
                use_container_width=True,
                column_config={
                    "invoice_number": "Facture",
                    "client_name": "Client",
                    "final_amount": "Montant",
                    "sale_date": "Date"
                }
            )
        else:
            st.info("Aucune vente récente")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_products():
    """Page Produits"""
    st.markdown('<div class="header fade-in">', unsafe_allow_html=True)
    st.title("📦 Gestion des Produits")
    st.markdown("**Inventaire et gestion des produits cosmétiques**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Barre de recherche et filtres
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search = st.text_input("🔍 Rechercher un produit", "")
    
    with col2:
        categories = ["Tous", "Soin Visage", "Maquillage", "Parfums", "Corps", "Cheveux"]
        category = st.selectbox("Catégorie", categories)
    
    with col3:
        if st.button("➕ Nouveau produit", use_container_width=True):
            st.session_state.show_product_form = True
    
    # Récupérer les produits
    products = get_products(search if search else None, 
                           category if category != "Tous" else None)
    
    if st.session_state.get('show_product_form', False):
        show_product_form()
    
    # Affichage des produits
    if products:
        # Convertir en DataFrame pour l'affichage
        df_products = pd.DataFrame(products)
        
        # Formater les colonnes
        df_display = pd.DataFrame({
            "Produit": df_products['name'],
            "Catégorie": df_products['category'],
            "Prix d'achat": df_products['purchase_price'],
            "Prix de vente": df_products['selling_price'],
            "Stock": df_products.get('stock', 0),
            "Statut": df_products.get('status', 'N/A'),
            "Marge": df_products.get('margin', 0)
        })
        
        # Appliquer le style
        def color_status(val):
            if val == "RUPTURE":
                return "background-color: #ff416c; color: white;"
            elif val == "ALERTE":
                return "background-color: #ff9a9e; color: #856404;"
            else:
                return "background-color: #00b09b; color: white;"
        
        st.dataframe(
            df_display.style.applymap(color_status, subset=['Statut']),
            use_container_width=True,
            height=400
        )
        
        # Graphique de répartition
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📊 Répartition par catégorie")
            
            category_counts = df_products['category'].value_counts()
            fig = px.pie(values=category_counts.values, 
                        names=category_counts.index,
                        color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📈 Top produits par marge")
            
            top_products = df_products.nlargest(10, 'margin')
            fig = px.bar(top_products, x='name', y='margin',
                        color='margin',
                        color_continuous_scale='viridis')
            fig.update_layout(height=300, xaxis_title="", yaxis_title="Marge %")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Aucun produit trouvé")

def show_product_form():
    """Formulaire d'ajout de produit"""
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.subheader("➕ Nouveau produit")
    
    with st.form("product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nom du produit", placeholder="Ex: Crème hydratante luxe")
            category = st.selectbox("Catégorie", 
                                   ["Soin Visage", "Maquillage", "Parfums", "Corps", "Cheveux", "Autre"])
            sku = st.text_input("SKU", placeholder="Code unique")
            purchase_price = st.number_input("Prix d'achat (FCFA)", min_value=0.0, step=100.0)
        
        with col2:
            selling_price = st.number_input("Prix de vente (FCFA)", min_value=0.0, step=100.0)
            initial_stock = st.number_input("Stock initial", min_value=0, step=1)
            alert_threshold = st.number_input("Seuil d'alerte", min_value=0, value=10, step=1)
            barcode = st.text_input("Code-barres", placeholder="Facultatif")
        
        description = st.text_area("Description", placeholder="Description du produit...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                # Créer le produit
                product_data = {
                    "name": name,
                    "category": category,
                    "purchase_price": float(purchase_price),
                    "selling_price": float(selling_price),
                    "alert_threshold": int(alert_threshold),
                    "sku": sku,
                    "barcode": barcode,
                    "description": description,
                    "initial_stock": int(initial_stock)
                }
                
                response = make_request("POST", "/products", json=product_data)
                if response and response.status_code == 201:
                    st.success("✅ Produit créé avec succès!")
                    st.session_state.show_product_form = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la création")
        
        with col2:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                st.session_state.show_product_form = False
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_sales():
    """Page Ventes"""
    st.markdown('<div class="header fade-in">', unsafe_allow_html=True)
    st.title("💰 Gestion des Ventes")
    st.markdown("**Enregistrement et suivi des ventes**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["📝 Nouvelle vente", "📋 Historique", "📊 Statistiques"])
    
    with tab1:
        show_new_sale()
    
    with tab2:
        show_sales_history()
    
    with tab3:
        show_sales_stats()

def show_new_sale():
    """Interface de nouvelle vente"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🛒 Panier")
        
        # Panier
        if not st.session_state.cart:
            st.info("👈 Ajoutez des produits depuis la liste")
        else:
            cart_df = pd.DataFrame(st.session_state.cart)
            cart_df['Total'] = cart_df['quantity'] * cart_df['price']
            
            st.dataframe(
                cart_df[['product', 'quantity', 'price', 'Total']],
                use_container_width=True,
                column_config={
                    "product": "Produit",
                    "quantity": "Qté",
                    "price": "Prix unitaire",
                    "Total": "Total"
                }
            )
            
            total = cart_df['Total'].sum()
            st.metric("Total panier", f"{total:,.0f} FCFA")
            
            if st.button("🔄 Vider le panier", use_container_width=True):
                st.session_state.cart = []
                st.rerun()
        
        # Client
        st.subheader("👤 Client")
        clients = get_clients()
        client_options = {c['full_name']: c['id'] for c in clients}
        
        col1, col2 = st.columns(2)
        with col1:
            client_choice = st.selectbox("Client existant", 
                                        ["Nouveau client"] + list(client_options.keys()))
        
        if client_choice == "Nouveau client":
            with st.expander("Créer un nouveau client"):
                new_client_name = st.text_input("Nom complet")
                new_client_phone = st.text_input("Téléphone")
                if st.button("Créer client"):
                    if new_client_name and new_client_phone:
                        st.success(f"Client {new_client_name} créé")
                    else:
                        st.warning("Veuillez remplir tous les champs")
    
    with col2:
        st.subheader("📦 Produits")
        
        # Recherche de produits
        products = get_products()
        product_options = {p['name']: p for p in products}
        
        selected_product = st.selectbox("Sélectionner un produit", list(product_options.keys()))
        
        if selected_product:
            product = product_options[selected_product]
            
            st.markdown(f"""
            **Prix:** {product['selling_price']:,.0f} FCFA  
            **Stock:** {product.get('stock', 0)} unités  
            **Statut:** <span class='badge badge-{'danger' if product.get('status') == 'RUPTURE' else 'warning' if product.get('status') == 'ALERTE' else 'success'}'>{
                product.get('status', 'N/A')}</span>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                quantity = st.number_input("Quantité", min_value=1, 
                                         max_value=product.get('stock', 100), 
                                         value=1)
            
            with col2:
                if st.button("➕ Ajouter au panier", use_container_width=True):
                    st.session_state.cart.append({
                        'product_id': product['id'],
                        'product': product['name'],
                        'price': product['selling_price'],
                        'quantity': quantity
                    })
                    st.success(f"{quantity} x {product['name']} ajouté!")
                    time.sleep(0.5)
                    st.rerun()
    
    # Paiement
    st.markdown("---")
    st.subheader("💳 Paiement")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        payment_method = st.selectbox("Méthode", ["CASH", "Saraly", "CARD", "BANK_TRANSFER"])
    
    with col2:
        discount = st.number_input("Remise (FCFA)", min_value=0.0, value=0.0, step=100.0)
    
    with col3:
        notes = st.text_input("Notes", placeholder="Notes facultatives")
    
    if st.button("✅ Finaliser la vente", type="primary", use_container_width=True):
        if st.session_state.cart:
            # Préparer les données
            sale_data = {
                "payment_method": payment_method,
                "discount": float(discount),
                "items": [
                    {
                        "product_id": item['product_id'],
                        "quantity": item['quantity'],
                        "unit_price": float(item['price'])
                    }
                    for item in st.session_state.cart
                ]
            }
            
            # Client existant
            if client_choice != "Nouveau client" and client_choice in client_options:
                sale_data["client_id"] = client_options[client_choice]
            
            # Envoyer la vente
            response = make_request("POST", "/sales", json=sale_data)
            if response and response.status_code == 201:
                sale_result = response.json()
                st.success(f"✅ Vente enregistrée! Facture: {sale_result.get('invoice_number')}")
                st.balloons()
                st.session_state.cart = []
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ Erreur lors de l'enregistrement de la vente")
        else:
            st.warning("⚠️ Le panier est vide!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_sales_history():
    """Historique des ventes"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Date de début", 
                                  datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("Date de fin", datetime.now())
    
    # Récupérer les ventes
    sales = get_sales(start_date, end_date)
    
    if sales:
        df_sales = pd.DataFrame(sales)
        
        # Statistiques
        total_sales = len(sales)
        total_amount = df_sales['final_amount'].sum()
        avg_ticket = df_sales['final_amount'].mean()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Nombre de ventes", total_sales)
        col2.metric("Chiffre d'affaires", f"{total_amount:,.0f} FCFA")
        col3.metric("Panier moyen", f"{avg_ticket:,.0f} FCFA")
        
        # Tableau des ventes
        st.dataframe(
            df_sales[['invoice_number', 'client_name', 'sale_date', 
                     'final_amount', 'payment_method', 'payment_status']],
            use_container_width=True,
            column_config={
                "invoice_number": "Facture",
                "client_name": "Client",
                "sale_date": "Date",
                "final_amount": "Montant",
                "payment_method": "Paiement",
                "payment_status": "Statut"
            }
        )
        
        # Graphique journalier
        df_sales['date'] = pd.to_datetime(df_sales['sale_date']).dt.date
        daily_sales = df_sales.groupby('date')['final_amount'].sum().reset_index()
        
        fig = px.line(daily_sales, x='date', y='final_amount',
                     title="Ventes journalières",
                     color_discrete_sequence=['#6a11cb'])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune vente trouvée pour cette période")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_sales_stats():
    """Statistiques des ventes"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Récupérer les ventes des 30 derniers jours
    sales = get_sales(datetime.now() - timedelta(days=30), datetime.now())
    
    if sales:
        df_sales = pd.DataFrame(sales)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Par méthode de paiement")
            payment_stats = df_sales.groupby('payment_method')['final_amount'].sum()
            fig = px.pie(values=payment_stats.values, names=payment_stats.index,
                        color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Tendance hebdomadaire")
            df_sales['week'] = pd.to_datetime(df_sales['sale_date']).dt.isocalendar().week
            weekly_sales = df_sales.groupby('week')['final_amount'].sum()
            fig = px.bar(x=weekly_sales.index, y=weekly_sales.values,
                        labels={'x': 'Semaine', 'y': 'Montant (FCFA)'},
                        color_discrete_sequence=['#2575fc'])
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_clients():
    """Page Clients"""
    st.markdown('<div class="header fade-in">', unsafe_allow_html=True)
    st.title("👥 Gestion des Clients")
    st.markdown("**Suivi et fidélisation de la clientèle**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Barre d'actions
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search = st.text_input("🔍 Rechercher un client", "")
    
    with col2:
        if st.button("➕ Nouveau client", use_container_width=True):
            st.session_state.show_client_form = True
    
    # Formulaire nouveau client
    if st.session_state.get('show_client_form', False):
        show_client_form()
    
    # Récupérer les clients
    clients = get_clients()
    
    if clients:
        df_clients = pd.DataFrame(clients)
        
        # Filtrer par recherche
        if search:
            df_clients = df_clients[df_clients['full_name'].str.contains(search, case=False, na=False)]
        
        # Affichage
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📋 Liste des clients")
            
            st.dataframe(
                df_clients[['full_name', 'phone', 'email', 'client_type', 
                           'total_purchases', 'last_purchase']],
                use_container_width=True,
                column_config={
                    "full_name": "Nom",
                    "phone": "Téléphone",
                    "email": "Email",
                    "client_type": "Type",
                    "total_purchases": "Total achats",
                    "last_purchase": "Dernier achat"
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("🏆 Top clients")
            
            top_clients = df_clients.nlargest(5, 'total_purchases')
            
            for _, client in top_clients.iterrows():
                st.markdown(f"""
                **{client['full_name']}**  
                📞 {client['phone']}  
                💰 {client['total_purchases']:,.0f} FCFA  
                🎯 {client['client_type']}
                ---
                """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Statistiques clients
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Statistiques clients")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            client_types = df_clients['client_type'].value_counts()
            fig = px.pie(values=client_types.values, names=client_types.index,
                        title="Répartition par type",
                        color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Clients actifs (achat dans les 30 derniers jours)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            active_clients = df_clients[
                pd.to_datetime(df_clients['last_purchase']) > thirty_days_ago
            ].shape[0]
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=active_clients,
                title={'text': "Clients actifs (30j)"},
                gauge={'axis': {'range': [0, len(df_clients)]}}
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            st.subheader("📈 Performance")
            st.metric("Nombre total", len(df_clients))
            st.metric("Clients VIP", 
                     len(df_clients[df_clients['client_type'] == 'VIP']))
            st.metric("Valeur moyenne", 
                     f"{df_clients['total_purchases'].mean():,.0f} FCFA")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Aucun client trouvé")

def show_client_form():
    """Formulaire de création de client"""
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.subheader("👤 Nouveau client")
    
    with st.form("client_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Nom complet *", placeholder="Ex: Marie Dupont")
            phone = st.text_input("Téléphone *", placeholder="Ex: +225 01 23 45 67 89")
            email = st.text_input("Email", placeholder="Ex: client@email.com")
        
        with col2:
            client_type = st.selectbox("Type de client", 
                                      ["REGULAR", "VIP", "FIDELITE", "WHOLESALER"])
            address = st.text_input("Adresse", "ATT Bougou 320")
            city = st.text_input("Ville", placeholder="Ex: Abidjan")
        
        notes = st.text_area("Notes", placeholder="Informations complémentaires...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                if full_name and phone:
                    client_data = {
                        "full_name": full_name,
                        "phone": phone,
                        "email": email if email else None,
                        "client_type": client_type,
                        "address": address,
                        "city": city if city else None,
                        "notes": notes if notes else None
                    }
                    
                    response = make_request("POST", "/clients", json=client_data)
                    if response and response.status_code == 201:
                        st.success("✅ Client créé avec succès!")
                        st.session_state.show_client_form = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la création")
                else:
                    st.warning("⚠️ Les champs marqués * sont obligatoires")
        
        with col2:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                st.session_state.show_client_form = False
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_stock():
    """Page Stock"""
    st.markdown('<div class="header fade-in">', unsafe_allow_html=True)
    st.title("📦 Gestion du Stock")
    st.markdown("**Suivi et optimisation des niveaux de stock**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Récupérer les alertes
    alerts = get_stock_alerts()
    
    # Alertes
    col1, col2 = st.columns(2)
    
    with col1:
        if alerts.get('out_of_stock'):
            st.markdown('<div class="alert-danger">', unsafe_allow_html=True)
            st.subheader("🚨 Rupture de stock")
            for product in alerts['out_of_stock'][:5]:
                st.write(f"• **{product.get('name')}** - {product.get('sku', 'N/A')}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if alerts.get('low_stock'):
            st.markdown('<div class="alert-warning">', unsafe_allow_html=True)
            st.subheader("⚠️ Stock faible")
            for product in alerts['low_stock'][:5]:
                current = product.get('current_stock', 0)
                threshold = product.get('alert_threshold', 10)
                st.write(f"• **{product.get('name')}** - {current}/{threshold}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Mouvements de stock
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Nouveau mouvement de stock")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        products = get_products()
        product_options = {p['name']: p['id'] for p in products}
        selected_product = st.selectbox("Produit", list(product_options.keys()))
    
    with col2:
        movement_type = st.selectbox("Type", ["IN", "OUT", "ADJUSTMENT", "RETURN"])
    
    with col3:
        quantity = st.number_input("Quantité", min_value=1, value=1)
    
    reason = st.text_input("Raison", placeholder="Ex: Réapprovisionnement, Vente, etc.")
    notes = st.text_area("Notes", placeholder="Notes supplémentaires...")
    
    if st.button("✅ Enregistrer le mouvement", use_container_width=True):
        if selected_product:
            movement_data = {
                "product_id": product_options[selected_product],
                "movement_type": movement_type,
                "quantity": quantity,
                "reason": reason,
                "notes": notes
            }
            
            response = make_request("POST", "/stock/movements", json=movement_data)
            if response and response.status_code == 200:
                st.success("✅ Mouvement enregistré!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Erreur lors de l'enregistrement")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analyse du stock
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Analyse du stock")
    
    if products:
        df_products = pd.DataFrame(products)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Valeur du stock
            df_products['valeur'] = df_products['purchase_price'] * df_products.get('stock', 0)
            total_value = df_products['valeur'].sum()
            
            fig = go.Figure(go.Indicator(
                mode="number",
                value=total_value,
                title={"text": "Valeur totale du stock"},
                number={"prefix": "", "suffix": " FCFA"}
            ))
            fig.update_layout(height=200)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Rotation
            slow_moving = df_products[
                (df_products.get('stock', 0) > 0) &
                (df_products.get('stock', 0) > df_products.get('alert_threshold', 10) * 3)
            ]
            
            st.metric("Produits à rotation lente", len(slow_moving))
        
        # Graphique ABC
        st.subheader("📈 Analyse ABC")
        
        df_products_sorted = df_products.sort_values('valeur', ascending=False)
        df_products_sorted['cumulative'] = df_products_sorted['valeur'].cumsum()
        df_products_sorted['percentage'] = (df_products_sorted['cumulative'] / total_value) * 100
        
        fig = px.line(df_products_sorted, x=range(len(df_products_sorted)), y='percentage',
                     labels={'x': 'Produits (classés)', 'y': 'Valeur cumulative %'},
                     color_discrete_sequence=['#6a11cb'])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_accounting():
    """Page Comptabilité"""
    st.markdown('<div class="header fade-in">', unsafe_allow_html=True)
    st.title("💰 Comptabilité")
    st.markdown("**Gestion financière et rapports**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Tableau de bord", "💸 Dépenses", "📑 Rapports"])
    
    with tab1:
        show_accounting_dashboard()
    
    with tab2:
        show_expenses()
    
    with tab3:
        show_financial_reports()

def show_accounting_dashboard():
    """Tableau de bord comptable"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Statistiques financières
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("CA du jour", "1,250,000 FCFA", "+5.2%")
    
    with col2:
        st.metric("Bénéfice", "450,000 FCFA", "+12.3%")
    
    with col3:
        st.metric("Dépenses", "150,000 FCFA", "-3.1%")
    
    with col4:
        st.metric("Marge", "36%", "+2.1%")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # CA mensuel
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun']
        revenue = [1200000, 1350000, 1250000, 1550000, 1650000, 1800000]
        
        fig = px.line(x=months, y=revenue, 
                     labels={'x': 'Mois', 'y': 'Chiffre d\'affaires (FCFA)'},
                     color_discrete_sequence=['#6a11cb'])
        fig.update_layout(height=300, title="Chiffre d'affaires mensuel")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Répartition des dépenses
        categories = ['Achats', 'Personnel', 'Loyer', 'Marketing', 'Autres']
        values = [45, 30, 15, 7, 3]
        
        fig = px.pie(values=values, names=categories,
                    color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_layout(height=300, title="Répartition des dépenses")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_expenses():
    """Gestion des dépenses"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Formulaire nouvelle dépense
    with st.expander("➕ Nouvelle dépense", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox("Catégorie", 
                                   ["ACHAT", "PERSONNEL", "LOYER", "MARKETING", "UTILITAIRES", "AUTRES"])
            amount = st.number_input("Montant (FCFA)", min_value=0.0, step=1000.0)
        
        with col2:
            payment_method = st.selectbox("Méthode de paiement", 
                                         ["CASH", "BANK_TRANSFER", "CARD", "CHECK"])
            expense_date = st.date_input("Date", datetime.now())
        
        description = st.text_input("Description", placeholder="Détails de la dépense...")
        
        if st.button("💾 Enregistrer la dépense", use_container_width=True):
            st.success("Dépense enregistrée! (simulation)")
    
    # Liste des dépenses récentes
    st.subheader("📋 Dépenses récentes")
    
    # Données simulées
    expenses_data = [
        {"date": "2024-01-15", "category": "ACHAT", "description": "Produits cosmétiques", "amount": 750000},
        {"date": "2024-01-10", "category": "PERSONNEL", "description": "Salaires", "amount": 500000},
        {"date": "2024-01-05", "category": "LOYER", "description": "Loyer boutique", "amount": 300000},
        {"date": "2024-01-02", "category": "MARKETING", "description": "Publicité Instagram", "amount": 150000},
    ]
    
    df_expenses = pd.DataFrame(expenses_data)
    st.dataframe(df_expenses, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_financial_reports():
    """Rapports financiers"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Date de début", 
                                  datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("Date de fin", datetime.now())
    
    # Types de rapports
    report_type = st.selectbox("Type de rapport", 
                              ["Bilan", "Compte de résultat", "Flux de trésorerie"])
    
    # Bouton génération
    if st.button("📄 Générer le rapport", use_container_width=True):
        st.success(f"Rapport {report_type} généré pour la période {start_date} au {end_date}")
        
        # Affichage du rapport simulé
        st.markdown("---")
        st.subheader(f"📑 Rapport {report_type}")
        
        if report_type == "Bilan":
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**ACTIF**")
                st.write("💵 Trésorerie: 2,500,000 FCFA")
                st.write("📦 Stocks: 1,200,000 FCFA")
                st.write("🏢 Immobilisations: 3,500,000 FCFA")
                st.write("**Total Actif: 7,200,000 FCFA**")
            
            with col2:
                st.markdown("**PASSIF**")
                st.write("🏦 Dettes fournisseurs: 850,000 FCFA")
                st.write("💳 Emprunts: 2,000,000 FCFA")
                st.write("👥 Capitaux propres: 4,350,000 FCFA")
                st.write("**Total Passif: 7,200,000 FCFA**")
        
        elif report_type == "Compte de résultat":
            st.write("💰 **Produits**")
            st.write("Ventes: 15,000,000 FCFA")
            st.write("Autres produits: 500,000 FCFA")
            st.write("**Total produits: 15,500,000 FCFA**")
            
            st.write("")
            st.write("💸 **Charges**")
            st.write("Achats: 9,000,000 FCFA")
            st.write("Personnel: 3,000,000 FCFA")
            st.write("Loyer: 1,200,000 FCFA")
            st.write("Autres charges: 800,000 FCFA")
            st.write("**Total charges: 14,000,000 FCFA**")
            
            st.write("")
            st.markdown("**🎯 Résultat: 1,500,000 FCFA**")
        
        else:  # Flux de trésorerie
            st.write("📥 **Encaissements**")
            st.write("Clients: 14,500,000 FCFA")
            st.write("**Total encaissements: 14,500,000 FCFA**")
            
            st.write("")
            st.write("📤 **Décaissements**")
            st.write("Fournisseurs: 8,500,000 FCFA")
            st.write("Salaires: 3,000,000 FCFA")
            st.write("Loyer: 1,200,000 FCFA")
            st.write("**Total décaissements: 12,700,000 FCFA**")
            
            st.write("")
            st.markdown("**💰 Flux net: 1,800,000 FCFA**")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_appointments():
    """Page Rendez-vous"""
    st.markdown('<div class="header fade-in">', unsafe_allow_html=True)
    st.title("📅 Gestion des Rendez-vous")
    st.markdown("**Planification et suivi des rendez-vous beauté**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Vue calendrier
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🗓️ Calendrier")
    
    # Sélection de date
    selected_date = st.date_input("Sélectionner une date", datetime.now())
    
    # Rendez-vous du jour (simulés)
    appointments_today = [
        {"time": "09:00", "client": "Marie Dupont", "service": "Soin visage", "status": "CONFIRMED"},
        {"time": "11:00", "client": "Sophie Martin", "service": "Maquillage", "status": "CONFIRMED"},
        {"time": "14:00", "client": "Julie Bernard", "service": "Massage", "status": "PENDING"},
        {"time": "16:00", "client": "Claire Petit", "service": "Épilations", "status": "CONFIRMED"},
    ]
    
    # Affichage horaire
    st.write(f"**Rendez-vous du {selected_date.strftime('%d/%m/%Y')}**")
    
    for app in appointments_today:
        col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
        with col1:
            st.write(f"**{app['time']}**")
        with col2:
            st.write(app['client'])
        with col3:
            st.write(app['service'])
        with col4:
            status_color = "green" if app['status'] == "CONFIRMED" else "orange"
            st.markdown(f"<span style='color:{status_color}'>{app['status']}</span>", 
                       unsafe_allow_html=True)
        st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Nouveau rendez-vous
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("➕ Nouveau rendez-vous")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sélection client
        clients = get_clients()
        client_options = {c['full_name']: c['id'] for c in clients}
        selected_client = st.selectbox("Client", list(client_options.keys()))
        
        # Services
        services = ["Soin visage", "Maquillage", "Massage", "Épilations", 
                   "Manucure", "Pédicure", "Coiffure", "Autre"]
        service = st.selectbox("Service", services)
        
        # Employé
        employees = ["Esthéticienne 1", "Esthéticienne 2", "Esthéticienne 3"]
        employee = st.selectbox("Esthéticienne", employees)
    
    with col2:
        # Date et heure
        appointment_date = st.date_input("Date du rendez-vous", datetime.now())
        appointment_time = st.time_input("Heure", datetime.now().time())
        
        # Durée
        duration = st.selectbox("Durée (minutes)", [30, 60, 90, 120])
        
        # Prix
        price = st.number_input("Prix (FCFA)", min_value=0.0, step=1000.0, value=15000.0)
    
    notes = st.text_area("Notes", placeholder="Notes ou demandes spéciales...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Prendre rendez-vous", use_container_width=True):
            st.success(f"Rendez-vous confirmé pour {selected_client} à {appointment_time}!")
            time.sleep(1)
            st.rerun()
    
    with col2:
        if st.button("📋 Voir tous les rendez-vous", use_container_width=True):
            st.info("Fonctionnalité en développement...")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_settings():
    """Page Paramètres"""
    st.markdown('<div class="header fade-in">', unsafe_allow_html=True)
    st.title("⚙️ Paramètres")
    st.markdown("**Configuration du système**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🛠️ Général", "👥 Utilisateurs", "🏪 Boutique", "🔒 Sécurité"])
    
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Paramètres généraux")
        
        col1, col2 = st.columns(2)
        
        with col1:
            app_name = st.text_input("Nom de l'application", "Luxe Beauté Management")
            currency = st.selectbox("Devise", ["FCFA", "EUR", "USD", "XOF"])
            timezone = st.selectbox("Fuseau horaire", ["UTC", "Europe/Paris", "Africa/Abidjan"])
        
        with col2:
            language = st.selectbox("Langue", ["Français", "Anglais", "Espagnol"])
            date_format = st.selectbox("Format de date", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
            items_per_page = st.slider("Éléments par page", 10, 100, 50)
        
        if st.button("💾 Enregistrer les paramètres", use_container_width=True):
            st.success("Paramètres enregistrés!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Gestion des utilisateurs")
        
        # Liste des utilisateurs
        users = [
            {"name": "Admin", "role": "Administrateur", "email": "admin@luxe-beaute.com", "status": "Actif"},
            {"name": "Manager", "role": "Gestionnaire", "email": "manager@luxe-beaute.com", "status": "Actif"},
            {"name": "Cashier", "role": "Caissier", "email": "cashier@luxe-beaute.com", "status": "Actif"},
            {"name": "Esthetician", "role": "Esthéticienne", "email": "esthetician@luxe-beaute.com", "status": "Actif"},
        ]
        
        df_users = pd.DataFrame(users)
        st.dataframe(df_users, use_container_width=True)
        
        # Ajout d'utilisateur
        with st.expander("➕ Ajouter un utilisateur"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Nom complet")
                new_email = st.text_input("Email")
            
            with col2:
                new_role = st.selectbox("Rôle", ["Administrateur", "Gestionnaire", "Caissier", "Esthéticienne"])
                new_password = st.text_input("Mot de passe", type="password")
            
            if st.button("Créer l'utilisateur"):
                st.success(f"Utilisateur {new_name} créé!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Informations boutique")
        
        col1, col2 = st.columns(2)
        
        with col1:
            shop_name = st.text_input("Nom de la boutique", "Luxe Beauté")
            address = st.text_input("Adresse", "ATT Bougou 320")
            city = st.text_input("Ville", "Abidjan")
            country = st.text_input("Pays", "Côte d'Ivoire")
        
        with col2:
            phone = st.text_input("Téléphone", "+225 01 23 45 67 89")
            email = st.text_input("Email boutique", "contact@luxe-beaute.com")
            website = st.text_input("Site web", "www.luxe-beaute.com")
            tax_id = st.text_input("Numéro fiscal", "CI-12345678-X")
        
        logo = st.file_uploader("Logo de la boutique", type=['png', 'jpg', 'jpeg'])
        
        if st.button("💾 Mettre à jour les informations", use_container_width=True):
            st.success("Informations boutique mises à jour!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Paramètres de sécurité")
        
        # Changement de mot de passe
        st.write("**Changement de mot de passe**")
        current_password = st.text_input("Mot de passe actuel", type="password")
        new_password = st.text_input("Nouveau mot de passe", type="password")
        confirm_password = st.text_input("Confirmer le mot de passe", type="password")
        
        if st.button("🔐 Changer le mot de passe", use_container_width=True):
            if new_password == confirm_password:
                st.success("Mot de passe changé avec succès!")
            else:
                st.error("Les mots de passe ne correspondent pas")
        
        # Session
        st.write("")
        st.write("**Sessions**")
        st.checkbox("Forcer la déconnexion après inactivité", value=True)
        timeout = st.slider("Délai d'inactivité (minutes)", 5, 120, 30)
        
        # Sauvegarde
        st.write("")
        st.write("**Sauvegarde**")
        backup_frequency = st.selectbox("Fréquence de sauvegarde", 
                                       ["Quotidienne", "Hebdomadaire", "Mensuelle"])
        
        if st.button("💾 Sauvegarder maintenant", use_container_width=True):
            st.success("Sauvegarde effectuée!")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Main application
def main():
    """Application principale"""
    # Initialisation
    init_session_state()
    
    # Vérifier l'authentification
    if not st.session_state.user:
        if not login():
            return
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h1 style='color: white; margin-bottom: 0;'>💄</h1>
            <h3 style='color: white; margin-top: 0;'>Luxe Beauté</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Menu de navigation
        menu_options = {
            "📊 Dashboard": "Dashboard",
            "📦 Produits": "Produits", 
            "💰 Ventes": "Ventes",
            "👥 Clients": "Clients",
            "📦 Stock": "Stock",
            "💰 Comptabilité": "Comptabilité",
            "📅 Rendez-vous": "Rendez-vous",
            "⚙️ Paramètres": "Paramètres"
        }
        
        selected = st.selectbox(
            "Navigation",
            list(menu_options.keys()),
            index=list(menu_options.keys()).index(
                menu_options.get(st.session_state.page, "📊 Dashboard")
            )
        )
        
        st.session_state.page = menu_options[selected]
        
        st.markdown("---")
        
        # Informations utilisateur
        if st.session_state.user:
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;'>
                <p style='color: white; margin-bottom: 0.5rem;'>👤 <strong>{st.session_state.user.get('full_name', 'Utilisateur')}</strong></p>
                <p style='color: white; margin: 0; font-size: 0.8rem;'>🏷️ {st.session_state.user.get('role', 'Utilisateur')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Bouton de déconnexion
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
        
        st.markdown("---")
        
        # Informations système
        st.markdown("""
        <div style='color: rgba(255,255,255,0.7); font-size: 0.8rem;'>
            <p>📱 Version 2.0.0</p>
            <p>🕐 Dernière mise à jour: Aujourd'hui</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Contenu principal
    try:
        if st.session_state.page == "Dashboard":
            show_dashboard()
        elif st.session_state.page == "Produits":
            show_products()
        elif st.session_state.page == "Ventes":
            show_sales()
        elif st.session_state.page == "Clients":
            show_clients()
        elif st.session_state.page == "Stock":
            show_stock()
        elif st.session_state.page == "Comptabilité":
            show_accounting()
        elif st.session_state.page == "Rendez-vous":
            show_appointments()
        elif st.session_state.page == "Paramètres":
            show_settings()
    except Exception as e:
        st.error(f"Une erreur est survenue: {str(e)}")
        st.info("Veuillez rafraîchir la page ou vérifier la connexion au serveur.")

if __name__ == "__main__":
    main()