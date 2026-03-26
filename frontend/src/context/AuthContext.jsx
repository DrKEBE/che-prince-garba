import React, { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/auth';

const DEV_MODE = import.meta.env.VITE_DEV_MODE === 'true';

export const AuthContext = createContext({});   // ← ajout de 'export'

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Vérifier l'authentification au démarrage
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('user');
    
    console.log('Initial auth check:', { token, storedUser });
    
    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Error parsing user:', e);
        localStorage.removeItem('user');
        localStorage.removeItem('auth_token');
      }
    }
    
    // Mode développement : auto-login
    if (DEV_MODE && !token) {
      console.log('[DEV] Auto-login for development');
      const devUser = {
        id: 1,
        username: 'admin',
        full_name: 'Administrateur',
        role: 'admin',
      };
      localStorage.setItem('auth_token', 'dev-fake-token-123');
      localStorage.setItem('user', JSON.stringify(devUser));
      setUser(devUser);
    }
    
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    setError(null);
    
    // ===== MODE DÉVELOPPEMENT =====
    if (DEV_MODE) {
      console.log('[DEV] Login attempt:', username);
      
      const devUsers = {
        'admin': { id: 1, username: 'admin', role: 'admin', full_name: 'Administrateur' },
        'manager': { id: 2, username: 'manager', role: 'manager', full_name: 'Manager' },
        'cashier': { id: 3, username: 'cashier', role: 'cashier', full_name: 'Caissier' },
        'user': { id: 4, username: 'user', role: 'user', full_name: 'Utilisateur' }
      };
      
      const userData = devUsers[username] || devUsers['admin'];
      const devToken = import.meta.env.VITE_DEV_TOKEN || 'fake-token-admin';
      
      localStorage.setItem('auth_token', devToken);
      localStorage.setItem('user', JSON.stringify(userData));
      
      setUser(userData);
      
      return { success: true, user: userData };
    }
    
    // ===== MODE PRODUCTION =====
    try {
      // Utiliser le service auth.js
      const result = await authService.login(username, password);
      
      if (result.success) {
        // authService a déjà stocké le token et l'utilisateur dans localStorage
        const storedUser = authService.getStoredUser();
        setUser(storedUser);
        return { success: true, user: storedUser };
      } else {
        setError(result.error);
        return { success: false, error: result.error };
      }
    } catch (err) {
      console.error('Login error:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Erreur de connexion';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    }
  };

  const logout = () => {
    authService.logout(); // cela efface tout et redirige vers /login
    setUser(null);
    setError(null);
  };

  const updateUser = async (userData) => {
    setError(null);
    
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    
    return { success: true, user: userData };
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    updateUser,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    isManager: user?.role === 'manager' || user?.role === 'admin',
    clearError: () => setError(null)
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};