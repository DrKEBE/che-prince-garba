
// frontend\src\hooks\useAuth.js
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

/**
 * Custom hook to use auth context
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

/**
 * Hook to check if user has required role
 */
export const useHasRole = (requiredRole) => {
  const { user } = useAuth();
  
  if (!user) return false;
  
  if (Array.isArray(requiredRole)) {
    return requiredRole.includes(user.role);
  }
  
  return user.role === requiredRole;
};

/**
 * Hook to check if user has any of the required roles
 */
export const useHasAnyRole = (requiredRoles) => {
  const { user } = useAuth();
  
  if (!user || !requiredRoles || !Array.isArray(requiredRoles)) {
    return false;
  }
  
  return requiredRoles.includes(user.role);
};

/**
 * Hook to get user permissions
 */
export const usePermissions = () => {
  const { user } = useAuth();
  
  if (!user) return [];
  
  // Default permissions based on role
  const rolePermissions = {
    ADMIN: [
      'view_dashboard',
      'manage_products',
      'manage_sales',
      'manage_clients',
      'manage_stock',
      'manage_accounting',
      'manage_users',
      'view_reports',
      'export_data',
      'manage_settings',
    ],
    MANAGER: [
      'view_dashboard',
      'manage_products',
      'manage_sales',
      'manage_clients',
      'manage_stock',
      'manage_accounting',
      'view_reports',
      'export_data',
    ],
    CASHIER: [
      'view_dashboard',
      'manage_sales',
      'manage_clients',
      'view_products',
      'view_reports',
    ],
    STOCK_MANAGER: [
      'view_dashboard',
      'manage_products',
      'manage_stock',
      'view_sales',
      'view_reports',
    ],
    BEAUTICIAN: [
      'view_dashboard',
      'manage_appointments',
      'view_clients',
      'view_products',
    ],
  };
  
  return rolePermissions[user.role] || [];
};

/**
 * Hook to check if user has specific permission
 */
export const useHasPermission = (permission) => {
  const permissions = usePermissions();
  return permissions.includes(permission);
};