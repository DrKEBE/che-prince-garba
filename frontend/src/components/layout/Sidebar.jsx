// frontend\src\components\layout\Sidebar.jsx
import React, { useState } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  IconButton,
  Divider,
  Box,
  Avatar,
  Typography,
  Badge,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Inventory as InventoryIcon,
  ShoppingCart as ShoppingCartIcon,
  Assignment as AssignmentIcon,
  LocalShipping as LocalShippingIcon,
  AccountBalance as AccountBalanceIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useSidebar } from '../../context/AppContext';
import { useQuery } from 'react-query';
import api from '../../services/api';

const drawerWidth = 240;
const collapsedDrawerWidth = 72;

const Sidebar = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user, logout } = useAuth();
  const { open, toggleSidebar, closeSidebar } = useSidebar();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false); // optionnel pour desktop


  // Définition des éléments de navigation selon le rôle
  const navItems = [
    { text: 'Tableau de bord', path: '/dashboard', icon: <DashboardIcon />, roles: ['ADMIN', 'MANAGER', 'CASHIER'] },
    { text: 'Ventes', path: '/sales', icon: <ShoppingCartIcon />, roles: ['ADMIN', 'MANAGER', 'CASHIER'] },
    { text: 'Clients', path: '/clients', icon: <PeopleIcon />, roles: ['ADMIN', 'MANAGER', 'CASHIER'] },
    { text: 'Produits', path: '/products', icon: <InventoryIcon />, roles: ['ADMIN', 'MANAGER'] },
    { text: 'Comptabilité', path: '/accounting', icon: <AccountBalanceIcon />, roles: ['ADMIN'] },
    { text: 'Paramètres', path: '/settings', icon: <SettingsIcon />, roles: ['ADMIN'] },
  ];
  // Filtrer selon le rôle de l'utilisateur
  const filteredItems = navItems.filter(item =>
    item.roles.includes(user?.role || 'user')
  );

  // Gestion de la fermeture sur mobile
  const handleItemClick = () => {
    if (isMobile) {
      closeSidebar();
    }
  };

  const handleLogout = () => {
    logout();
  };

  // Rendu du contenu du drawer
  const drawerContent = (
    <>
      <Toolbar sx={{ justifyContent: collapsed && !isMobile ? 'center' : 'space-between', px: 1 }}>
        {!collapsed && !isMobile && (
          <Typography variant="h6" sx={{ color: 'primary.main', fontWeight: 600 }}>
            Prince Garba
          </Typography>
        )}
        {!isMobile && (
          <IconButton onClick={() => setCollapsed(!collapsed)} edge="end">
            {collapsed ? <MenuIcon /> : <ChevronLeftIcon />}
          </IconButton>
        )}
      </Toolbar>
      <Divider />
      <List sx={{ flexGrow: 1, px: 1 }}>
        {filteredItems.map((item) => {
          const isActive = location.pathname.startsWith(item.path);
          return (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                component={NavLink}
                to={item.path}
                onClick={handleItemClick}
                selected={isActive}
                sx={{
                  minHeight: 48,
                  justifyContent: collapsed ? 'center' : 'initial',
                  borderRadius: 1,
                  '&.Mui-selected': {
                    backgroundColor: theme.palette.primary.light + '20',
                    color: theme.palette.primary.main,
                    '& .MuiListItemIcon-root': {
                      color: theme.palette.primary.main,
                    },
                  },
                  '&:hover': {
                    backgroundColor: theme.palette.action.hover,
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: collapsed ? 'auto' : 2,
                    justifyContent: 'center',
                    color: isActive ? theme.palette.primary.main : 'inherit',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {!collapsed && <ListItemText primary={item.text} />}
                {item.text === 'Stock' && lowStockCount > 0 && collapsed && (
                  <Badge badgeContent={lowStockCount} color="error" sx={{ position: 'absolute', top: 8, right: 8 }} />
                )}
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
      <Divider />
      <Box sx={{ p: collapsed ? 1 : 2, display: 'flex', alignItems: 'center', justifyContent: collapsed ? 'center' : 'space-between' }}>
        {!collapsed ? (
          <>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
                {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
              </Avatar>
              <Box>
                <Typography variant="subtitle2" noWrap>
                  {user?.full_name || user?.username}
                </Typography>
                <Typography variant="caption" color="text.secondary" noWrap>
                  {user?.role}
                </Typography>
              </Box>
            </Box>
            <IconButton onClick={handleLogout} size="small">
              <LogoutIcon fontSize="small" />
            </IconButton>
          </>
        ) : (
          <IconButton onClick={handleLogout} size="small">
            <LogoutIcon />
          </IconButton>
        )}
      </Box>
    </>
  );

  return (
    <Box
      component="nav"
      sx={{ width: { sm: open ? (collapsed ? collapsedDrawerWidth : drawerWidth) : 0 }, flexShrink: { sm: 0 } }}
    >
      {/* Drawer permanent pour desktop */}
      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? open : true}
        onClose={closeSidebar}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', sm: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: open ? (collapsed ? collapsedDrawerWidth : drawerWidth) : 0,
            transition: theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
            overflowX: 'hidden',
            borderRight: '1px solid',
            borderColor: theme.palette.divider,
          },
        }}
      >
        {drawerContent}
      </Drawer>
    </Box>
  );
};

export default Sidebar;