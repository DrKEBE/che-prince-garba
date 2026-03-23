// src/routes.jsx - VERSION CORRIGÉE
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Layout
import Layout from './components/layout/Layout';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Sales from './pages/Sales';
import Clients from './pages/Clients';
import Stock from './pages/Stock';
import Accounting from './pages/Accounting';
import Appointments from './pages/Appointments';
import Suppliers from './pages/Suppliers';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Chargement...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      {/* Routes protégées */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* Ces routes s'afficheront dans <Outlet /> de Layout */}
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="products" element={<Products />} />
        <Route path="sales" element={<Sales />} />
        <Route path="clients" element={<Clients />} />
        <Route path="stock" element={<Stock />} />
        <Route path="accounting" element={<Accounting />} />
        <Route path="appointments" element={<Appointments />} />
        <Route path="suppliers" element={<Suppliers />} />
      </Route>
      
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}