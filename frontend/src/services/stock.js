import api from './api';

export const stockService = {
  /**
   * Récupère tous les mouvements de stock
   */
  async getStockMovements(params = {}) {
    const response = await api.get('/stock/movements/', { params });
    return response.data;
  },

  /**
   * Crée un nouveau mouvement de stock
   */
  async createStockMovement(movementData) {
    const response = await api.post('/stock/movements/', movementData);
    return response.data;
  },

  /**
   * Récupère les alertes de stock
   */
  async getStockAlerts() {
    const response = await api.get('/stock/alerts/');
    return response.data;
  },

  /**
   * Récupère les statistiques de stock
   */
  async getStockStats() {
    // Utilise l'endpoint dashboard pour les stats
    const response = await api.get('/dashboard/stats');
    return response.data;
  },

  /**
   * Récupère l'historique des mouvements par produit
   */
  async getProductStockHistory(productId, params = {}) {
    const response = await api.get(`/products/${productId}/movements`, { params });
    return response.data;
  },

  /**
   * Récupère les produits avec stock faible
   */
  async getLowStockProducts(thresholdPercentage = 0.3) {
    const response = await api.get('/dashboard/inventory-alerts', {
      params: { threshold_percentage: thresholdPercentage }
    });
    return response.data;
  },

  /**
   * Met à jour le stock d'un produit
   */
  async updateProductStock(productId, quantity, movementType, reason = '') {
    const movementData = {
      product_id: productId,
      movement_type: movementType,
      quantity: quantity,
      reason: reason,
      movement_date: new Date().toISOString()
    };
    return this.createStockMovement(movementData);
  },

  /**
   * Récupère les produits expirant bientôt
   */
  async getExpiringProducts(days = 30) {
    // Cette fonctionnalité pourrait être ajoutée au backend
    // Pour l'instant, nous filtrons côté frontend
    const products = await this.getAllProductsWithStock();
    const today = new Date();
    const expiryDate = new Date();
    expiryDate.setDate(today.getDate() + days);
    
    return products.filter(product => {
      if (!product.expiration_date) return false;
      const expDate = new Date(product.expiration_date);
      return expDate <= expiryDate && expDate >= today;
    });
  },

  /**
   * Récupère tous les produits avec leur stock actuel
   */
  async getAllProductsWithStock() {
    const response = await api.get('/products/', {
      params: { include_inactive: false }
    });
    return response.data;
  },

  /**
   * Génère un rapport de stock
   */
  async generateStockReport(format = 'pdf') {
    const response = await api.get('/reports/stock', {
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  },

  /**
   * Importe un fichier CSV de stock
   */
  async importStockCSV(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/stock/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Exporte les données de stock en CSV
   */
  async exportStockCSV() {
    const response = await api.get('/stock/export', {
      responseType: 'blob'
    });
    return response.data;
  }
};

export default stockService;