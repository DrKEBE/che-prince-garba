import streamlit as st

def configure_page():
    """Configure les paramètres de la page Streamlit"""
    st.set_page_config(
        page_title="Luxe Beauté Management",
        page_icon="💄",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/your-repo',
            'Report a bug': "https://github.com/your-repo/issues",
            'About': "# Luxe Beauté Management\nSystème de gestion premium pour instituts de beauté"
        }
    )

def set_custom_css():
    """Définit le CSS personnalisé"""
    custom_css = """
    <style>
    /* Styles généraux */
    .main {
        padding: 2rem;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Cartes */
    .card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #FF6B9D;
    }
    
    .card-success {
        border-left-color: #28a745;
    }
    
    .card-warning {
        border-left-color: #ffc107;
    }
    
    .card-danger {
        border-left-color: #dc3545;
    }
    
    .card-info {
        border-left-color: #17a2b8;
    }
    
    /* Boutons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    /* Tableaux */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Titres */
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 600;
    }
    
    h1 {
        border-bottom: 2px solid #FF6B9D;
        padding-bottom: 0.5rem;
    }
    
    /* Badges */
    .badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .badge-success {
        background-color: #d4edda;
        color: #155724;
    }
    
    .badge-warning {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .badge-danger {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    .badge-info {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    
    /* Animation de chargement */
    .loading {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    
    /* Scroll personnalisé */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #FF6B9D;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #e0558a;
    }
    
    /* Alertes personnalisées */
    .alert {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    
    .alert-success {
        background-color: #d4edda;
        border-left-color: #28a745;
        color: #155724;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border-left-color: #ffc107;
        color: #856404;
    }
    
    .alert-danger {
        background-color: #f8d7da;
        border-left-color: #dc3545;
        color: #721c24;
    }
    
    /* Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Icônes */
    .icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    
    .icon-small {
        font-size: 1rem;
    }
    
    /* Grille */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)