// frontend\src\services\api.js
import axios from 'axios';

// Configuration basée sur l'environnement
const ENV = import.meta.env;
const IS_DEV = ENV.VITE_DEV_MODE === 'true';

// EN DÉVELOPPEMENT : Utilisez '/api/v1' directement (proxy Vite intercepte)
// EN PRODUCTION : Utilisez l'URL directe avec '/api/v1'
const api = axios.create({
  baseURL: IS_DEV 
    ? '/api/v1'  // ← Proxy Vite intercepte '/api/v1'
    : `${ENV.VITE_API_URL || 'http://localhost:8000'}/api/v1`,  // ← URL directe en prod
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false,
});

// Intercepteur de requête amélioré
api.interceptors.request.use(
  (config) => {
    // Mode développement - logging
    if (IS_DEV) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
      
      // Token de développement
      const devToken = ENV.VITE_DEV_TOKEN || 'fake-token-admin';
      const storedToken = localStorage.getItem('auth_token');
      
      // Priorité : stored token > dev token
      if (storedToken) {
        config.headers.Authorization = `Bearer ${storedToken}`;
      } else if (devToken) {
        config.headers.Authorization = `Bearer ${devToken}`;
        config.headers['X-Dev-Mode'] = 'true';
      }
    } else {
      // Mode production
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Intercepteur de réponse avec gestion d'erreur améliorée
api.interceptors.response.use(
  (response) => {
    if (IS_DEV) {
      console.log(`[API] Response ${response.status} from ${response.config.url}`);
    }
    return response;
  },
  (error) => {
    const { config, response } = error;
    
    if (IS_DEV) {
      console.error('[API] Error:', {
        url: config?.url,
        method: config?.method,
        status: response?.status,
        data: response?.data,
      });
      
      // Simulation de réponse pour le développement si backend hors ligne
      if (!response && config?.url?.includes('/dashboard/')) {
        console.warn('[DEV] Backend offline, returning mock data for:', config.url);
        
        // Mock data pour le développement
        const mockData = getMockData(config.url);
        if (mockData) {
          return Promise.resolve({
            data: mockData,
            status: 200,
            statusText: 'OK',
            headers: {},
            config,
          });
        }
      }
    }
    
    // Gestion des erreurs spécifiques
    if (response?.status === 401) {
      // Rediriger vers login si non authentifié
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Fonction helper pour les données mock en dev
function getMockData(url) {
  // NOTE: config.url est le chemin RELATIF après baseURL
  // Ex: baseURL = '/api/v1', config.url = '/dashboard/stats'
  const mockDatabase = {
    '/dashboard/stats': {
      total_sales: 125430.50,
      total_clients: 342,
      total_products: 156,
      low_stock_items: 12,
      monthly_growth: 15.3,
    },
    '/dashboard/sales-trend': {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      data: [65000, 81000, 72000, 89000, 93000, 125000],
    },
    '/dashboard/inventory-alerts': [
      { id: 1, name: 'Crème Hydratante Luxe', current: 5, minimum: 20, category: 'Soins' },
      { id: 2, name: 'Parfum Exclusif', current: 8, minimum: 15, category: 'Parfums' },
    ],
  };
  
  return mockDatabase[url];
}

// Export utilitaire pour le développement
if (IS_DEV) {
  api.dev = {
    setToken: (token) => {
      localStorage.setItem('auth_token', token);
      api.defaults.headers.Authorization = `Bearer ${token}`;
    },
    clearToken: () => {
      localStorage.removeItem('auth_token');
      delete api.defaults.headers.Authorization;
    },
    mock: (endpoint, data) => {
      console.log(`[DEV] Mocking ${endpoint} with:`, data);
      // Implémentation du mock si nécessaire
    },
  };
}

export default api;