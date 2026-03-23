// src/services/auth.js
import api from './api';
import { API_CONFIG, ROLES } from '../constants/config';

// Service d'authentification
export const authService = {
  /**
   * Connexion utilisateur
   * @param {string} username - Nom d'utilisateur
   * @param {string} password - Mot de passe
   * @returns {Promise<Object>} Réponse avec token et utilisateur
   */
  async login(username, password) {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await api.post('/auth/token', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const { access_token, token_type, user } = response.data;
      
      // Stocker les données d'authentification
      this.setAuthData(access_token, user);
      
      return {
        success: true,
        token: access_token,
        user,
        token_type
      };
    } catch (error) {
      return this.handleAuthError(error);
    }
  },

  /**
   * Inscription d'un nouvel utilisateur
   * @param {Object} userData - Données d'inscription
   * @returns {Promise<Object>} Utilisateur créé
   */
  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return this.handleAuthError(error);
    }
  },

  /**
   * Récupérer l'utilisateur courant
   * @returns {Promise<Object>} Données utilisateur
   */
  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me');
      const user = response.data;
      
      // Mettre à jour le stockage local
      localStorage.setItem('user', JSON.stringify(user));
      
      return {
        success: true,
        user
      };
    } catch (error) {
      // Si erreur 401, déconnecter
      if (error.response?.status === 401) {
        this.clearAuthData();
      }
      return {
        success: false,
        error: error.response?.data?.detail || 'Erreur de récupération utilisateur'
      };
    }
  },

  /**
   * Déconnexion utilisateur
   */
  logout() {
    this.clearAuthData();
    window.location.href = '/login';
  },

  /**
   * Mettre à jour les données utilisateur
   * @param {Object} userData - Nouvelles données utilisateur
   * @returns {Promise<Object>} Résultat de la mise à jour
   */
  async updateUser(userData) {
    try {
      // Note: Endpoint à implémenter dans le backend
      // const response = await api.put('/auth/me', userData);
      // return { success: true, user: response.data };
      
      // Pour l'instant, mettre à jour le stockage local
      const currentUser = this.getStoredUser();
      const updatedUser = { ...currentUser, ...userData };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      
      return {
        success: true,
        user: updatedUser
      };
    } catch (error) {
      return this.handleAuthError(error);
    }
  },

  /**
   * Vérifier si l'utilisateur est authentifié
   * @returns {boolean} Authentifié ou non
   */
  isAuthenticated() {
    const token = localStorage.getItem('auth_token');
    const user = localStorage.getItem('user');
    return !!(token && user);
  },

  /**
   * Vérifier si l'utilisateur a un rôle spécifique
   * @param {string|Array} requiredRoles - Rôle ou liste de rôles requis
   * @returns {boolean} True si l'utilisateur a le rôle
   */
  hasRole(requiredRoles) {
    const user = this.getStoredUser();
    if (!user || !user.role) return false;
    
    if (Array.isArray(requiredRoles)) {
      return requiredRoles.includes(user.role);
    }
    
    return user.role === requiredRoles;
  },

  /**
   * Vérifier si l'utilisateur a une permission spécifique
   * @param {string} permission - Permission à vérifier
   * @returns {boolean} True si l'utilisateur a la permission
   */
  hasPermission(permission) {
    const user = this.getStoredUser();
    if (!user || !user.role) return false;
    
    // Utiliser les permissions par rôle depuis config.js
    const rolePermissions = {
      [ROLES.ADMIN]: ['all'],
      [ROLES.MANAGER]: [
        'view_dashboard', 'manage_products', 'manage_sales', 'manage_clients',
        'manage_stock', 'manage_accounting', 'view_financial_reports',
        'manage_expenses', 'manage_appointments', 'view_reports', 'export_data'
      ],
      [ROLES.CASHIER]: [
        'view_dashboard', 'view_products', 'manage_sales', 'manage_clients',
        'process_refunds', 'view_invoices', 'view_reports'
      ],
      [ROLES.STOCK_MANAGER]: [
        'view_dashboard', 'manage_products', 'manage_stock', 'manage_suppliers',
        'manage_purchase_orders', 'view_sales', 'view_reports', 'export_data'
      ],
      [ROLES.BEAUTICIAN]: [
        'view_dashboard', 'manage_appointments', 'view_clients', 'view_products'
      ]
    };
    
    const permissions = rolePermissions[user.role] || [];
    return permissions.includes('all') || permissions.includes(permission);
  },

  /**
   * Récupérer l'utilisateur stocké
   * @returns {Object|null} Utilisateur ou null
   */
  getStoredUser() {
    const userData = localStorage.getItem('user');
    if (!userData) return null;
    
    try {
      return JSON.parse(userData);
    } catch (error) {
      console.error('Erreur de parsing des données utilisateur:', error);
      return null;
    }
  },

  /**
   * Récupérer le token d'authentification
   * @returns {string|null} Token ou null
   */
  getToken() {
    return localStorage.getItem('auth_token');
  },

  /**
   * Stocker les données d'authentification
   * @param {string} token - Token d'accès
   * @param {Object} user - Données utilisateur
   */
  setAuthData(token, user) {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user', JSON.stringify(user));
    
    // Configurer le header Authorization pour toutes les futures requêtes
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  },

  /**
   * Effacer les données d'authentification
   */
  clearAuthData() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    delete api.defaults.headers.common['Authorization'];
  },

  /**
   * Gérer les erreurs d'authentification
   * @param {Error} error - Erreur axios
   * @returns {Object} Erreur formatée
   */
  handleAuthError(error) {
    const status = error.response?.status;
    const detail = error.response?.data?.detail;
    
    let message = 'Une erreur est survenue';
    
    switch (status) {
      case 400:
        message = detail || 'Données invalides';
        break;
      case 401:
        message = 'Identifiants incorrects';
        break;
      case 403:
        message = 'Accès non autorisé';
        break;
      case 404:
        message = 'Ressource non trouvée';
        break;
      case 409:
        message = 'Conflit de données';
        break;
      case 422:
        message = 'Validation des données échouée';
        break;
      case 500:
        message = 'Erreur serveur';
        break;
    }
    
    return {
      success: false,
      error: message,
      status,
      detail
    };
  },

  /**
   * Vérifier si l'utilisateur est admin
   * @returns {boolean} True si admin
   */
  isAdmin() {
    return this.hasRole(ROLES.ADMIN);
  },

  /**
   * Vérifier si l'utilisateur est manager
   * @returns {boolean} True si manager
   */
  isManager() {
    return this.hasRole([ROLES.MANAGER, ROLES.ADMIN]);
  },

  /**
   * Rafraîchir le token (à implémenter si backend supporte refresh token)
   */
  async refreshToken() {
    // TODO: Implémenter si backend ajoute /auth/refresh
    console.log('Refresh token non implémenté');
    return { success: false };
  },

  /**
   * Changer le mot de passe (à implémenter)
   */
  async changePassword(oldPassword, newPassword) {
    // TODO: Implémenter quand backend ajoutera l'endpoint
    console.log('Changement de mot de passe non implémenté');
    return { success: false };
  },

  /**
   * Récupérer les données d'authentification pour l'initialisation
   * @returns {Object} Données d'auth
   */
  getAuthData() {
    return {
      token: this.getToken(),
      user: this.getStoredUser(),
      isAuthenticated: this.isAuthenticated()
    };
  }
};

// Export par défaut
export default authService;

// Hook personnalisé pour utiliser l'authentification
export const useAuth = () => {
  return {
    login: authService.login,
    logout: authService.logout,
    register: authService.register,
    getCurrentUser: authService.getCurrentUser,
    updateUser: authService.updateUser,
    isAuthenticated: authService.isAuthenticated,
    hasRole: authService.hasRole,
    hasPermission: authService.hasPermission,
    isAdmin: authService.isAdmin,
    isManager: authService.isManager,
    getToken: authService.getToken,
    getStoredUser: authService.getStoredUser,
    refreshToken: authService.refreshToken,
    changePassword: authService.changePassword
  };
};