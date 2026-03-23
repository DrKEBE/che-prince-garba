"""
Widgets de filtres élégants pour l'application
"""
import streamlit as st
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import pandas as pd

from config.constants import COLORS, PAYMENT_METHODS, CLIENT_TYPES, PRODUCT_CATEGORIES
from utils.formatters import format_currency, format_date

class FilterWidgets:
    """Widgets de filtres stylisés"""
    
    @staticmethod
    def quick_filter_bar(
        filter_type: str = "products",
        on_filter: Optional[Callable] = None,
        on_clear: Optional[Callable] = None
    ):
        """Barre de filtres rapides élégante"""
        
        filter_html = f"""
        <style>
        .quick-filter-bar {{
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            border: 1px solid #E9ECEF;
        }}
        
        .filter-row {{
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        
        .filter-item {{
            flex: 1;
            min-width: 200px;
        }}
        
        .filter-actions {{
            display: flex;
            gap: 0.5rem;
            margin-left: auto;
        }}
        
        .filter-btn {{
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            font-size: 0.9rem;
        }}
        
        .btn-filter {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
            color: white;
        }}
        
        .btn-clear {{
            background: #F8F9FA;
            color: #5D6D7E;
            border: 1px solid #E9ECEF;
        }}
        
        .filter-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        .date-range {{
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }}
        
        .date-separator {{
            color: #7F8C8D;
            font-weight: bold;
        }}
        </style>
        
        <div class="quick-filter-bar">
            <div class="filter-row">
        """
        
        st.markdown(filter_html, unsafe_allow_html=True)
        
        # Définir les colonnes selon le type de filtre
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if filter_type == "products":
                category = st.selectbox(
                    "Catégorie",
                    options=["Toutes"] + PRODUCT_CATEGORIES,
                    key="filter_category"
                )
            elif filter_type == "sales":
                payment_method = st.selectbox(
                    "Méthode",
                    options=["Toutes"] + list(PAYMENT_METHODS.values()),
                    key="filter_payment"
                )
            elif filter_type == "clients":
                client_type = st.selectbox(
                    "Type",
                    options=["Tous"] + list(CLIENT_TYPES.values()),
                    key="filter_client_type"
                )
        
        with col2:
            if filter_type == "products":
                stock_status = st.selectbox(
                    "Stock",
                    options=["Tous", "En stock", "Faible stock", "Rupture"],
                    key="filter_stock"
                )
            elif filter_type == "sales":
                sale_status = st.selectbox(
                    "Statut",
                    options=["Tous", "Payé", "En attente", "Partiel", "Annulé"],
                    key="filter_status"
                )
        
        with col3:
            min_value = st.number_input("Min", value=0, key="filter_min")
        
        with col4:
            max_value = st.number_input("Max", value=1000000, key="filter_max")
        
        # Boutons d'action
        st.markdown('</div><div class="filter-actions">', unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns([1, 1])
        
        with col_btn1:
            if st.button("🗑️ Effacer", type="secondary", use_container_width=True):
                if on_clear:
                    on_clear()
                st.rerun()
        
        with col_btn2:
            if st.button("🔍 Appliquer", type="primary", use_container_width=True):
                filters = {}
                if filter_type == "products":
                    filters = {
                        'category': category if category != "Toutes" else None,
                        'stock_status': stock_status if stock_status != "Tous" else None,
                        'min_price': min_value,
                        'max_price': max_value
                    }
                elif filter_type == "sales":
                    filters = {
                        'payment_method': payment_method if payment_method != "Toutes" else None,
                        'status': sale_status if sale_status != "Tous" else None,
                        'min_amount': min_value,
                        'max_amount': max_value
                    }
                
                if on_filter:
                    on_filter(filters)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    @staticmethod
    def date_range_filter(
        default_range: str = "30d",
        on_change: Optional[Callable] = None
    ):
        """Filtre de plage de dates élégant"""
        
        filter_html = f"""
        <style>
        .date-range-filter {{
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            border-radius: 10px;
            padding: 1rem;
            border: 1px solid #E9ECEF;
            margin-bottom: 1rem;
        }}
        
        .date-range-title {{
            font-size: 0.9rem;
            color: #7F8C8D;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .date-range-buttons {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        
        .date-btn {{
            padding: 0.5rem 1rem;
            border-radius: 8px;
            background: white;
            border: 1px solid #E9ECEF;
            color: #5D6D7E;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.9rem;
            flex: 1;
            text-align: center;
        }}
        
        .date-btn:hover {{
            background: #f0f0f0;
            transform: translateY(-1px);
        }}
        
        .date-btn.active {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
            color: white;
            border-color: {COLORS['primary']};
            box-shadow: 0 2px 8px {COLORS['primary']}40;
        }}
        
        .custom-range {{
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #E9ECEF;
        }}
        
        .date-inputs {{
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 1rem;
            align-items: center;
        }}
        
        .date-separator {{
            text-align: center;
            color: #7F8C8D;
            font-weight: bold;
        }}
        </style>
        
        <div class="date-range-filter">
            <div class="date-range-title">📅 Période</div>
            <div class="date-range-buttons">
        """
        
        st.markdown(filter_html, unsafe_allow_html=True)
        
        # Boutons de plages prédéfinies
        col1, col2, col3, col4, col5 = st.columns(5)
        
        date_ranges = [
            ("Aujourd'hui", "1d"),
            ("Hier", "1d-1"),
            ("7 jours", "7d"),
            ("30 jours", "30d"),
            ("90 jours", "90d")
        ]
        
        for i, (label, value) in enumerate(date_ranges):
            with [col1, col2, col3, col4, col5][i]:
                if st.button(label, key=f"date_{value}", use_container_width=True):
                    if on_change:
                        on_change(value)
        
        # Plage personnalisée
        st.markdown('<div class="custom-range">', unsafe_allow_html=True)
        
        date_cols = st.columns([2, 1, 2])
        
        with date_cols[0]:
            start_date = st.date_input("Du", value=datetime.now() - timedelta(days=30))
        
        with date_cols[1]:
            st.markdown('<div class="date-separator">→</div>', unsafe_allow_html=True)
        
        with date_cols[2]:
            end_date = st.date_input("Au", value=datetime.now())
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        return start_date, end_date
    
    @staticmethod
    def search_filter(
        placeholder: str = "Rechercher...",
        on_search: Optional[Callable] = None,
        search_type: str = "text"
    ):
        """Champ de recherche élégant"""
        
        search_html = f"""
        <style>
        .search-filter {{
            position: relative;
            margin-bottom: 1rem;
        }}
        
        .search-input {{
            width: 100%;
            padding: 0.75rem 1rem 0.75rem 3rem;
            border: 2px solid #E9ECEF;
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: white;
            color: #2C3E50;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: {COLORS['primary']};
            box-shadow: 0 0 0 3px {COLORS['primary']}20;
        }}
        
        .search-icon {{
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: {COLORS['primary']};
            font-size: 1.2rem;
            z-index: 1;
        }}
        
        .search-actions {{
            position: absolute;
            right: 0.5rem;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            gap: 0.5rem;
        }}
        
        .search-btn {{
            background: {COLORS['primary']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: 500;
        }}
        
        .search-btn:hover {{
            background: {COLORS['secondary']};
            transform: translateY(-1px);
        }}
        
        .search-btn.clear {{
            background: transparent;
            color: #7F8C8D;
            padding: 0.5rem;
        }}
        </style>
        
        <div class="search-filter">
            <div class="search-icon">🔍</div>
            <input type="{search_type}" 
                   class="search-input" 
                   placeholder="{placeholder}" 
                   id="search-input"
                   onkeypress="if(event.keyCode == 13) document.getElementById('search-btn').click()">
            <div class="search-actions">
                <button class="search-btn clear" onclick="document.getElementById('search-input').value = ''; document.getElementById('clear-btn').click()">✕</button>
                <button class="search-btn" onclick="document.getElementById('search-btn').click()">Rechercher</button>
            </div>
        </div>
        """
        
        st.markdown(search_html, unsafe_allow_html=True)
        
        # Contrôles Streamlit
        search_col1, search_col2 = st.columns([4, 1])
        
        with search_col1:
            search_term = st.text_input(
                placeholder,
                label_visibility="collapsed",
                key="search_term"
            )
        
        with search_col2:
            search_btn = st.button("🔍", key="search_btn", use_container_width=True)
            clear_btn = st.button("✕", key="clear_btn", type="secondary", use_container_width=True)
        
        if search_btn and on_search and search_term:
            on_search(search_term)
        
        if clear_btn:
            if on_search:
                on_search("")
            st.rerun()
    
    @staticmethod
    def category_filter(
        categories: List[str],
        selected: List[str] = None,
        on_select: Optional[Callable] = None,
        multi_select: bool = True
    ):
        """Filtre de catégories sous forme de badges"""
        
        if selected is None:
            selected = []
        
        filter_html = f"""
        <style>
        .category-filter {{
            margin-bottom: 1.5rem;
        }}
        
        .category-title {{
            font-size: 0.9rem;
            color: #7F8C8D;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .category-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        
        .category-badge {{
            padding: 0.5rem 1rem;
            border-radius: 20px;
            background: #F8F9FA;
            color: #5D6D7E;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid #E9ECEF;
            font-size: 0.9rem;
        }}
        
        .category-badge:hover {{
            background: #E9ECEF;
            transform: translateY(-1px);
        }}
        
        .category-badge.selected {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
            color: white;
            border-color: {COLORS['primary']};
            box-shadow: 0 2px 8px {COLORS['primary']}40;
        }}
        
        .category-badge.selected:hover {{
            background: linear-gradient(135deg, {COLORS['secondary']} 0%, {COLORS['primary']} 100%);
        }}
        
        .category-all {{
            background: #2C3E50 !important;
            color: white !important;
            border-color: #2C3E50 !important;
        }}
        </style>
        
        <div class="category-filter">
            <div class="category-title">📁 Catégories</div>
            <div class="category-badges">
        """
        
        st.markdown(filter_html, unsafe_allow_html=True)
        
        # Bouton "Toutes"
        if st.button("Toutes", key="cat_all", type="primary" if not selected else "secondary"):
            if on_select:
                on_select([])
        
        # Badges de catégories
        for i, category in enumerate(categories):
            is_selected = category in selected
            
            if st.button(
                category,
                key=f"cat_{i}",
                type="primary" if is_selected else "secondary"
            ):
                new_selection = []
                if multi_select:
                    if is_selected:
                        new_selection = [c for c in selected if c != category]
                    else:
                        new_selection = selected + [category]
                else:
                    new_selection = [category] if not is_selected else []
                
                if on_select:
                    on_select(new_selection)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    @staticmethod
    def status_filter(
        status_options: Dict[str, str],
        selected: List[str] = None,
        on_select: Optional[Callable] = None
    ):
        """Filtre de statut avec indicateurs visuels"""
        
        if selected is None:
            selected = []
        
        filter_html = """
        <style>
        .status-filter {
            margin-bottom: 1.5rem;
        }
        
        .status-title {
            font-size: 0.9rem;
            color: #7F8C8D;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 0.5rem;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem;
            border-radius: 10px;
            background: #F8F9FA;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid #E9ECEF;
        }
        
        .status-item:hover {
            background: #E9ECEF;
            transform: translateY(-1px);
        }
        
        .status-item.selected {
            border-color: #E9ECEF;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        
        .status-label {
            font-size: 0.9rem;
            color: #2C3E50;
            flex-grow: 1;
        }
        
        .status-count {
            background: white;
            padding: 0.25rem 0.5rem;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        </style>
        
        <div class="status-filter">
            <div class="status-title">📊 Statuts</div>
            <div class="status-grid">
        """
        
        st.markdown(filter_html, unsafe_allow_html=True)
        
        # Options de statut
        cols = st.columns(len(status_options))
        
        for idx, (status_key, status_label) in enumerate(status_options.items()):
            with cols[idx]:
                is_selected = status_key in selected
                
                # Déterminer la couleur
                color_map = {
                    "success": "#28A745",
                    "warning": "#FFC107",
                    "danger": "#DC3545",
                    "info": "#17A2B8",
                    "primary": COLORS['primary']
                }
                
                status_color = color_map.get(status_key.lower(), COLORS['primary'])
                
                if st.button(
                    f"{status_label}",
                    key=f"status_{status_key}",
                    type="primary" if is_selected else "secondary"
                ):
                    new_selection = []
                    if is_selected:
                        new_selection = [s for s in selected if s != status_key]
                    else:
                        new_selection = selected + [status_key]
                    
                    if on_select:
                        on_select(new_selection)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    @staticmethod
    def price_range_filter(
        min_value: float = 0,
        max_value: float = 1000000,
        current_min: float = None,
        current_max: float = None,
        on_change: Optional[Callable] = None
    ):
        """Filtre de plage de prix avec curseur"""
        
        if current_min is None:
            current_min = min_value
        if current_max is None:
            current_max = max_value
        
        filter_html = f"""
        <style>
        .price-filter {{
            margin-bottom: 1.5rem;
        }}
        
        .price-title {{
            font-size: 0.9rem;
            color: #7F8C8D;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .price-slider-container {{
            position: relative;
            height: 40px;
        }}
        
        .price-track {{
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 6px;
            background: #E9ECEF;
            border-radius: 3px;
            transform: translateY(-50%);
        }}
        
        .price-fill {{
            position: absolute;
            top: 50%;
            height: 6px;
            background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
            border-radius: 3px;
            transform: translateY(-50%);
        }}
        
        .price-handle {{
            position: absolute;
            top: 50%;
            width: 20px;
            height: 20px;
            background: white;
            border: 2px solid {COLORS['primary']};
            border-radius: 50%;
            cursor: pointer;
            transform: translate(-50%, -50%);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
        }}
        
        .price-handle:hover {{
            transform: translate(-50%, -50%) scale(1.2);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        
        .price-values {{
            display: flex;
            justify-content: space-between;
            margin-top: 1rem;
            font-size: 0.9rem;
            color: #5D6D7E;
        }}
        
        .price-input {{
            background: #F8F9FA;
            border: 1px solid #E9ECEF;
            border-radius: 6px;
            padding: 0.5rem;
            width: 100px;
            text-align: center;
            font-weight: 500;
        }}
        </style>
        
        <div class="price-filter">
            <div class="price-title">💰 Plage de prix</div>
            <div class="price-slider-container">
                <div class="price-track"></div>
                <div class="price-fill" id="price-fill"></div>
                <div class="price-handle" id="price-handle-min"></div>
                <div class="price-handle" id="price-handle-max"></div>
            </div>
            <div class="price-values">
                <input type="number" class="price-input" id="price-min" value="{current_min}">
                <span>à</span>
                <input type="number" class="price-input" id="price-max" value="{current_max}">
            </div>
        </div>
        
        <script>
        function updatePriceFilter() {{
            const minValue = parseFloat(document.getElementById('price-min').value);
            const maxValue = parseFloat(document.getElementById('price-max').value);
            const minHandle = document.getElementById('price-handle-min');
            const maxHandle = document.getElementById('price-handle-max');
            const fill = document.getElementById('price-fill');
            
            const containerWidth = document.querySelector('.price-slider-container').offsetWidth;
            const minPercent = ((minValue - {min_value}) / ({max_value} - {min_value})) * 100;
            const maxPercent = ((maxValue - {min_value}) / ({max_value} - {min_value})) * 100;
            
            minHandle.style.left = minPercent + '%';
            maxHandle.style.left = maxPercent + '%';
            fill.style.left = minPercent + '%';
            fill.style.right = (100 - maxPercent) + '%';
        }}
        
        document.getElementById('price-min').addEventListener('input', updatePriceFilter);
        document.getElementById('price-max').addEventListener('input', updatePriceFilter);
        updatePriceFilter();
        </script>
        """
        
        st.markdown(filter_html, unsafe_allow_html=True)
        
        # Slider Streamlit
        price_range = st.slider(
            "Plage de prix",
            min_value=float(min_value),
            max_value=float(max_value),
            value=(float(current_min), float(current_max)),
            format="%.2f FCFA",
            label_visibility="collapsed"
        )
        
        if on_change and price_range:
            on_change({"min": price_range[0], "max": price_range[1]})
    
    @staticmethod
    def sort_filter(
        sort_options: Dict[str, str],
        current_sort: str = None,
        on_sort: Optional[Callable] = None
    ):
        """Filtre de tri avec sélecteur élégant"""
        
        filter_html = f"""
        <style>
        .sort-filter {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        .sort-label {{
            font-size: 0.9rem;
            color: #7F8C8D;
        }}
        
        .sort-select {{
            padding: 0.5rem 1rem;
            border: 1px solid #E9ECEF;
            border-radius: 8px;
            background: white;
            color: #2C3E50;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .sort-select:hover {{
            border-color: {COLORS['primary']};
        }}
        
        .sort-select:focus {{
            outline: none;
            border-color: {COLORS['primary']};
            box-shadow: 0 0 0 3px {COLORS['primary']}20;
        }}
        
        .sort-direction {{
            padding: 0.5rem;
            border-radius: 8px;
            background: #F8F9FA;
            border: 1px solid #E9ECEF;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .sort-direction:hover {{
            background: #E9ECEF;
        }}
        
        .sort-direction.active {{
            background: {COLORS['primary']};
            color: white;
            border-color: {COLORS['primary']};
        }}
        </style>
        
        <div class="sort-filter">
            <div class="sort-label">Trier par:</div>
            <select class="sort-select" id="sort-select">
        """
        
        st.markdown(filter_html, unsafe_allow_html=True)
        
        # Sélecteur de tri
        sort_key = st.selectbox(
            "Trier par",
            options=list(sort_options.keys()),
            format_func=lambda x: sort_options[x],
            label_visibility="collapsed"
        )
        
        st.markdown('</select>', unsafe_allow_html=True)
        
        # Direction du tri
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬆️", help="Ascendant", key="sort_asc"):
                if on_sort:
                    on_sort(sort_key, "asc")
        with col2:
            if st.button("⬇️", help="Descendant", key="sort_desc"):
                if on_sort:
                    on_sort(sort_key, "desc")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Instance globale
filters = FilterWidgets()