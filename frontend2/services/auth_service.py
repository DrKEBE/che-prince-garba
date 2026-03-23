import streamlit as st
import time
from datetime import datetime, timedelta
from jose import jwt

from typing import Optional, Dict, Any

from config.constants import APP_CONFIG
from services.api_client import APIClient

class AuthService:
    """Service d'authentification"""
    
    def __init__(self):
        self.api_client = APIClient()
        self.session_timeout = 30 * 60  # 30 minutes en secondes
    
    def login(self, username: str, password: str) -> bool:
        """Authentifie l'utilisateur"""
        try:
            # Afficher un indicateur de chargement
            with st.spinner("Connexion en cours..."):
                # Appel API
                result = self.api_client.login(username, password)
                
                if result and result.get('access_token'):
                    # Stocker les informations de session
                    st.session_state.authenticated = True
                    st.session_state.auth_token = result['access_token']
                    st.session_state.user_info = result.get('user', {})
                    st.session_state.login_time = time.time()
                    
                    # Journaliser la connexion
                    self._log_login(username, True)
                    
                    st.success(f"Bienvenue {result['user'].get('full_name', '')} !")
                    time.sleep(1)
                    return True
                else:
                    self._log_login(username, False)
                    st.error("Nom d'utilisateur ou mot de passe incorrect")
                    return False
                    
        except Exception as e:
            st.error(f"Erreur de connexion: {str(e)}")
            self._log_login(username, False, str(e))
            return False
    
    def logout(self):
        """Déconnecte l'utilisateur"""
        # Journaliser la déconnexion
        self._log_logout()
        
        # Nettoyer la session
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        st.success("Déconnexion réussie !")
        time.sleep(1)
    
    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est authentifié"""
        if not st.session_state.get('authenticated'):
            return False
        
        # Vérifier le timeout de session
        login_time = st.session_state.get('login_time', 0)
        if time.time() - login_time > self.session_timeout:
            st.warning("Session expirée. Veuillez vous reconnecter.")
            self.logout()
            return False
        
        return True
    
    def check_permission(self, required_role: str = None) -> bool:
        """Vérifie les permissions de l'utilisateur"""
        if not self.is_authenticated():
            return False
        
        user_info = st.session_state.get('user_info', {})
        user_role = user_info.get('role')
        
        # Mapping des rôles et permissions
        role_hierarchy = {
            'ADMIN': 4,
            'MANAGER': 3,
            'STOCK_MANAGER': 2,
            'CASHIER': 1,
            'BEAUTICIAN': 0
        }
        
        if required_role:
            required_level = role_hierarchy.get(required_role, 0)
            user_level = role_hierarchy.get(user_role, 0)
            return user_level >= required_level
        
        return True
    
    def get_user_info(self) -> Dict[str, Any]:
        """Récupère les informations de l'utilisateur"""
        return st.session_state.get('user_info', {})
    
    def refresh_token(self) -> bool:
        """Rafraîchit le token d'authentification"""
        try:
            # Récupérer le token actuel
            token = st.session_state.get('auth_token')
            if not token:
                return False
            
            # Décoder le token pour vérifier l'expiration
            decoded = jwt.decode(token, options={"verify_signature": False})
            exp_time = decoded.get('exp', 0)
            
            # Rafraîchir si le token expire dans moins de 5 minutes
            if exp_time - time.time() < 300:
                # Dans une implémentation réelle, appeler l'endpoint de refresh
                # Pour l'instant, on se contente de renouveler le timestamp
                st.session_state.login_time = time.time()
                return True
            
            return True
        except:
            return False
    
    def _log_login(self, username: str, success: bool, error: str = None):
        """Journalise les tentatives de connexion"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'success': success,
            'ip': st.session_state.get('client_ip', 'unknown'),
            'user_agent': st.session_state.get('user_agent', 'unknown'),
            'error': error
        }
        
        # Stocker dans l'historique des connexions
        if 'login_history' not in st.session_state:
            st.session_state.login_history = []
        
        st.session_state.login_history.append(log_entry)
        
        # Limiter l'historique à 100 entrées
        if len(st.session_state.login_history) > 100:
            st.session_state.login_history = st.session_state.login_history[-100:]
    
    def _log_logout(self):
        """Journalise les déconnexions"""
        user_info = self.get_user_info()
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'username': user_info.get('username', 'unknown'),
            'session_duration': time.time() - st.session_state.get('login_time', 0)
        }
        
        if 'logout_history' not in st.session_state:
            st.session_state.logout_history = []
        
        st.session_state.logout_history.append(log_entry)
    
    def get_login_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de connexion"""
        history = st.session_state.get('login_history', [])
        
        successful = sum(1 for log in history if log['success'])
        failed = len(history) - successful
        
        recent_logins = history[-10:] if history else []
        
        return {
            'total_attempts': len(history),
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / len(history) * 100) if history else 0,
            'recent_logins': recent_logins
        }
    
