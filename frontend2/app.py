import os
import streamlit as st
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Mode développement
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

if DEV_MODE:
    st.session_state["authenticated"] = True
    st.session_state["user"] = {
        "username": "dev_admin",
        "role": "admin"
    }

# Initialiser l'état utilisateur
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "full_name": "Admin Démo",
        "role": "Administrateur"
    }

# Import des modules personnalisés
try:
    from config.components import configure_page, set_custom_css
    from components.header import show_header
    from components.sidebar import show_sidebar
    from services.auth_service import AuthService
    from services.api_client import APIClient
except ImportError as e:
    st.error(f"Erreur d'importation : {e}")
    st.info("Veuillez vérifier que tous les modules sont installés")

def main():
    """Application principale - VERSION CORRIGÉE"""
    
    # Configuration initiale de la page (DOIT ÊTRE EN PREMIER)
    st.set_page_config(
        page_title="Luxe Beauté Management",
        page_icon="💄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Appliquer le CSS personnalisé
    try:
        configure_page()
        set_custom_css()
    except:
        # CSS de secours
        st.markdown("""
        <style>
        .main { padding: 2rem; }
        .stButton > button { background-color: #FF6B9D; color: white; }
        </style>
        """, unsafe_allow_html=True)
    
    # Vérifier l'authentification
    if not st.session_state.get('authenticated', False):
        try:
            from views.auth import login_page
            login_page()
        except ImportError:
            # Page d'authentification de secours
            st.title("🔐 Connexion")
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter"):
                st.session_state.authenticated = True
                st.session_state.user = {"username": username, "role": "admin"}
                st.rerun()
        return
    
    # Initialiser la page courante
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Afficher le header
    try:
        show_header()
    except:
        # Header de secours
        st.markdown("""
        <h1 style="color: #2C3E50; border-bottom: 2px solid #FF6B9D; padding-bottom: 10px;">
            💄 Luxe Beauté Management
        </h1>
        <p style="color: #7F8C8D;">Système de gestion premium</p>
        """, unsafe_allow_html=True)
    
    # Sidebar avec navigation
    try:
        current_page = show_sidebar()
    except Exception as e:
        st.error(f"Erreur sidebar : {e}")
        current_page = "dashboard"
    
    # Contenu principal basé sur la page sélectionnée
    try:
        if current_page == "dashboard":
            from views.dashboard import dashboard_page
            dashboard_page()
            
        elif current_page == "produits":
            from views.produits import produits_page
            produits_page()
            
        elif current_page == "ventes":
            from views.ventes import ventes_page
            ventes_page()
            
        elif current_page == "clients":
            from views.clients import clients_page
            clients_page()
            
        elif current_page == "stock":
            from views.stock import stock_page
            stock_page()
            
        elif current_page == "fournisseurs":
            from views.fournisseurs import fournisseurs_page
            fournisseurs_page()
            
        elif current_page == "comptabilite":
            from views.comptabilite import comptabilite_page
            comptabilite_page()
            
        elif current_page == "rendez_vous":
            from views.rendez_vous import rendez_vous_page
            rendez_vous_page()
            
        elif current_page == "rapports":
            from views.rapports import rapports_page
            rapports_page()
            
        elif current_page == "parametres":
            from views.parametres import parametres_page
            parametres_page()
            
        elif current_page == "logout":
            # Déconnexion
            st.session_state.authenticated = False
            st.success("✅ Déconnecté avec succès")
            st.rerun()
            
    except ImportError as e:
        st.error(f"Page non trouvée : {e}")
        st.info("La page demandée n'est pas encore implémentée")
    except Exception as e:
        st.error(f"Erreur : {str(e)}")
        if st.button("🔄 Revenir au Dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()

if __name__ == "__main__":
    main()