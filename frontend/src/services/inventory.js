import api from './api';

/**
 * Service unifié pour la gestion d'inventaire :
 * - Produits
 * - Mouvements de stock
 * - Fournisseurs
 * - Commandes fournisseurs
 * - Alertes & rapports
 */
export const inventoryService = {
  // ============================
  // TABLEAU DE BORD INVENTAIRE
  // ============================
  async getDashboardStats() {
    const response = await api.get('/inventory/dashboard');
    return response.data;
  },

  // ============================
  // PRODUITS
  // ============================
  async getProducts(params = {}) {
    const response = await api.get('/inventory/products', { params });
    return response.data;
  },

  async getProductById(id) {
    const response = await api.get(`/inventory/products/${id}`);
    return response.data;
  },

  async createProduct(productData, supplierId = null) {
    const params = supplierId ? { supplier_id: supplierId } : {};
    const response = await api.post('/inventory/products', productData, { params });
    return response.data;
  },

  async updateProduct(id, productData) {
    const response = await api.put(`/inventory/products/${id}`, productData);
    return response.data;
  },

  async deleteProduct(id) {
    const response = await api.delete(`/inventory/products/${id}`);
    return response.data;
  },

  async uploadProductImage(productId, file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(
      `/inventory/products/${productId}/image`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  // ============================
  // MOUVEMENTS DE STOCK
  // ============================
  async createStockMovement(movementData) {
    const response = await api.post('/inventory/stock/movements', movementData);
    return response.data;
  },

  async getStockMovements(params = {}) {
    const response = await api.get('/inventory/stock/movements', { params });
    return response.data;
  },

  async getProductStockHistory(productId, days = 30) {
    const response = await api.get(`/inventory/products/${productId}/stock-history`, {
      params: { days },
    });
    return response.data;
  },

  // ============================
  // FOURNISSEURS
  // ============================
  async getSuppliers(params = {}) {
    const response = await api.get('/inventory/suppliers', { params });
    return response.data;
  },

  async getSupplierById(id, withStats = false) {
    const response = await api.get(`/inventory/suppliers/${id}`, {
      params: { with_stats: withStats },
    });
    return response.data;
  },

  async createSupplier(supplierData) {
    const response = await api.post('/inventory/suppliers', supplierData);
    return response.data;
  },

  async updateSupplier(id, supplierData) {
    const response = await api.put(`/inventory/suppliers/${id}`, supplierData);
    return response.data;
  },

  async deleteSupplier(id) {
    const response = await api.delete(`/inventory/suppliers/${id}`);
    return response.data;
  },

  async getSupplierProducts(supplierId, activeOnly = true) {
    const response = await api.get(`/inventory/suppliers/${supplierId}/products`, {
      params: { active_only: activeOnly },
    });
    return response.data;
  },

  // ============================
  // COMMANDES FOURNISSEURS
  // ============================
  async createPurchaseOrder(orderData) {
    const response = await api.post('/inventory/purchase-orders', orderData);
    return response.data;
  },

  async receivePurchaseOrder(orderId, items) {
    const response = await api.post(`/inventory/purchase-orders/${orderId}/receive`, { items });
    return response.data;
  },

  // ============================
  // ALERTES & RAPPORTS
  // ============================
  async getLowStockAlerts(thresholdPercentage = 0.3, limit = 50) {
    const response = await api.get('/inventory/alerts/low-stock', {
      params: { threshold_percentage: thresholdPercentage, limit },
    });
    return response.data;
  },

  async getOutOfStockAlerts(limit = 50) {
    const response = await api.get('/inventory/alerts/out-of-stock', {
      params: { limit },
    });
    return response.data;
  },

  async getStockValueReport(byCategory = false, bySupplier = false) {
    const response = await api.get('/inventory/reports/stock-value', {
      params: { by_category: byCategory, by_supplier: bySupplier },
    });
    return response.data;
  },

  async getStockTurnoverReport(days = 90) {
    const response = await api.get('/inventory/reports/stock-turnover', {
      params: { days },
    });
    return response.data;
  },
};

export default inventoryService;