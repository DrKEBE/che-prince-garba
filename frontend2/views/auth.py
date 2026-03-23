"""
Page d'authentification
"""
import streamlit as st
import time
from datetime import datetime
import hashlib

from services.auth_service import AuthService
from services.api_client import APIClient
from utils.session_state import SessionStateManager
from config.theme import ThemeManager
from config.components import set_custom_css

def login_page():
    """Page de connexion"""
    
    # Configuration
    st.set_page_config(
        page_title="Connexion - Luxe Beauté",
        page_icon="🔐",
        layout="centered"
    )
    
    # Appliquer le CSS
    set_custom_css()
    ThemeManager.apply_theme()
    
    # Services
    auth_service = AuthService()
    api_client = APIClient()
    
    # Vérifier si déjà connecté
    if st.session_state.get('authenticated'):
        st.success("✅ Vous êtes déjà connecté !")
        time.sleep(1)
        st.switch_page("app.py")
        return
    
    # CSS spécifique à la page de login
    login_css = """
    <style>
    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2.5rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .login-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, 
            #FF6B9D 0%, 
            #9B59B6 50%, 
            #FF6B9D 100%
        );
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-logo {
        font-size: 3rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .login-title {
        color: #2C3E50;
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        color: #7F8C8D;
        font-size: 0.875rem;
    }
    
    .login-form {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .form-label {
        font-weight: 500;
        color: #2C3E50;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .form-input {
        padding: 0.75rem 1rem;
        border: 1px solid #DEE2E6;
        border-radius: 10px;
        font-size: 1rem;
        transition: all 0.3s;
    }
    
    .form-input:focus {
        outline: none;
        border-color: #FF6B9D;
        box-shadow: 0 0 0 3px rgba(255, 107, 157, 0.1);
    }
    
    .login-btn {
        background: linear-gradient(90deg, #FF6B9D 0%, #9B59B6 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        margin-top: 1rem;
    }
    
    .login-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(255, 107, 157, 0.3);
    }
    
    .login-footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #E9ECEF;
        color: #7F8C8D;
        font-size: 0.875rem;
    }
    
    .forgot-password {
        text-align: right;
        margin-top: 0.5rem;
    }
    
    .forgot-password a {
        color: #FF6B9D;
        text-decoration: none;
        font-size: 0.875rem;
    }
    
    .forgot-password a:hover {
        text-decoration: underline;
    }
    
    .demo-credentials {
        background: #F8F9FA;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1.5rem;
        font-size: 0.875rem;
    }
    
    .demo-title {
        font-weight: 600;
        color: #2C3E50;
        margin-bottom: 0.5rem;
    }
    
    .demo-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.25rem;
    }
    
    .demo-label {
        color: #7F8C8D;
    }
    
    .demo-value {
        font-weight: 500;
        color: #2C3E50;
    }
    
    .error-message {
        background: #F8D7DA;
        color: #721C24;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #DC3545;
    }
    
    .success-message {
        background: #D4EDDA;
        color: #155724;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #28A745;
    }
    
    /* Animation de chargement */
    .spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s ease-in-out infinite;
        margin-right: 10px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Responsive */
    @media (max-width: 480px) {
        .login-container {
            margin: 1rem;
            padding: 1.5rem;
        }
    }
    </style>
    """
    
    st.markdown(login_css, unsafe_allow_html=True)
    
    # Contenu de la page
    login_html = """
    <div class="login-container">
        <div class="login-header">
            <div class="login-logo">💄</div>
            <div class="login-title">Luxe Beauté Management</div>
            <div class="login-subtitle">Système de gestion premium pour instituts de beauté</div>
        </div>
    """
    
    st.markdown(login_html, unsafe_allow_html=True)
    
    # Formulaire de connexion
    with st.form("login_form"):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            username = st.text_input(
                "👤 Nom d'utilisateur",
                placeholder="Entrez votre nom d'utilisateur",
                key="username_input"
            )
            
            password = st.text_input(
                "🔒 Mot de passe",
                type="password",
                placeholder="Entrez votre mot de passe",
                key="password_input"
            )
            
            # Options
            col_a, col_b = st.columns(2)
            with col_a:
                remember_me = st.checkbox("Se souvenir de moi", value=True)
            
           
            # Bouton de connexion
            login_button = st.form_submit_button(
                "🔓 Se connecter",
                type="primary",
                use_container_width=True
            )
    
        # Bouton Mot de passe oublié (hors form)
    forgot_password = st.button("Mot de passe oublié ?", type="secondary")
 
    # Gestion du mot de passe oublié
    if forgot_password:
        st.info("📧 Un lien de réinitialisation sera envoyé à votre email.")
    
    # Traitement de la connexion
    if login_button:
        if not username or not password:
            st.error("⚠️ Veuillez remplir tous les champs")
        else:
            # Indicateur de chargement
            with st.spinner("Connexion en cours..."):
                # Simuler un délai pour l'animation
                time.sleep(0.5)
                
                # Tentative de connexion
                if auth_service.login(username, password):
                    # Initialiser l'état de session
                    SessionStateManager.init_session_state()
                    
                    # Redirection
                    st.success("✅ Connexion réussie !")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
    
    # Pied de page
    footer_html = """
        <div class="login-footer">
            <div class="demo-credentials">
                <div class="demo-title">💡 Démonstration</div>
                <div class="demo-item">
                    <span class="demo-label">Utilisateur:</span>
                    <span class="demo-value">admin</span>
                </div>
                <div class="demo-item">
                    <span class="demo-label">Mot de passe:</span>
                    <span class="demo-value">admin123</span>
                </div>
            </div>
            
            <div style="margin-top: 1.5rem;">
                © 2024 Luxe Beauté Management • v2.0.0
            </div>
        </div>
    </div>
    """
    
    st.markdown(footer_html, unsafe_allow_html=True)
    
    # Script pour les interactions
    script_js = """
    <script>
    // Focus automatique sur le champ utilisateur
    document.addEventListener('DOMContentLoaded', function() {
        const usernameInput = document.querySelector('input[placeholder*="nom d\\'utilisateur"]');
        if (usernameInput) {
            usernameInput.focus();
        }
        
        // Animation d'entrée
        const container = document.querySelector('.login-container');
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            container.style.transition = 'all 0.5s ease';
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 100);
        
        // Gestion du mot de passe oublié
        document.querySelectorAll('[data-testid="stButton"][kind="secondary"]').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                alert('Fonctionnalité à venir : réinitialisation par email');
            });
        });
    });
    
    // Validation en temps réel
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', function() {
            const form = this.closest('form');
            const submitBtn = form.querySelector('[data-testid="stButton"][kind="primary"]');
            
            if (this.value.trim() === '') {
                this.style.borderColor = '#E74C3C';
            } else {
                this.style.borderColor = '#2ECC71';
            }
        });
    });
    </script>
    """
    
    st.markdown(script_js, unsafe_allow_html=True)

