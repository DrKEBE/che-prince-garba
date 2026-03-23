"""
Page de gestion des produits
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any

from services.api_client import APIClient
from utils.formatters import format_currency, format_stock_status
from widgets.cards import create_product_card
from widgets.tables import create_products_table
from widgets.filters import ProductFilters
from utils.validators import Validators, display_validation_errors

def produits_page():
    """Page de gestion des produits"""
    
    st.title("💄 Gestion des Produits")
    
    # Initialisation
    api_client = APIClient()
    
    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Liste des produits", 
        "➕ Nouveau produit", 
        "📊 Statistiques",
        "⚙️ Catégories"
    ])
    
    # Onglet 1: Liste des produits
    with tab1:
        st.markdown("### 📦 Catalogue des produits")
        
        # Filtres
        with st.expander("🔍 Filtres avancés", expanded=False):
            filters = ProductFilters.render_filters()
        
        # Recherche rapide
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            search_term = st.text_input(
                "Rechercher un produit",
                placeholder="Nom, SKU, code-barres...",
                key="product_search"
            )
        
        with col2:
            low_stock = st.checkbox("Stock faible seulement", key="low_stock_filter")
        
        with col3:
            view_mode = st.selectbox(
                "Affichage",
                ["Tableau", "Cartes"],
                key="product_view_mode"
            )
        
        # Récupérer les produits
        with st.spinner("Chargement des produits..."):
            products = api_client.get_products(
                search=search_term if search_term else None,
                low_stock=low_stock,
                force_refresh=True
            )
        
        # Affichage
        if view_mode == "Tableau":
            create_products_table(
                products,
                page_size=15,
                show_search=False,
                selectable=True,
                key="products_table"
            )
        else:
            # Affichage en cartes
            if not products:
                st.info("Aucun produit trouvé")
            else:
                cols = st.columns(3)
                for i, product in enumerate(products):
                    with cols[i % 3]:
                        st.markdown(
                            create_product_card(product, show_actions=True),
                            unsafe_allow_html=True
                        )
        
        # Actions rapides
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📥 Exporter CSV", use_container_width=True):
                if products:
                    df = pd.DataFrame(products)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Télécharger",
                        csv,
                        "produits.csv",
                        "text/csv"
                    )
        
        with col2:
            if st.button("🖨️ Imprimer étiquettes", use_container_width=True):
                st.info("Fonctionnalité d'impression à venir")
        
        with col3:
            if st.button("📧 Envoyer alertes", use_container_width=True):
                low_stock_products = [p for p in products if p.get('current_stock', 0) <= p.get('alert_threshold', 10)]
                if low_stock_products:
                    st.warning(f"{len(low_stock_products)} produits en stock faible")
                else:
                    st.success("Aucune alerte stock nécessaire")
        
        with col4:
            if st.button("🔄 Actualiser", use_container_width=True):
                st.rerun()
    
    # Onglet 2: Nouveau produit
    with tab2:
        st.markdown("### ➕ Ajouter un nouveau produit")
        
        with st.form("new_product_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nom du produit *", placeholder="Ex: Crème hydratante")
                category = st.selectbox(
                    "Catégorie *",
                    ["Soins Visage", "Soins Corps", "Maquillage", "Parfums", "Accessoires", "Homme", "Femme", "Enfant", "Professionnel"]
                )
                brand = st.text_input("Marque", placeholder="Ex: Lancôme")
                sku = st.text_input("SKU", placeholder="Code unique")
                barcode = st.text_input("Code-barres", placeholder="EAN-13")
            
            with col2:
                purchase_price = st.number_input(
                    "Prix d'achat (FCFA) *",
                    min_value=0.0,
                    value=0.0,
                    step=100.0
                )
                selling_price = st.number_input(
                    "Prix de vente (FCFA) *",
                    min_value=0.0,
                    value=0.0,
                    step=100.0
                )
                alert_threshold = st.number_input(
                    "Seuil d'alerte stock *",
                    min_value=0,
                    value=10,
                    step=1
                )
                initial_stock = st.number_input(
                    "Stock initial",
                    min_value=0,
                    value=0,
                    step=1
                )
            
            # Description et images
            description = st.text_area(
                "Description",
                placeholder="Description détaillée du produit...",
                height=100
            )
            
            # Images
            uploaded_images = st.file_uploader(
                "Images du produit",
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True,
                help="Téléchargez jusqu'à 5 images"
            )
            
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
                product_data = {
                    "name": name,
                    "category": category,
                    "brand": brand,
                    "sku": sku,
                    "barcode": barcode,
                    "purchase_price": purchase_price,
                    "selling_price": selling_price,
                    "alert_threshold": alert_threshold,
                    "initial_stock": initial_stock,
                    "description": description
                }
                
                valid, errors = Validators.validate_product_data(product_data)
                
                if valid:
                    try:
                        # Appel API
                        result = api_client.create_product(product_data)
                        if result:
                            st.success("✅ Produit créé avec succès !")
                            st.balloons()
                    except Exception as e:
                        st.error(f"❌ Erreur : {str(e)}")
                else:
                    display_validation_errors(errors)
    
    # Onglet 3: Statistiques
    with tab3:
        st.markdown("### 📊 Statistiques produits")
        
        if not products:
            st.info("Aucun produit à analyser")
        else:
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_products = len(products)
                st.metric("Total produits", total_products)
            
            with col2:
                low_stock_count = len([p for p in products if p.get('current_stock', 0) <= p.get('alert_threshold', 10)])
                st.metric("Stock faible", low_stock_count, delta=f"-{total_products - low_stock_count}")
            
            with col3:
                out_of_stock_count = len([p for p in products if p.get('current_stock', 0) <= 0])
                st.metric("Rupture", out_of_stock_count)
            
            with col4:
                avg_margin = sum(p.get('margin', 0) for p in products) / total_products if total_products > 0 else 0
                st.metric("Marge moyenne", f"{avg_margin:.1f}%")
            
            # Graphiques
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📈 Répartition par catégorie")
                
                # Calculer les statistiques par catégorie
                categories = {}
                for product in products:
                    cat = product.get('category', 'Non catégorisé')
                    if cat not in categories:
                        categories[cat] = {
                            'count': 0,
                            'stock': 0,
                            'value': 0
                        }
                    categories[cat]['count'] += 1
                    categories[cat]['stock'] += product.get('current_stock', 0)
                    categories[cat]['value'] += product.get('selling_price', 0) * product.get('current_stock', 0)
                
                # Créer un DataFrame
                df_categories = pd.DataFrame([
                    {
                        'Catégorie': cat,
                        'Nombre': data['count'],
                        'Stock': data['stock'],
                        'Valeur (FCFA)': data['value']
                    }
                    for cat, data in categories.items()
                ])
                
                if not df_categories.empty:
                    st.dataframe(
                        df_categories.sort_values('Valeur (FCFA)', ascending=False),
                        use_container_width=True
                    )
            
            with col2:
                st.markdown("#### 🚨 Top 5 - Stock faible")
                
                # Produits avec stock faible
                low_stock_products = sorted(
                    [p for p in products if p.get('current_stock', 0) <= p.get('alert_threshold', 10)],
                    key=lambda x: x.get('current_stock', 0)
                )[:5]
                
                if low_stock_products:
                    for product in low_stock_products:
                        with st.container():
                            col_a, col_b, col_c = st.columns([3, 1, 1])
                            with col_a:
                                st.markdown(f"**{product['name']}**")
                                st.caption(f"Catégorie: {product.get('category', 'N/A')}")
                            with col_b:
                                st.metric("Stock", product.get('current_stock', 0))
                            with col_c:
                                st.metric("Seuil", product.get('alert_threshold', 10))
                            st.divider()
                else:
                    st.success("✅ Aucun produit en stock faible")
            
            # Tableau de bord avancé
            st.markdown("#### 📋 Vue d'ensemble")
            
            # Créer un DataFrame pour l'analyse
            analysis_data = []
            for product in products:
                stock = product.get('current_stock', 0)
                threshold = product.get('alert_threshold', 10)
                status = "🟢 Normal"
                if stock <= 0:
                    status = "🔴 Rupture"
                elif stock <= threshold:
                    status = "🟡 Faible"
                
                analysis_data.append({
                    'ID': product.get('id', '')[:8],
                    'Nom': product.get('name', ''),
                    'Catégorie': product.get('category', ''),
                    'Prix': format_currency(product.get('selling_price', 0)),
                    'Stock': stock,
                    'Seuil': threshold,
                    'Statut': status,
                    'Marge': f"{product.get('margin', 0):.1f}%"
                })
            
            df_analysis = pd.DataFrame(analysis_data)
            st.dataframe(
                df_analysis,
                use_container_width=True,
                hide_index=True
            )
    
    # Onglet 4: Catégories
    with tab4:
        st.markdown("### ⚙️ Gestion des catégories")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📂 Catégories existantes")
            
            # Récupérer les catégories des produits
            categories = set(p.get('category') for p in products if p.get('category'))
            
            if categories:
                for category in sorted(categories):
                    category_products = [p for p in products if p.get('category') == category]
                    category_value = sum(p.get('selling_price', 0) * p.get('current_stock', 0) for p in category_products)
                    
                    with st.expander(f"{category} ({len(category_products)} produits)"):
                        st.metric("Valeur totale", format_currency(category_value))
                        st.metric("Stock total", sum(p.get('current_stock', 0) for p in category_products))
            else:
                st.info("Aucune catégorie définie")
        
        with col2:
            st.markdown("#### ➕ Nouvelle catégorie")
            
            with st.form("new_category_form"):
                new_category = st.text_input("Nom de la catégorie")
                category_description = st.text_area("Description")
                
                if st.form_submit_button("Créer", type="primary"):
                    if new_category:
                        st.success(f"Catégorie '{new_category}' créée")
                    else:
                        st.error("Veuillez saisir un nom")

def edit_product_page(product_id: str):
    """Page d'édition d'un produit"""
    st.title("✏️ Modifier le produit")
    
    api_client = APIClient()
    
    # Récupérer le produit
    product = api_client.get_product(product_id)
    if not product:
        st.error("Produit non trouvé")
        return
    
    # Formulaire d'édition
    with st.form("edit_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nom *", value=product.get('name', ''))
            category = st.text_input("Catégorie *", value=product.get('category', ''))
            brand = st.text_input("Marque", value=product.get('brand', ''))
            sku = st.text_input("SKU", value=product.get('sku', ''))
        
        with col2:
            purchase_price = st.number_input(
                "Prix d'achat *",
                min_value=0.0,
                value=float(product.get('purchase_price', 0))
            )
            selling_price = st.number_input(
                "Prix de vente *",
                min_value=0.0,
                value=float(product.get('selling_price', 0))
            )
            alert_threshold = st.number_input(
                "Seuil d'alerte *",
                min_value=0,
                value=product.get('alert_threshold', 10)
            )
        
        description = st.text_area(
            "Description",
            value=product.get('description', ''),
            height=100
        )
        
        is_active = st.checkbox("Produit actif", value=product.get('is_active', True))
        
        col_a, col_b = st.columns([1, 3])
        with col_a:
            submit = st.form_submit_button("💾 Sauvegarder", type="primary")
        
        if submit:
            # Validation
            product_data = {
                "name": name,
                "category": category,
                "brand": brand,
                "sku": sku,
                "purchase_price": purchase_price,
                "selling_price": selling_price,
                "alert_threshold": alert_threshold,
                "description": description,
                "is_active": is_active
            }
            
            valid, errors = Validators.validate_product_data(product_data)
            
            if valid:
                try:
                    # Mise à jour
                    result = api_client.update_product(product_id, product_data)
                    if result:
                        st.success("✅ Produit mis à jour avec succès !")
                        st.balloons()
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)}")
            else:
                display_validation_errors(errors)

if __name__ == "__main__":
    produits_page()