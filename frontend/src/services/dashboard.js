// frontend\src\services\dashboard.js
import api from './api';

export const dashboardService = {
      // Get sales trend with enhanced parameters
  async getSalesTrend(days = 30, groupBy = 'day') {
    const response = await api.get('/dashboard/sales-trend', {
      params: { days, group_by: groupBy },
    });
    return response.data;
  },
  // Get dashboard statistics
  async getStats() {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },

  // Get sales trend
  async getSalesTrend(days = 30, groupBy = 'day') {
    const response = await api.get('/dashboard/sales-trend', {
      params: { days, group_by: groupBy },
    });
    return response.data;
  },

  // Get top products
  async getTopProducts(limit = 10, days = 30, sortBy = 'revenue') {
    const response = await api.get('/dashboard/top-products', {
      params: { limit, days, sort_by: sortBy },
    });
    return response.data;
  },

  // Get client insights
  async getClientInsights(limit = 10, days = 90) {
    const response = await api.get('/dashboard/client-insights', {
      params: { limit, days },
    });
    return response.data;
  },

  // Get inventory alerts
  async getInventoryAlerts(thresholdPercentage = 0.3) {
    const response = await api.get('/dashboard/inventory-alerts', {
      params: { threshold_percentage: thresholdPercentage },
    });
    return response.data;
  },

  // Get performance metrics
  async getPerformanceMetrics(period = 'month') {
    const response = await api.get('/dashboard/performance-metrics', {
      params: { period },
    });
    return response.data;
  },

  // Get realtime updates
  async getRealtimeUpdates() {
    const response = await api.get('/dashboard/realtime-updates');
    return response.data;
  },

  // Get financial metrics
  async getFinancialMetrics() {
    const response = await api.get('/accounting/dashboard/financial-metrics');
    return response.data;
  },

  // Get sales summary
  async getSalesSummary(startDate, endDate) {
    const response = await api.get('/accounting/financial-reports/sales_summary', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },

  // Get profit analysis
  async getProfitAnalysis(startDate, endDate) {
    const response = await api.get('/accounting/profit-analysis', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },

  // Get cash flow
  async getCashFlow(startDate, endDate) {
    const response = await api.get('/accounting/cash-flow', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },
};