import React, { useState, useEffect } from 'react';
import { DEV_CONFIG } from '../../constants/config';
import api from '../../services/api';

const DevPanel = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [systemInfo, setSystemInfo] = useState(null);
  const [selectedRole, setSelectedRole] = useState('admin');

  if (!DEV_CONFIG.IS_DEV) return null;

  const roles = [
    { value: 'admin', label: 'Admin' },
    { value: 'manager', label: 'Manager' },
    { value: 'cashier', label: 'Cashier' },
    { value: 'stock', label: 'Stock Manager' }
  ];

  const tokens = {
    admin: 'fake-token-admin',
    manager: 'fake-token-manager',
    cashier: 'fake-token-cashier',
    stock: 'fake-token-stock'
  };

  const handleRoleChange = (role) => {
    setSelectedRole(role);
    const token = tokens[role];
    window.devApi?.setToken(token);
    localStorage.setItem('auth_token', token);
    
    // Simuler un utilisateur
    const users = {
      admin: { id: 1, username: 'admin', role: 'ADMIN', full_name: 'Admin Dev' },
      manager: { id: 2, username: 'manager', role: 'MANAGER', full_name: 'Manager Dev' },
      cashier: { id: 3, username: 'cashier', role: 'CASHIER', full_name: 'Cashier Dev' },
      stock: { id: 4, username: 'stock', role: 'STOCK_MANAGER', full_name: 'Stock Dev' }
    };
    
    localStorage.setItem('user', JSON.stringify(users[role]));
    window.location.reload();
  };

  const fetchSystemInfo = async () => {
    try {
      const response = await api.get('/dev/system-info');
      setSystemInfo(response.data);
    } catch (error) {
      console.error('Erreur récupération info système:', error);
    }
  };

  const testAuth = async () => {
    try {
      const response = await api.get('/dev/auth-test');
      alert(`Test auth réussi:\n${JSON.stringify(response.data, null, 2)}`);
    } catch (error) {
      alert(`Erreur auth: ${error.message}`);
    }
  };

  return (
    <>
      {/* Bouton de toggle */}
      <button
        onClick={() => setIsVisible(!isVisible)}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          zIndex: 9999,
          background: '#8A2BE2',
          color: 'white',
          border: 'none',
          borderRadius: '50%',
          width: '50px',
          height: '50px',
          cursor: 'pointer',
          fontSize: '24px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.3)'
        }}
        title="Panel de développement"
      >
        {isVisible ? '×' : '⚙️'}
      </button>

      {/* Panel */}
      {isVisible && (
        <div style={{
          position: 'fixed',
          bottom: '80px',
          right: '20px',
          zIndex: 9998,
          background: 'white',
          border: '1px solid #ccc',
          borderRadius: '8px',
          padding: '20px',
          width: '300px',
          maxHeight: '80vh',
          overflow: 'auto',
          boxShadow: '0 4px 20px rgba(0,0,0,0.2)'
        }}>
          <h3 style={{ marginTop: 0 }}>🔧 Panel Développement</h3>
          
          <div style={{ marginBottom: '15px' }}>
            <strong>Mode:</strong> {DEV_CONFIG.DEV_BYPASS_AUTH ? 'BYPASS AUTH' : 'NORMAL'}
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <label>Rôle de test:</label>
            <select 
              value={selectedRole}
              onChange={(e) => handleRoleChange(e.target.value)}
              style={{ width: '100%', padding: '5px', marginTop: '5px' }}
            >
              {roles.map(role => (
                <option key={role.value} value={role.value}>
                  {role.label}
                </option>
              ))}
            </select>
          </div>
          
          <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
            <button 
              onClick={testAuth}
              style={{ flex: 1, padding: '8px', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px' }}
            >
              Test Auth
            </button>
            <button 
              onClick={fetchSystemInfo}
              style={{ flex: 1, padding: '8px', background: '#2196F3', color: 'white', border: 'none', borderRadius: '4px' }}
            >
              System Info
            </button>
          </div>
          
          {systemInfo && (
            <div style={{ 
              background: '#f5f5f5', 
              padding: '10px', 
              borderRadius: '4px',
              fontSize: '12px',
              marginTop: '10px'
            }}>
              <pre>{JSON.stringify(systemInfo, null, 2)}</pre>
            </div>
          )}
          
          <div style={{ marginTop: '15px', fontSize: '12px', color: '#666' }}>
            <div>Token actuel: {tokens[selectedRole]}</div>
            <div>User ID: {DEV_CONFIG.DEV_USER_ID}</div>
            <div>Base URL: {API_CONFIG.BASE_URL}</div>
          </div>
        </div>
      )}
    </>
  );
};

export default DevPanel;