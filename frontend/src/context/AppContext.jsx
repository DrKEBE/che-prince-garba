// frontend/src/context/AppContext.jsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const AppContext = createContext({});

export const useApp = () => useContext(AppContext);

export const AppProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [themeMode, setThemeMode] = useState('light');
  const [searchHistory, setSearchHistory] = useState([]);
  const [recentItems, setRecentItems] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const location = useLocation();

  // Load saved preferences from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('themeMode');
    const savedFavorites = localStorage.getItem('favorites');
    const savedSearchHistory = localStorage.getItem('searchHistory');
    const savedRecentItems = localStorage.getItem('recentItems');

    if (savedTheme) setThemeMode(savedTheme);
    if (savedFavorites) setFavorites(JSON.parse(savedFavorites));
    if (savedSearchHistory) setSearchHistory(JSON.parse(savedSearchHistory));
    if (savedRecentItems) setRecentItems(JSON.parse(savedRecentItems));
  }, []);

  // Save preferences to localStorage
  useEffect(() => {
    localStorage.setItem('themeMode', themeMode);
    localStorage.setItem('favorites', JSON.stringify(favorites));
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
    localStorage.setItem('recentItems', JSON.stringify(recentItems));
  }, [themeMode, favorites, searchHistory, recentItems]);

  // Track recent pages
  useEffect(() => {
    const path = location.pathname;
    if (path !== '/' && !path.includes('/login')) {
      const pageName = getPageName(path);
      
      setRecentItems(prev => {
        const filtered = prev.filter(item => item.path !== path);
        const updated = [
          { path, name: pageName, timestamp: new Date().toISOString() },
          ...filtered.slice(0, 9), // Keep last 10 items
        ];
        return updated;
      });
    }
  }, [location]);

  const getPageName = (path) => {
    const pages = {
      '/': 'Tableau de bord',
      '/products': 'Produits',
      '/sales': 'Ventes',
      '/clients': 'Clients',
      '/stock': 'Stock',
      '/accounting': 'Comptabilité',
      '/appointments': 'Rendez-vous',
      '/suppliers': 'Fournisseurs',
    };
    
    return pages[path] || 'Page inconnue';
  };

  const addNotification = (notification) => {
    const newNotification = {
      id: Date.now(),
      ...notification,
      timestamp: new Date().toISOString(),
      read: false,
    };
    
    setNotifications(prev => [newNotification, ...prev.slice(0, 49)]); // Keep last 50
  };

  const markNotificationAsRead = (id) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === id ? { ...notif, read: true } : notif
      )
    );
  };

  const markAllNotificationsAsRead = () => {
    setNotifications(prev =>
      prev.map(notif => ({ ...notif, read: true }))
    );
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  const addToSearchHistory = (query) => {
    if (!query.trim()) return;
    
    setSearchHistory(prev => {
      const filtered = prev.filter(item => item !== query);
      return [query, ...filtered.slice(0, 9)]; // Keep last 10
    });
  };

  const clearSearchHistory = () => {
    setSearchHistory([]);
  };

  const toggleFavorite = (item) => {
    setFavorites(prev => {
      const exists = prev.find(fav => fav.id === item.id && fav.type === item.type);
      
      if (exists) {
        return prev.filter(fav => !(fav.id === item.id && fav.type === item.type));
      } else {
        return [
          { ...item, addedAt: new Date().toISOString() },
          ...prev.slice(0, 49), // Keep last 50
        ];
      }
    });
  };

  const isFavorite = (id, type) => {
    return favorites.some(fav => fav.id === id && fav.type === type);
  };

  const toggleTheme = () => {
    setThemeMode(prev => (prev === 'light' ? 'dark' : 'light'));
  };

  const toggleSidebar = () => {
    setSidebarOpen(prev => !prev);
  };

  const value = {
    // State
    notifications,
    sidebarOpen,
    themeMode,
    searchHistory,
    recentItems,
    favorites,
    
    // Actions
    addNotification,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    removeNotification,
    clearNotifications,
    
    addToSearchHistory,
    clearSearchHistory,
    
    toggleFavorite,
    isFavorite,
    
    toggleTheme,
    toggleSidebar,
    
    // Derived values
    unreadNotifications: notifications.filter(n => !n.read).length,
    hasNotifications: notifications.length > 0,
    hasUnreadNotifications: notifications.some(n => !n.read),
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

// Custom hooks for specific contexts
export const useNotifications = () => {
  const context = useContext(AppContext);
  
  if (!context) {
    throw new Error('useNotifications must be used within AppProvider');
  }
  
  return {
    notifications: context.notifications,
    addNotification: context.addNotification,
    markAsRead: context.markNotificationAsRead,
    markAllAsRead: context.markAllNotificationsAsRead,
    removeNotification: context.removeNotification,
    clearNotifications: context.clearNotifications,
    unreadCount: context.unreadNotifications,
    hasNotifications: context.hasNotifications,
    hasUnread: context.hasUnreadNotifications,
  };
};

export const useTheme = () => {
  const context = useContext(AppContext);
  
  if (!context) {
    throw new Error('useTheme must be used within AppProvider');
  }
  
  return {
    mode: context.themeMode,
    toggleTheme: context.toggleTheme,
    isDark: context.themeMode === 'dark',
    isLight: context.themeMode === 'light',
  };
};

export const useFavorites = () => {
  const context = useContext(AppContext);
  
  if (!context) {
    throw new Error('useFavorites must be used within AppProvider');
  }
  
  return {
    favorites: context.favorites,
    toggleFavorite: context.toggleFavorite,
    isFavorite: context.isFavorite,
  };
};

export const useSidebar = () => {
  const context = useContext(AppContext);
  
  if (!context) {
    throw new Error('useSidebar must be used within AppProvider');
  }
  
  return {
    open: context.sidebarOpen,
    toggleSidebar: context.toggleSidebar,
  };
};
