// frontend\src\services\sales.js
import api from './api';

export const saleService = {
  // Get all sales
  async getSales(params = {}) {
    const response = await api.get('/sales', { params });
    return response.data;
  },

  // Get sale by ID
  async getSaleById(id) {
    const response = await api.get(`/sales/${id}`);
    return response.data;
  },

  // Create sale
  async createSale(saleData) {
    const response = await api.post('/sales', saleData);
    return response.data;
  },

  // Update sale
  async updateSale(id, saleData) {
    const response = await api.put(`/sales/${id}`, saleData);
    return response.data;
  },

  // Get refundable items
  async getRefundableItems(saleId) {
    const response = await api.get(`/sales/${saleId}/refundable-items`);
    return response.data;
  },

  // Create refund
  async createRefund(saleId, refundData) {
    const response = await api.post(`/sales/${saleId}/refunds/`, refundData);
    return response.data;
  },

  // Get refunds
  async getRefunds(params = {}) {
    const response = await api.get('/sales/refunds/', { params });
    return response.data;
  },

  // Get refund details
  async getRefundDetails(refundId) {
    const response = await api.get(`/sales/refunds/${refundId}`);
    return response.data;
  },

  // Approve refund
  async approveRefund(refundId, data) {
    const response = await api.put(`/sales/refunds/${refundId}/approve`, data);
    return response.data;
  },

  // Process refund
  async processRefund(refundId, data) {
    const response = await api.put(`/sales/refunds/${refundId}/process`, data);
    return response.data;
  },

  // Get daily sales
  async getDailySales() {
    const response = await api.get('/sales/performance/daily');
    return response.data;
  },

  // Get sales period analysis
  async getSalesAnalysis(startDate, endDate) {
    const response = await api.get('/sales/period-analysis', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },

  // Get refund statistics
  async getRefundStats(params = {}) {
    const response = await api.get('/sales/refund-stats', { params });
    return response.data;
  },

  // Generate invoice PDF
  async generateInvoice(saleId) {
    const response = await api.get(`/sales/${saleId}/invoice`, {
      responseType: 'blob',
    });
    return response.data;
  },
};