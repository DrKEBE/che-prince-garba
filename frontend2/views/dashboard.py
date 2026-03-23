"""
Dashboard principal avec métriques et visualisations
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import List, Dict, Any

from services.api_client import APIClient
from services.analytics_service import AnalyticsService
from widgets.cards import create_stat_card
from widgets.charts import ChartManager
from utils.formatters import format_currency, format_percentage, format_date
from config.theme import ThemeManager
from utils.session_state import get_session_state

def dashboard_page():
    """Page principale du dashboard"""
    
    st.title("📊 Tableau de Bord")
    
    # Initialisation
    api_client = APIClient()
    analytics = AnalyticsService()
    ThemeManager.apply_theme()
    
    # Métriques principales en haut
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_stat_card(
            title="CA du Jour",
            value=format_currency(1250000),
            change="+12.5%",
            icon="💰",
            color="success",
            trend="up"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_stat_card(
            title="Nouveaux Clients",
            value="24",
            change="+3",
            icon="👥",
            color="primary",
            trend="up"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_stat_card(
            title="Ventes en Attente",
            value="8",
            change="-2",
            icon="⏳",
            color="warning",
            trend="down"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_stat_card(
            title="Stock Faible",
            value="12",
            change="+4",
            icon="📦",
            color="danger",
            trend="up"
        ), unsafe_allow_html=True)
    
    # Graphiques principaux
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Performance des Ventes")
        
        # Données de vente (simulées - à remplacer par API)
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        sales_data = pd.DataFrame({
            'date': dates,
            'ventes': [100000 + i*50000 + (i%7)*20000 for i in range(len(dates))],
            'objectif': [120000] * len(dates)
        })
        
        # Créer le graphique
        fig = ChartManager.create_sales_chart(sales_data, 'date', 'ventes', "Tendances des Ventes")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Distribution des Ventes")
        
        # Données par catégorie
        categories = ['Soins Visage', 'Maquillage', 'Parfums', 'Accessoires']
        values = [45, 25, 20, 10]
        
        fig = go.Figure(data=[go.Pie(
            labels=categories,
            values=values,
            hole=.4,
            marker=dict(
                colors=['#FF6B9D', '#9B59B6', '#3498DB', '#2ECC71'],
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textposition='inside'
        )])
        
        fig.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Section produits populaires
    st.markdown("---")
    st.markdown("### 🏆 Produits les Plus Vendus")
    
    # Récupérer les top produits
    top_products = api_client.get_top_products(limit=5, days=30)
    
    if top_products:
        cols = st.columns(5)
        for idx, product in enumerate(top_products[:5]):
            with cols[idx]:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; border-radius: 10px; background: linear-gradient(135deg, #FFE4E9 0%, #FFD1DC 100%);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">💄</div>
                    <div style="font-weight: 600; color: #2C3E50; margin-bottom: 0.25rem;">{product.get('name', 'Produit')}</div>
                    <div style="color: #FF6B9D; font-weight: 700;">{format_currency(product.get('total_revenue', 0))}</div>
                    <div style="font-size: 0.875rem; color: #7F8C8D;">{product.get('total_sold', 0)} vendus</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Chargement des produits populaires...")
    
    # Alertes et notifications
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚡ Alertes Stock")
        
        alertes = [
            {"produit": "Crème Hydratante", "stock": 3, "seuil": 10},
            {"produit": "Rouge à Lèvres", "stock": 5, "seuil": 15},
            {"produit": "Parfum Chanel", "stock": 2, "seuil": 5},
            {"produit": "Masque Visage", "stock": 0, "seuil": 8},
        ]
        
        for alerte in alertes:
            with st.container():
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    st.markdown(f"**{alerte['produit']}**")
                with col_b:
                    st.metric("Stock", alerte['stock'])
                with col_c:
                    if alerte['stock'] <= 0:
                        st.error("RUPTURE")
                    elif alerte['stock'] <= alerte['seuil']:
                        st.warning("FAIBLE")
                st.divider()
    
    with col2:
        st.markdown("### 📅 Prochains Rendez-vous")
        
        rdvs = [
            {"client": "Sophie Martin", "heure": "10:30", "service": "Soin Visage"},
            {"client": "Marie Dubois", "heure": "14:00", "service": "Maquillage"},
            {"client": "Julie Bernard", "heure": "15:30", "service": "Épil"},
            {"client": "Claire Petit", "heure": "17:00", "service": "Manucure"},
        ]
        
        for rdv in rdvs:
            with st.container():
                st.markdown(f"""
                <div style="padding: 0.75rem; background: #F8F9FA; border-radius: 8px; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <div style="font-weight: 600; color: #2C3E50;">{rdv['client']}</div>
                            <div style="font-size: 0.875rem; color: #7F8C8D;">{rdv['service']}</div>
                        </div>
                        <div style="
                            background: #FF6B9D;
                            color: white;
                            padding: 0.25rem 0.75rem;
                            border-radius: 20px;
                            font-weight: 500;
                        ">{rdv['heure']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Statistiques avancées
    st.markdown("---")
    st.markdown("### 📊 Statistiques Détaillées")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎯 Performance Mensuelle")
        
        monthly_data = pd.DataFrame({
            'Mois': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'],
            'CA': [1200000, 1500000, 1800000, 1600000, 2000000, 2200000],
            'Objectif': [1300000, 1400000, 1700000, 1600000, 1900000, 2100000]
        })
        
        fig = ChartManager.create_comparison_chart(
            monthly_data['CA'].tolist(),
            monthly_data['Objectif'].tolist(),
            monthly_data['Mois'].tolist(),
            ""
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 👥 Analyse Clients")
        
        client_types = {
            'Nouveaux': 15,
            'Réguliers': 45,
            'VIP': 25,
            'Inactifs': 15
        }
        
        fig = go.Figure(data=[go.Bar(
            x=list(client_types.keys()),
            y=list(client_types.values()),
            marker_color=['#FF6B9D', '#9B59B6', '#FFC107', '#6C757D']
        )])
        
        fig.update_layout(
            height=300,
            margin=dict(t=30, b=30, l=30, r=30)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("#### ⏰ Heures d'Affluence")
        
        hours = list(range(9, 20))
        traffic = [10, 15, 25, 40, 60, 85, 90, 75, 50, 35, 20]
        
        fig = go.Figure(data=[go.Scatter(
            x=hours,
            y=traffic,
            mode='lines+markers',
            line=dict(color='#FF6B9D', width=3),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 157, 0.2)'
        )])
        
        fig.update_layout(
            xaxis_title="Heure",
            yaxis_title="Affluence",
            height=300,
            margin=dict(t=30, b=30, l=30, r=30)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Section actualités
    st.markdown("---")
    st.markdown("### 📰 Actualités & Conseils")
    
    news = [
        {
            "title": "Nouvelle Collection Printemps",
            "content": "Découvrez notre nouvelle collection de maquillage printanière",
            "date": "15/03/2024",
            "color": "#FF6B9D"
        },
        {
            "title": "Promotion Spéciale",
            "content": "-30% sur tous les soins visage ce week-end",
            "date": "10/03/2024",
            "color": "#9B59B6"
        },
        {
            "title": "Atelier Beauté",
            "content": "Apprenez les techniques de maquillage avec nos experts",
            "date": "05/03/2024",
            "color": "#3498DB"
        }
    ]
    
    cols = st.columns(3)
    for idx, item in enumerate(news):
        with cols[idx]:
            st.markdown(f"""
            <div style="
                padding: 1.5rem;
                border-radius: 12px;
                background: linear-gradient(135deg, {item['color']} 0%, {item['color']}99 100%);
                color: white;
                height: 200px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            ">
                <div>
                    <div style="font-size: 0.875rem; opacity: 0.9;">{item['date']}</div>
                    <div style="font-size: 1.25rem; font-weight: 600; margin: 0.5rem 0;">{item['title']}</div>
                    <div style="font-size: 0.9375rem; opacity: 0.9;">{item['content']}</div>
                </div>
                <div style="text-align: right;">
                    <button style="
                        background: white;
                        color: {item['color']};
                        border: none;
                        padding: 0.5rem 1rem;
                        border-radius: 20px;
                        font-weight: 500;
                        cursor: pointer;
                    ">Voir plus →</button>
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard_page()