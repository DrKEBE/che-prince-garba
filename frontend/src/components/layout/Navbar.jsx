// frontend\src\components\layout\Navbar.jsx
import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Badge,
  Box,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  ListItemIcon,
  ListItemText,
  InputBase,
  Tooltip,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Brightness4,
  Brightness7,
  Dashboard,
  Inventory2,
  PointOfSale,
  People,
  Warehouse,
  ReceiptLong,
  CalendarToday,
  Factory,
  AddShoppingCart,
  Add,
  PersonAdd,
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import { useApp, useNotifications, useTheme as useAppTheme, useSidebar } from '../../context/AppContext';
import { THEME_COLORS, ROLES } from '../../constants/config';

const Navbar = () => {
  const theme = useTheme();
  const { user, logout } = useAuth();
  const { mode, toggleTheme } = useAppTheme();
  const { toggleSidebar } = useSidebar();
  const { notifications, unreadCount, markAllAsRead } = useNotifications();
  
  const [anchorElUser, setAnchorElUser] = useState(null);
  const [anchorElNotifications, setAnchorElNotifications] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleOpenUserMenu = (event) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };

  const handleOpenNotifications = (event) => {
    setAnchorElNotifications(event.currentTarget);
  };

  const handleCloseNotifications = () => {
    setAnchorElNotifications(null);
  };

  const handleLogout = () => {
    logout();
    handleCloseUserMenu();
  };

  const handleSearch = (e) => {
    e.preventDefault();
    console.log('Searching for:', searchQuery);
    // TODO: Implement search functionality
  };

  const getNavIcon = (path) => {
    const icons = {
      '/': <Dashboard />,
      '/products': <Inventory2 />,
      '/sales': <PointOfSale />,
      '/clients': <People />,
      '/stock': <Warehouse />,
      '/accounting': <ReceiptLong />,
      '/appointments': <CalendarToday />,
      '/suppliers': <Factory />,
    };
    return icons[path] || <Dashboard />;
  };

  const getRoleBadgeColor = (role) => {
    const colors = {
      [ROLES.ADMIN]: '#EF4444',
      [ROLES.MANAGER]: '#3B82F6',
      [ROLES.CASHIER]: '#10B981',
      [ROLES.STOCK_MANAGER]: '#F59E0B',
      [ROLES.BEAUTICIAN]: '#8A2BE2',
    };
    return colors[role] || '#6B7280';
  };

  const quickActions = [
    { label: 'Nouvelle vente', icon: <AddShoppingCart />, path: '/sales/new', roles: [ROLES.ADMIN, ROLES.MANAGER, ROLES.CASHIER] },
    { label: 'Nouveau produit', icon: <Add />, path: '/products/new', roles: [ROLES.ADMIN, ROLES.MANAGER, ROLES.STOCK_MANAGER] },
    { label: 'Nouveau client', icon: <PersonAdd />, path: '/clients/new', roles: [ROLES.ADMIN, ROLES.MANAGER, ROLES.CASHIER] },
  ];

  const userActions = [
    { label: 'Mon profil', icon: <PersonIcon />, onClick: () => console.log('Profile') },
    { label: 'Paramètres', icon: <SettingsIcon />, onClick: () => console.log('Settings') },
    { label: mode === 'dark' ? 'Mode clair' : 'Mode sombre', icon: mode === 'dark' ? <Brightness7 /> : <Brightness4 />, onClick: toggleTheme },
    { label: 'Déconnexion', icon: <LogoutIcon />, onClick: handleLogout },
  ];

  return (
    <AppBar 
      position="fixed" 
      sx={{ 
        zIndex: theme.zIndex.drawer + 1,
        background: `linear-gradient(135deg, ${THEME_COLORS.PRIMARY} 0%, ${THEME_COLORS.SECONDARY} 100%)`,
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
      }}
    >
      <Toolbar>
        {/* Menu Button */}
        <IconButton
          size="large"
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={toggleSidebar}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        {/* Logo */}
        <Typography
          variant="h6"
          noWrap
          component="div"
          sx={{
            mr: 4,
            fontWeight: 700,
            background: 'linear-gradient(45deg, #FFFFFF 30%, #FFD6FF 90%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            display: { xs: 'none', sm: 'block' },
          }}
        >
          💄 Luxe Beauté
        </Typography>

        {/* Quick Actions */}
        <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1, mr: 2 }}>
          {quickActions
            .filter(action => action.roles.includes(user?.role))
            .map((action) => (
              <Tooltip key={action.label} title={action.label}>
                <IconButton
                  size="small"
                  sx={{
                    bgcolor: alpha('#FFFFFF', 0.2),
                    '&:hover': { bgcolor: alpha('#FFFFFF', 0.3) },
                    color: 'white',
                  }}
                  onClick={() => console.log(`Navigate to ${action.path}`)}
                >
                  {action.icon}
                </IconButton>
              </Tooltip>
            ))}
        </Box>

        {/* Search Bar */}
        <Box
          component="form"
          onSubmit={handleSearch}
          sx={{
            display: { xs: 'none', md: 'flex' },
            flexGrow: 0.4,
            position: 'relative',
            borderRadius: theme.shape.borderRadius,
            backgroundColor: alpha(theme.palette.common.white, 0.15),
            '&:hover': {
              backgroundColor: alpha(theme.palette.common.white, 0.25),
            },
            marginLeft: 2,
            width: 'auto',
          }}
        >
          <Box sx={{ p: theme.spacing(0, 2), display: 'flex', alignItems: 'center' }}>
            <SearchIcon />
          </Box>
          <InputBase
            placeholder="Rechercher produit, client..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{
              color: 'inherit',
              width: '100%',
              '& .MuiInputBase-input': {
                padding: theme.spacing(1, 1, 1, 0),
              },
            }}
          />
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        {/* Notifications */}
        <IconButton
          size="large"
          aria-label="show notifications"
          color="inherit"
          onClick={handleOpenNotifications}
          sx={{ mr: 1 }}
        >
          <Badge badgeContent={unreadCount} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>

        <Menu
          anchorEl={anchorElNotifications}
          open={Boolean(anchorElNotifications)}
          onClose={handleCloseNotifications}
          PaperProps={{
            sx: {
              mt: 1.5,
              width: 320,
              maxHeight: 400,
              overflow: 'auto',
            },
          }}
        >
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Notifications</Typography>
            {notifications.length > 0 && (
              <Typography
                variant="body2"
                sx={{ color: 'primary.main', cursor: 'pointer' }}
                onClick={markAllAsRead}
              >
                Tout marquer comme lu
              </Typography>
            )}
          </Box>
          <Divider />
          {notifications.length > 0 ? (
            notifications.slice(0, 5).map((notification) => (
              <MenuItem key={notification.id} onClick={handleCloseNotifications}>
                <ListItemIcon>
                  <Badge color="error" variant="dot" invisible={notification.read}>
                    {notification.type === 'success' && '✅'}
                    {notification.type === 'error' && '❌'}
                    {notification.type === 'warning' && '⚠️'}
                    {notification.type === 'info' && 'ℹ️'}
                  </Badge>
                </ListItemIcon>
                <ListItemText
                  primary={notification.title}
                  secondary={notification.message}
                  primaryTypographyProps={{
                    sx: { fontWeight: notification.read ? 'normal' : 'bold' },
                  }}
                />
              </MenuItem>
            ))
          ) : (
            <MenuItem disabled>
              <ListItemText primary="Aucune notification" />
            </MenuItem>
          )}
        </Menu>

        {/* User Profile */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Paramètres du compte">
            <IconButton
              onClick={handleOpenUserMenu}
              sx={{ 
                p: 0,
                border: `2px solid ${alpha('#FFFFFF', 0.3)}`,
                '&:hover': { borderColor: alpha('#FFFFFF', 0.5) },
              }}
            >
              <Avatar
                alt={user?.name || 'Utilisateur'}
                src={user?.avatar_url}
                sx={{
                  bgcolor: getRoleBadgeColor(user?.role),
                  width: 40,
                  height: 40,
                }}
              >
                {user?.name?.charAt(0) || 'U'}
              </Avatar>
            </IconButton>
          </Tooltip>
          
          <Box sx={{ display: { xs: 'none', md: 'flex' }, flexDirection: 'column' }}>
            <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>
              {user?.name || 'Utilisateur'}
            </Typography>
            <Typography variant="caption" sx={{ color: alpha('#FFFFFF', 0.8) }}>
              {user?.role || 'Non défini'}
            </Typography>
          </Box>
        </Box>

        <Menu
          anchorEl={anchorElUser}
          open={Boolean(anchorElUser)}
          onClose={handleCloseUserMenu}
          PaperProps={{
            sx: {
              mt: 1.5,
              minWidth: 200,
            },
          }}
        >
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Avatar
              alt={user?.name}
              src={user?.avatar_url}
              sx={{
                width: 60,
                height: 60,
                mx: 'auto',
                mb: 1,
                bgcolor: getRoleBadgeColor(user?.role),
              }}
            />
            <Typography variant="subtitle1" fontWeight="bold">
              {user?.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {user?.email}
            </Typography>
            <Box
              sx={{
                mt: 1,
                px: 1,
                py: 0.5,
                bgcolor: alpha(getRoleBadgeColor(user?.role), 0.1),
                borderRadius: 1,
                display: 'inline-block',
              }}
            >
              <Typography variant="caption" color={getRoleBadgeColor(user?.role)}>
                {user?.role}
              </Typography>
            </Box>
          </Box>
          <Divider />
          {userActions.map((action) => (
            <MenuItem key={action.label} onClick={action.onClick}>
              <ListItemIcon>{action.icon}</ListItemIcon>
              <ListItemText>{action.label}</ListItemText>
            </MenuItem>
          ))}
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;