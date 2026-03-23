import api from './api';
import { format } from 'date-fns';

/**
 * Service pour la gestion comptable
 * Correspond aux endpoints de /routes/accounting.py
 */
export const accountingService = {
  // ==================== DÉPENSES ====================
  /**
   * Récupère la liste des dépenses avec filtres optionnels
   */
  async getExpenses(params = {}) {
    const response = await api.get('/accounting/expenses/', { params });
    return response.data;
  },

  /**
   * Récupère une dépense par ID
   */
  async getExpenseById(id) {
    const response = await api.get(`/accounting/expenses/${id}`);
    return response.data;
  },

  /**
   * Crée une nouvelle dépense
   */
  async createExpense(data) {
    const response = await api.post('/accounting/expenses/', data);
    return response.data;
  },

  /**
   * Met à jour une dépense existante
   */
  async updateExpense(id, data) {
    const response = await api.put(`/accounting/expenses/${id}`, data);
    return response.data;
  },

  /**
   * Supprime une dépense
   */
  async deleteExpense(id) {
    const response = await api.delete(`/accounting/expenses/${id}`);
    return response.data;
  },

  // ==================== ANALYSE FINANCIÈRE ====================
  /**
   * Analyse de profitabilité sur une période
   * @param {string} startDate - Date de début (YYYY-MM-DD)
   * @param {string} endDate - Date de fin (YYYY-MM-DD)
   */
  async getProfitAnalysis(startDate, endDate) {
    const response = await api.get('/accounting/profit-analysis', {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  },

  /**
   * Flux de trésorerie quotidien sur une période
   */
  async getCashFlow(startDate, endDate) {
    const response = await api.get('/accounting/cash-flow', {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  },

  /**
   * Génère un rapport financier (income_statement, balance_sheet, sales_summary)
   */
  async getFinancialReport(reportType, startDate, endDate) {
    const response = await api.get(`/accounting/financial-reports/${reportType}`, {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  },

  /**
   * Métriques financières pour le dashboard (quotidien, mensuel, annuel)
   */
  async getFinancialMetrics() {
    const response = await api.get('/accounting/dashboard/financial-metrics');
    return response.data;
  },

  // ==================== PAIEMENTS ====================
  /**
   * Enregistre un paiement (vente, dépense, etc.)
   */
  async recordPayment(data) {
    const response = await api.post('/accounting/payments/', data);
    return response.data;
  },

  /**
   * Réconciliation des paiements sur une période
   */
  async reconcilePayments(startDate, endDate) {
    const response = await api.get('/accounting/payments/reconciliation', {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  },

  // ==================== UTILITAIRES ====================
  /**
   * Exporte les données de dépenses au format CSV/Excel
   * (à implémenter côté backend si nécessaire, sinon ici)
   */
  async exportExpenses(params = {}) {
    const response = await api.get('/accounting/expenses/export', {
      params,
      responseType: 'blob'
    });
    return response.data;
  }
};

export default accountingService;