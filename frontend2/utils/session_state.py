import os

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"



"""
Gestionnaire d'état de session pour Streamlit
"""
import streamlit as st
from datetime import datetime, timedelta
import json
import hashlib

class SessionStateManager:
    """Gère l'état de session de l'application"""
    
    @staticmethod
    def init_session_state():
        """Initialise l'état de session"""
        defaults = {
            # Authentification
            'authenticated': True if DEV_MODE else False,
            'auth_token': None,
            'user_info': {},
            'login_time': None,
            
            # Navigation
            'current_page': 'dashboard',
            'previous_page': None,
            'page_history': [],
            
            # Données
            'products_cache': {},
            'clients_cache': {},
            'sales_cache': {},
            'last_refresh': {},
            
            # Paramètres utilisateur
            'theme': 'light',
            'language': 'fr',
            'notifications_enabled': True,
            'auto_refresh': True,
            'refresh_interval': 300,  # 5 minutes
            
            # Filtres persistants
            'product_filters': {},
            'client_filters': {},
            'sales_filters': {},
            
            # Panier de vente temporaire
            'cart': [],
            'current_sale': None,
            'selected_client': None,
            
            # Statistiques
            'app_start_time': datetime.now().timestamp(),
            'page_views': {},
            'user_actions': [],
            
            # Configuration
            'app_config': {},
            'permissions': [],
            'user_role': None,
            
            # Cache d'images
            'images_cache': {},
            
            # État des formulaires
            'form_data': {},
            'form_errors': {},
            
            # Sélection multiple
            'selected_items': {
                'products': [],
                'clients': [],
                'sales': []
            }
        }
        
        # Initialiser les valeurs par défaut
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        if DEV_MODE:
            st.session_state['user_info'] = {
                'id': 1,
                'username': 'dev_admin',
                'role': 'admin'
            }
            st.session_state['login_time'] = datetime.now().timestamp()
            st.session_state['user_role'] = 'admin'

    @staticmethod
    def update_session_state(key, value):
        """Met à jour l'état de session"""
        st.session_state[key] = value
        
        # Journaliser les modifications importantes
        if key in ['authenticated', 'current_page', 'selected_client']:
            SessionStateManager.log_action(f"session_update_{key}", value)
    
    @staticmethod
    def get_session_state(key, default=None):
        """Récupère une valeur de l'état de session"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def clear_session_state(keys=None):
        """Efface tout ou partie de l'état de session"""
        if keys is None:
            # Sauvegarder certaines données importantes
            important_keys = ['authenticated', 'user_info', 'theme', 'language']
            backup = {k: st.session_state.get(k) for k in important_keys}
            
            # Effacer tout
            st.session_state.clear()
            
            # Restaurer les données importantes
            for k, v in backup.items():
                if v is not None:
                    st.session_state[k] = v
        else:
            for key in keys:
                if key in st.session_state:
                    del st.session_state[key]
    
    @staticmethod
    def save_state_to_local():
        """Sauvegarde l'état de session dans le stockage local (simulé)"""
        try:
            # Ne sauvegarder que les données non sensibles
            state_to_save = {
                'theme': st.session_state.get('theme'),
                'language': st.session_state.get('language'),
                'user_preferences': {
                    'notifications_enabled': st.session_state.get('notifications_enabled'),
                    'auto_refresh': st.session_state.get('auto_refresh'),
                    'refresh_interval': st.session_state.get('refresh_interval')
                },
                'filters': {
                    'products': st.session_state.get('product_filters', {}),
                    'clients': st.session_state.get('client_filters', {}),
                    'sales': st.session_state.get('sales_filters', {})
                }
            }
            
            # Convertir en JSON
            state_json = json.dumps(state_to_save)
            
            # Dans une application réelle, on sauvegarderait dans localStorage
            # Pour Streamlit, on simule avec session_state
            st.session_state['saved_state'] = state_json
            
            return True
        except Exception as e:
            print(f"Erreur sauvegarde état: {e}")
            return False
    
    @staticmethod
    def load_state_from_local():
        """Charge l'état de session depuis le stockage local"""
        try:
            saved_state = st.session_state.get('saved_state')
            if saved_state:
                state_data = json.loads(saved_state)
                
                # Restaurer les préférences
                if 'theme' in state_data:
                    st.session_state['theme'] = state_data['theme']
                
                if 'language' in state_data:
                    st.session_state['language'] = state_data['language']
                
                if 'user_preferences' in state_data:
                    prefs = state_data['user_preferences']
                    st.session_state['notifications_enabled'] = prefs.get('notifications_enabled', True)
                    st.session_state['auto_refresh'] = prefs.get('auto_refresh', True)
                    st.session_state['refresh_interval'] = prefs.get('refresh_interval', 300)
                
                if 'filters' in state_data:
                    filters = state_data['filters']
                    st.session_state['product_filters'] = filters.get('products', {})
                    st.session_state['client_filters'] = filters.get('clients', {})
                    st.session_state['sales_filters'] = filters.get('sales', {})
                
                return True
        except Exception as e:
            print(f"Erreur chargement état: {e}")
        
        return False
    
    @staticmethod
    def log_action(action_type: str, details=None):
        """Journalise les actions utilisateur"""
        if 'user_actions' not in st.session_state:
            st.session_state['user_actions'] = []
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action_type,
            'details': details,
            'page': st.session_state.get('current_page'),
            'user': st.session_state.get('user_info', {}).get('username')
        }
        
        st.session_state['user_actions'].append(log_entry)
        
        # Limiter l'historique à 1000 entrées
        if len(st.session_state['user_actions']) > 1000:
            st.session_state['user_actions'] = st.session_state['user_actions'][-1000:]
    
    @staticmethod
    def get_user_actions(limit=50):
        """Récupère les dernières actions utilisateur"""
        actions = st.session_state.get('user_actions', [])
        return actions[-limit:] if limit else actions
    
    @staticmethod
    def track_page_view(page_name: str):
        """Suivi des vues de pages"""
        if 'page_views' not in st.session_state:
            st.session_state['page_views'] = {}
        
        current_time = datetime.now()
        today = current_time.date().isoformat()
        
        if today not in st.session_state['page_views']:
            st.session_state['page_views'][today] = {}
        
        if page_name not in st.session_state['page_views'][today]:
            st.session_state['page_views'][today][page_name] = 0
        
        st.session_state['page_views'][today][page_name] += 1
        
        # Mettre à jour l'historique de navigation
        if 'page_history' not in st.session_state:
            st.session_state['page_history'] = []
        
        st.session_state['page_history'].append({
            'page': page_name,
            'timestamp': current_time.isoformat()
        })
        
        # Limiter l'historique à 100 entrées
        if len(st.session_state['page_history']) > 100:
            st.session_state['page_history'] = st.session_state['page_history'][-100:]
    
    @staticmethod
    def get_page_stats(days=7):
        """Récupère les statistiques de pages"""
        page_views = st.session_state.get('page_views', {})
        
        stats = {}
        for date_str, views in page_views.items():
            date = datetime.fromisoformat(date_str).date()
            days_ago = (datetime.now().date() - date).days
            
            if days_ago <= days:
                for page, count in views.items():
                    if page not in stats:
                        stats[page] = 0
                    stats[page] += count
        
        return stats
    
    @staticmethod
    def add_to_cart(item: dict, quantity: int = 1):
        """Ajoute un produit au panier"""
        if 'cart' not in st.session_state:
            st.session_state['cart'] = []
        
        # Vérifier si le produit est déjà dans le panier
        for i, cart_item in enumerate(st.session_state['cart']):
            if cart_item['product_id'] == item.get('product_id'):
                st.session_state['cart'][i]['quantity'] += quantity
                st.session_state['cart'][i]['total'] = st.session_state['cart'][i]['quantity'] * cart_item['unit_price']
                SessionStateManager.log_action('cart_update', {'product_id': item['product_id'], 'quantity': quantity})
                return
        
        # Ajouter le nouvel article
        cart_item = {
            'product_id': item.get('product_id'),
            'name': item.get('name'),
            'unit_price': item.get('selling_price', 0),
            'quantity': quantity,
            'total': quantity * item.get('selling_price', 0),
            'stock': item.get('current_stock', 0),
            'category': item.get('category')
        }
        
        st.session_state['cart'].append(cart_item)
        SessionStateManager.log_action('cart_add', {'product_id': item['product_id'], 'quantity': quantity})
    
    @staticmethod
    def remove_from_cart(product_id: str):
        """Retire un produit du panier"""
        if 'cart' not in st.session_state:
            return
        
        st.session_state['cart'] = [item for item in st.session_state['cart'] if item['product_id'] != product_id]
        SessionStateManager.log_action('cart_remove', {'product_id': product_id})
    
    @staticmethod
    def clear_cart():
        """Vide le panier"""
        if 'cart' in st.session_state:
            SessionStateManager.log_action('cart_clear', {'items_count': len(st.session_state['cart'])})
            st.session_state['cart'] = []
    
    @staticmethod
    def get_cart_total():
        """Calcule le total du panier"""
        if 'cart' not in st.session_state:
            return 0
        
        return sum(item.get('total', 0) for item in st.session_state['cart'])
    
    @staticmethod
    def get_cart_item_count():
        """Compte le nombre d'articles dans le panier"""
        if 'cart' not in st.session_state:
            return 0
        
        return sum(item.get('quantity', 0) for item in st.session_state['cart'])
    
    @staticmethod
    def select_item(item_type: str, item_id: str, selected: bool = True):
        """Sélectionne/désélectionne un élément"""
        if 'selected_items' not in st.session_state:
            st.session_state['selected_items'] = {
                'products': [],
                'clients': [],
                'sales': []
            }
        
        if item_type not in st.session_state['selected_items']:
            st.session_state['selected_items'][item_type] = []
        
        if selected:
            if item_id not in st.session_state['selected_items'][item_type]:
                st.session_state['selected_items'][item_type].append(item_id)
        else:
            st.session_state['selected_items'][item_type] = [
                id for id in st.session_state['selected_items'][item_type] 
                if id != item_id
            ]
    
    @staticmethod
    def clear_selection(item_type: str = None):
        """Efface la sélection"""
        if item_type:
            if item_type in st.session_state.get('selected_items', {}):
                st.session_state['selected_items'][item_type] = []
        else:
            if 'selected_items' in st.session_state:
                for key in st.session_state['selected_items']:
                    st.session_state['selected_items'][key] = []
    
    @staticmethod
    def get_selected_items(item_type: str):
        """Récupère les éléments sélectionnés"""
        return st.session_state.get('selected_items', {}).get(item_type, [])
    
    @staticmethod
    def create_session_token():
        """Crée un token de session unique"""
        session_data = {
            'user_id': st.session_state.get('user_info', {}).get('id'),
            'timestamp': datetime.now().isoformat(),
            'random': hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()
        }
        
        token = hashlib.sha256(json.dumps(session_data).encode()).hexdigest()
        st.session_state['session_token'] = token
        
        return token
    
    @staticmethod
    def validate_session():
        if DEV_MODE:
            return True

        """Valide la session en cours"""
        if not st.session_state.get('authenticated'):
            return False
        
        # Vérifier le timeout de session
        login_time = st.session_state.get('login_time')
        if not login_time:
            return False
        
        # Timeout de 30 minutes
        if datetime.now().timestamp() - login_time > 1800:
            st.session_state['authenticated'] = False
            st.session_state['session_expired'] = True
            return False
        
        return True

# Fonctions d'export
def init_session_state():
    """Initialise l'état de session (fonction d'export)"""
    return SessionStateManager.init_session_state()

def get_session_state(key, default=None):
    """Récupère l'état de session (fonction d'export)"""
    return SessionStateManager.get_session_state(key, default)

def update_session_state(key, value):
    """Met à jour l'état de session (fonction d'export)"""
    return SessionStateManager.update_session_state(key, value)