// frontend/src/services/products.js
import api from './api';

export const productService = {
  // Get all products
  async getProducts(params = {}) {
    const response = await api.get('/products/', { params });
    return response.data;
  },

  // Get product by ID
  async getProductById(id) {
    const response = await api.get(`/products/${id}`);
    return response.data;
  },

  // Create product
  async createProduct(productData) {
    const response = await api.post('/products/', productData);
    return response.data;
  },

  // Update product
  async updateProduct(id, productData) {
    const response = await api.put(`/products/${id}`, productData);
    return response.data;
  },

  // Delete product
  async deleteProduct(id) {
    await api.delete(`/products/${id}`);
  },

  // Search products
  async searchProducts(searchParams) {
    const response = await api.get('/products/', { params: searchParams });
    return response.data;
  },

  // Get low stock products
  async getLowStockProducts() {
    const response = await api.get('/dashboard/inventory-alerts');
    return response.data;
  },

  // Update stock
  async updateStock(movementData) {
    const response = await api.post('/stock/movements/', movementData);
    return response.data;
  },

  // Get product statistics
  async getProductStats(productId) {
    const response = await api.get(`/products/${productId}/stats`);
    return response.data;
  },

  // Upload product image
  async uploadProductImage(productId, file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/products/${productId}/image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // Get product movements
  async getProductMovements(productId, params = {}) {
    const response = await api.get('/stock/movements/', {
      params: { product_id: productId, ...params }
    });
    return response.data;
  },

  // Create stock movement (alias for updateStock)
  async createStockMovement(movementData) {
    return this.updateStock(movementData);
  },

  // Get stock alerts
  async getStockAlerts() {
    const response = await api.get('/stock/alerts/');
    return response.data;
  },

  // Get product categories
  async getCategories() {
    const response = await api.get('/products/categories');
    return response.data;
  },

  // Get product brands
  async getBrands() {
    const response = await api.get('/products/brands');
    return response.data;
  },

  
  // Après les méthodes existantes, par exemple après getBrands
  async getProductStats() {
    const response = await api.get('/products/stats');
    return response.data;
  },

  async getProductMovementStats(productId) {
    const response = await api.get(`/products/${productId}/movements/stats`);
    return response.data;
  },

    // Bulk update products
    async bulkUpdateProducts(updates) {
      const response = await api.put('/products/bulk', updates);
      return response.data;
    },
  };