def register_page():
    """Page d'inscription"""
    st.title("📝 Créer un compte")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("Prénom", placeholder="Votre prénom")
            email = st.text_input("Email", placeholder="votre@email.com")
            username = st.text_input("Nom d'utilisateur", placeholder="Choisissez un nom d'utilisateur")
        
        with col2:
            last_name = st.text_input("Nom", placeholder="Votre nom")
            phone = st.text_input("Téléphone", placeholder="+225 XX XX XX XX")
            role = st.selectbox("Rôle", ["CASHIER", "STOCK_MANAGER", "MANAGER"])
        
        password = st.text_input("Mot de passe", type="password")
        confirm_password = st.text_input("Confirmer le mot de passe", type="password")
        
        col_a, col_b = st.columns(2)
        with col_a:
            terms = st.checkbox("J'accepte les conditions d'utilisation")
        
        submit = st.form_submit_button("Créer le compte", type="primary")
        
        if submit:
            # Validation
            if not all([first_name, last_name, email, username, password]):
                st.error("Veuillez remplir tous les champs obligatoires")
            elif password != confirm_password:
                st.error("Les mots de passe ne correspondent pas")
            elif not terms:
                st.error("Veuillez accepter les conditions d'utilisation")
            else:
                # Tentative d'inscription
                try:
                    # Dans une application réelle, appeler l'API d'inscription
                    st.success("Compte créé avec succès !")
                    st.info("Un email de confirmation vous a été envoyé.")
                    time.sleep(2)
                    st.switch_page("views/auth.py")
                except Exception as e:
                    st.error(f"Erreur lors de la création du compte: {str(e)}")

def logout_page():
    """Page de déconnexion"""
    auth_service = AuthService()
    auth_service.logout()
    
    st.success("✅ Déconnexion réussie !")
    time.sleep(1)
    st.switch_page("views/auth.py")

if __name__ == "__main__":
    login_page()