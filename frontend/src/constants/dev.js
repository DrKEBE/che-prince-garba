// frontend/src/constants/dev.js
// Configuration pour le développement
const devConfig = {
  enabled: import.meta.env.VITE_DEV_MODE === 'true',
  
  // Tokens de développement par rôle
  tokens: {
    admin: 'fake-token-admin',
    manager: 'fake-token-manager',
    cashier: 'fake-token-cashier',
    stock: 'fake-token-stock'
  },
  
  // Utilisateurs de développement
  users: {
    1: { id: 1, username: 'admin', role: 'ADMIN', full_name: 'Administrateur' },
    2: { id: 2, username: 'manager', role: 'MANAGER', full_name: 'Manager' },
    3: { id: 3, username: 'cashier', role: 'CASHIER', full_name: 'Caissier' }
  },
  
  // Routes exemptées (pour logs)
  exemptRoutes: [
    '/api/v1/dashboard/stats',
    '/api/v1/dashboard/sales-trend',
    '/api/v1/dashboard/inventory-alerts'
  ],
  
  // URLs utiles
  endpoints: {
    devInfo: '/api/v1/dev/info',
    devToken: '/api/v1/dev/auth/token'
  }
};

export default devConfig;