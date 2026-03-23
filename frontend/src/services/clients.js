// frontend\src\services\clients.js
import api from './api';

export const clientService = {
  // Get all clients
  async getClients(params = {}) {
    const response = await api.get('/clients/', { params }); // <-- slash ajouté
    return response.data;
  },

  // Get client by ID
  async getClientById(id) {
    const response = await api.get(`/clients/${id}/`); // <-- slash ajouté
    return response.data;
  },

  // Create client
  async createClient(clientData) {
    const response = await api.post('/clients/', clientData); // <-- slash ajouté
    return response.data;
  },

  // Update client
  async updateClient(id, clientData) {
    const response = await api.put(`/clients/${id}/`, clientData); // <-- slash ajouté
    return response.data;
  },

  // Delete client
  async deleteClient(id) {
    await api.delete(`/clients/${id}/`); // <-- slash ajouté
  },

  // Search clients
  async searchClients(searchParams) {
    const response = await api.get('/clients/', { params: searchParams }); // <-- slash ajouté
    return response.data;
  },

  // Get client purchase history
  async getClientPurchaseHistory(id, days = 365) {
    const response = await api.get(`/clients/${id}/purchase-history/`, { // <-- slash ajouté
      params: { days },
    });
    return response.data;
  },

  // Get top clients
  async getTopClients(limit = 10, periodDays = 30) {
    const response = await api.get('/clients/stats/top-clients', { // <-- slash ajouté
      params: { limit, period_days: periodDays },
    });
    return response.data;
  },

  // Get client stats
  async getClientStats(id) {
    const response = await api.get(`/clients/${id}/stats`); // <-- slash ajouté
    return response.data;
  },
};