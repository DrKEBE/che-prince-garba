import streamlit as st
from config.constants import COLORS
from config.theme import ThemeManager

def show_sidebar():
    """Affiche la sidebar avec navigation - VERSION CORRIGÉE"""
    
    # Appliquer le thème
    ThemeManager.apply_theme()
    
    # CSS personnalisé pour la sidebar
    sidebar_css = """
    <style>
    /* Style de la sidebar principale */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, 
            #2C3E50 0%, 
            #34495E 50%, 
            #2C3E50 100%
        );
        padding: 1.5rem 1rem;
        min-width: 280px !important;
        max-width: 280px !important;
    }
    
    /* Logo de la sidebar */
    .sidebar-logo {
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar-logo-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .sidebar-logo-text {
        color: white;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
    }
    
    .sidebar-logo-subtext {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.75rem;
        margin-top: 0.25rem;
    }
    
    /* Navigation */
    .sidebar-nav {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .nav-section {
        margin-bottom: 1rem;
    }
    
    .section-title {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.75rem;
        padding-left: 1rem;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        color: rgba(255, 255, 255, 0.8);
        text-decoration: none;
        border-radius: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
        border: none;
        background: transparent;
        width: 100%;
        text-align: left;
        font-size: 0.9375rem;
    }
    
    .nav-item:hover {
        background: rgba(255, 107, 157, 0.1);
        color: white;
        transform: translateX(5px);
    }
    
    .nav-item.active {
        background: linear-gradient(90deg, 
            rgba(255, 107, 157, 0.2) 0%, 
            rgba(255, 107, 157, 0.1) 100%
        );
        color: white;
        border-left: 3px solid #FF6B9D;
        box-shadow: 0 4px 12px rgba(255, 107, 157, 0.2);
    }
    
    .nav-icon {
        font-size: 1.25rem;
        width: 24px;
        text-align: center;
    }
    
    .nav-text {
        flex-grow: 1;
    }
    
    .nav-badge {
        background: #FF6B9D;
        color: white;
        font-size: 0.75rem;
        padding: 0.125rem 0.5rem;
        border-radius: 10px;
        font-weight: 500;
    }
    
    /* Bouton de déconnexion */
    .logout-btn {
        margin-top: auto;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Footer de la sidebar */
    .sidebar-footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    
    .version-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.75rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        margin-bottom: 1rem;
    }
    
    .app-status {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
        color: rgba(255, 255, 255, 0.7);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #2ECC71;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    </style>
    """
    
    st.markdown(sidebar_css, unsafe_allow_html=True)
    
    # Initialiser la page courante si elle n'existe pas
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    with st.sidebar:
        # Logo
        st.markdown("""
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">💄</div>
            <div class="sidebar-logo-text">Luxe Beauté</div>
            <div class="sidebar-logo-subtext">Management System</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation avec des boutons Streamlit natifs
        st.markdown('<div class="section-title">PRINCIPAL</div>', unsafe_allow_html=True)
        if st.button("📊 Dashboard", key="btn_dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        st.markdown('<div class="section-title">VENTES</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button("💰 Ventes", key="btn_ventes", use_container_width=True):
                st.session_state.current_page = "ventes"
                st.rerun()
        with col2:
            st.markdown('<span class="nav-badge">5</span>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button("👥 Clients", key="btn_clients", use_container_width=True):
                st.session_state.current_page = "clients"
                st.rerun()
        with col2:
            st.markdown('<span class="nav-badge">12</span>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button("📅 Rendez-vous", key="btn_rendez_vous", use_container_width=True):
                st.session_state.current_page = "rendez_vous"
                st.rerun()
        with col2:
            st.markdown('<span class="nav-badge">8</span>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">STOCK</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button("💄 Produits", key="btn_produits", use_container_width=True):
                st.session_state.current_page = "produits"
                st.rerun()
        with col2:
            st.markdown('<span class="nav-badge">24</span>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button("📦 Stock", key="btn_stock", use_container_width=True):
                st.session_state.current_page = "stock"
                st.rerun()
        with col2:
            st.markdown('<span class="nav-badge">3</span>', unsafe_allow_html=True)
        
        if st.button("🏢 Fournisseurs", key="btn_fournisseurs", use_container_width=True):
            st.session_state.current_page = "fournisseurs"
            st.rerun()
        
        st.markdown('<div class="section-title">FINANCES</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button("💵 Comptabilité", key="btn_comptabilite", use_container_width=True):
                st.session_state.current_page = "comptabilite"
                st.rerun()
        with col2:
            st.markdown('<span class="nav-badge">2</span>', unsafe_allow_html=True)
        
        if st.button("📈 Rapports", key="btn_rapports", use_container_width=True):
            st.session_state.current_page = "rapports"
            st.rerun()
        
        st.markdown('<div class="section-title">ADMINISTRATION</div>', unsafe_allow_html=True)
        if st.button("⚙️ Paramètres", key="btn_parametres", use_container_width=True):
            st.session_state.current_page = "parametres"
            st.rerun()
        
        if st.button("🚪 Déconnexion", key="btn_logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div class="sidebar-footer">
            <div class="version-badge">v2.0.0</div>
            <div class="app-status">
                <span class="status-dot"></span>
                <span>Système opérationnel</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Retourner la page sélectionnée
    return st.session_state.get('current_page', 'dashboard')