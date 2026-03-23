//frontend\src\components\dashboard\InventoryAlerts.jsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Tabs,
  Tab,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  LinearProgress,
  Avatar,
  Badge,
  Grid,
  CardActions,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Inventory as InventoryIcon,
  Schedule as ScheduleIcon,
  TrendingUp as TrendingUpIcon,
  ShoppingCart as ShoppingCartIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
  ArrowForward as ArrowForwardIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { motion } from 'framer-motion';
import { dashboardService } from '../../services/dashboard';
import { formatDate, formatCurrency } from '../../utils/formatters';
import { STOCK_ALERT_LEVELS } from '../../constants/config';

// Alert item component
const AlertItem = ({ alert, type, onAcknowledge }) => {
  const theme = useTheme();
  
  const getSeverityInfo = () => {
    switch (type) {
      case 'RUPTURE':
        return {
          color: 'error',
          icon: <ErrorIcon />,
          label: 'Rupture de stock',
          bgColor: theme.palette.error.light + '20',
        };
      case 'ALERTE':
        const percentage = alert.percentage || 0;
        if (percentage <= STOCK_ALERT_LEVELS.CRITICAL * 100) {
          return {
            color: 'error',
            icon: <WarningIcon />,
            label: 'Stock critique',
            bgColor: theme.palette.error.light + '20',
          };
        } else if (percentage <= STOCK_ALERT_LEVELS.WARNING * 100) {
          return {
            color: 'warning',
            icon: <WarningIcon />,
            label: 'Stock faible',
            bgColor: theme.palette.warning.light + '20',
          };
        } else {
          return {
            color: 'info',
            icon: <InfoIcon />,
            label: 'Stock bas',
            bgColor: theme.palette.info.light + '20',
          };
        }
      case 'EXPIRE':
        const daysRemaining = alert.days_until_expiry || 0;
        if (daysRemaining <= 50) {
          return {
            color: 'error',
            icon: <ScheduleIcon color="error" />,
            label: 'Expiration imminente',
            bgColor: theme.palette.error.light + '20',
          };
        } else if (daysRemaining <= 100) {
          return {
            color: 'warning',
            icon: <ScheduleIcon color="warning" />,
            label: 'Expire bientôt',
            bgColor: theme.palette.warning.light + '20',
          };
        } else {
          return {
            color: 'info',
            icon: <ScheduleIcon color="info" />,
            label: 'Expiration proche',
            bgColor: theme.palette.info.light + '20',
          };
        }
      case 'TOP_SELLING':
        return {
          color: 'secondary',
          icon: <TrendingUpIcon />,
          label: 'Produit populaire - Stock bas',
          bgColor: theme.palette.secondary.light + '20',
        };

      default:
        return {
          color: 'info',
          icon: <InfoIcon />,
          label: 'Alerte',
          bgColor: theme.palette.info.light + '20',
        };
    }
  };

  const severity = getSeverityInfo();

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        variant="outlined"
        sx={{
          mb: 2,
          borderLeft: `4px solid ${theme.palette[severity.color].main}`,
          bgcolor: severity.bgColor,
          '&:hover': {
            boxShadow: theme.shadows[2],
            transform: 'translateY(-2px)',
            transition: 'all 0.3s ease',
          },
        }}
      >
        <CardContent>
          <Grid container alignItems="center" spacing={2}>
            <Grid item>
              <Avatar
                sx={{
                  bgcolor: theme.palette[severity.color].main,
                  color: theme.palette[severity.color].contrastText,
                }}
              >
                {severity.icon}
              </Avatar>
            </Grid>
            <Grid item xs>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Typography variant="subtitle1" fontWeight="medium">
                  {alert.name}
                </Typography>
                <Chip
                  label={severity.label}
                  size="small"
                  color={severity.color}
                  variant="outlined"
                />
              </Box>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {type === 'RUPTURE' && 'Rupture de stock - Produit indisponible'}
                {type === 'ALERTE' && `Stock faible: ${alert.current_stock} unités restantes (seuil: ${alert.threshold})`}
                {type === 'EXPIRE' && `Expire le ${formatDate(alert.expiration_date)} (${alert.days_until_expiry} jours)`}
                {type === 'TOP_SELLING' && `Produit populaire : ${alert.total_sold} ventes - Stock restant ${alert.current_stock}`}
              </Typography>

              <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap', mt: 1 }}>
                {alert.category && (
                  <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <InventoryIcon fontSize="small" />
                    {alert.category}
                  </Typography>
                )}
                {alert.current_stock !== undefined && (
                  <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <InventoryIcon fontSize="small" />
                    Stock: {alert.current_stock}
                    {alert.threshold && `/${alert.threshold}`}
                    {alert.percentage && ` (${alert.percentage.toFixed(1)}%)`}
                  </Typography>
                )}
                {alert.total_sold !== undefined && (
                  <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <TrendingUpIcon fontSize="small" />
                    Vendu: {alert.total_sold} unités
                  </Typography>
                )}
              </Box>
            </Grid>
            <Grid item>
              <Button
                size="small"
                variant="contained"
                color={severity.color}
                endIcon={<ShoppingCartIcon />}
                onClick={() => onAcknowledge(alert.id)}
                sx={{ minWidth: 120 }}
              >
                {type === 'RUPTURE' ? 'Commander' : 'Réapprovisionner'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const InventoryAlerts = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alerts, setAlerts] = useState({
    out_of_stock: { products: [], count: 0 },
    low_stock: { products: [], count: 0 },
    expiring_soon: { products: [], count: 0 },
    top_selling_low_stock: { products: [], count: 0 }
  });
  const [activeTab, setActiveTab] = useState(0);

  const fetchAlerts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await dashboardService.getInventoryAlerts();
      setAlerts(response || {
        out_of_stock: { products: [], count: 0 },
        low_stock: { products: [], count: 0 },
        expiring_soon: { products: [], count: 0 },
        top_selling_low_stock: { products: [], count: 0 }
      });
    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError('Erreur lors du chargement des alertes');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5 * 60 * 1000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, [fetchAlerts]);

  const handleAcknowledgeAlert = async (productId) => {
    try {
      // TODO: Implement when backend endpoint is available
      // await api.put(`/stock/alerts/${productId}/acknowledge`);
      console.log('Acknowledge alert for product:', productId);
      fetchAlerts();
    } catch (err) {
      console.error('Error acknowledging alert:', err);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const getTotalAlerts = () => {
    return (
      alerts.out_of_stock.count +
      alerts.low_stock.count +
      alerts.expiring_soon.count +
      alerts.top_selling_low_stock.count
    );
  };

  const getCriticalAlerts = () => {
    return alerts.out_of_stock.count + alerts.low_stock.products.filter(p => (p.percentage || 0) <= 20).length;
  };

  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Box sx={{ width: '100%', textAlign: 'center' }}>
            <LinearProgress sx={{ mb: 2 }} />
            <Typography variant="body2" color="text.secondary">
              Chargement des alertes...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Box sx={{ textAlign: 'center' }}>
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
            <Button onClick={fetchAlerts} startIcon={<RefreshIcon />}>
              Réessayer
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const totalAlerts = getTotalAlerts();
  const criticalAlerts = getCriticalAlerts();

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <WarningIcon color="warning" />
            <Typography variant="h6">Alertes de Stock</Typography>
            {totalAlerts > 0 && (
              <Badge 
                badgeContent={totalAlerts} 
                color={criticalAlerts > 0 ? "error" : "warning"}
                sx={{ ml: 1 }}
              />
            )}
          </Box>
        }
        subheader="Surveillez les niveaux de stock et les dates d'expiration"
        action={
          <Tooltip title="Rafraîchir">
            <IconButton onClick={fetchAlerts}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        }
      />
      <CardContent>
        {/* Tabs for different alert types */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange} centered>
            <Tab label="Toutes" />
            <Tab label="Rupture" />
            <Tab label="Stock Bas" />
            <Tab label="Expiration" />
            <Tab label="Populaire" />
          </Tabs>
        </Box>

        {/* All Alerts */}
        {activeTab === 0 && (
          <>
            {totalAlerts === 0 ? (
              <Box textAlign="center" py={4}>
                <CheckCircleIcon color="success" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="h6" gutterBottom color="text.secondary">
                  Aucune alerte
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Tous les stocks sont à jour et optimaux
                </Typography>
              </Box>
            ) : (
              <Box sx={{ maxHeight: 400, overflow: 'auto', pr: 1 }}>
                {/* Out of stock alerts */}
                {alerts.out_of_stock.products.slice(0, 3).map((alert, index) => (
                  <AlertItem
                    key={`out-${index}`}
                    alert={alert}
                    type="RUPTURE"
                    onAcknowledge={handleAcknowledgeAlert}
                  />
                ))}
                
                {/* Low stock alerts */}
                {alerts.low_stock.products.slice(0, 3).map((alert, index) => (
                  <AlertItem
                    key={`low-${index}`}
                    alert={alert}
                    type="ALERTE"
                    onAcknowledge={handleAcknowledgeAlert}
                  />
                ))}
                
                {/* Expiring alerts */}
                {alerts.expiring_soon.products.slice(0, 3).map((alert, index) => (
                  <AlertItem
                    key={`expire-${index}`}
                    alert={alert}
                    type="EXPIRE"
                    onAcknowledge={handleAcknowledgeAlert}
                  />
                ))}
                
                {totalAlerts > 9 && (
                  <Button
                    fullWidth
                    variant="outlined"
                    endIcon={<ArrowForwardIcon />}
                    sx={{ mt: 2 }}
                  >
                    Voir toutes les alertes ({totalAlerts})
                  </Button>
                )}
              </Box>
            )}
          </>
        )}

        {/* Out of Stock Alerts */}
        {activeTab === 1 && (
          <>
            {alerts.out_of_stock.count === 0 ? (
              <Box textAlign="center" py={4}>
                <CheckCircleIcon color="success" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  Aucune rupture de stock
                </Typography>
              </Box>
            ) : (
              <Box sx={{ maxHeight: 400, overflow: 'auto', pr: 1 }}>
                {alerts.out_of_stock.products.map((alert, index) => (
                  <AlertItem
                    key={`out-${index}`}
                    alert={alert}
                    type="RUPTURE"
                    onAcknowledge={handleAcknowledgeAlert}
                  />
                ))}
              </Box>
            )}
          </>
        )}

        {/* Low Stock Alerts */}
        {activeTab === 2 && (
          <>
            {alerts.low_stock.count === 0 ? (
              <Box textAlign="center" py={4}>
                <TrendingUpIcon color="success" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  Tous les stocks sont au niveau optimal
                </Typography>
              </Box>
            ) : (
              <Box sx={{ maxHeight: 400, overflow: 'auto', pr: 1 }}>
                {alerts.low_stock.products.map((alert, index) => (
                  <AlertItem
                    key={`low-${index}`}
                    alert={alert}
                    type="ALERTE"
                    onAcknowledge={handleAcknowledgeAlert}
                  />
                ))}
              </Box>
            )}
          </>
        )}

        {/* Expiring Alerts */}
        {activeTab === 3 && (
          <>
            {alerts.expiring_soon.count === 0 ? (
              <Box textAlign="center" py={4}>
                <ScheduleIcon color="success" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  Aucun produit n'expire bientôt
                </Typography>
              </Box>
            ) : (
              <Box sx={{ maxHeight: 400, overflow: 'auto', pr: 1 }}>
                {alerts.expiring_soon.products.map((alert, index) => (
                  <AlertItem
                    key={`expire-${index}`}
                    alert={alert}
                    type="EXPIRE"
                    onAcknowledge={handleAcknowledgeAlert}
                  />
                ))}
              </Box>
            )}
          </>
        )}

        {/* Top Selling Low Stock Alerts */}
        {activeTab === 4 && (
          <>
            {alerts.top_selling_low_stock.count === 0 ? (
              <Box textAlign="center" py={4}>
                <CheckCircleIcon color="success" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  Aucun produit populaire en stock faible
                </Typography>
              </Box>
            ) : (
              <Box sx={{ maxHeight: 400, overflow: 'auto', pr: 1 }}>
                {alerts.top_selling_low_stock.products.map((alert, index) => (
                  <AlertItem
                    key={`top-${index}`}
                    alert={alert}
                    type="TOP_SELLING"
                    onAcknowledge={handleAcknowledgeAlert}
                  />
                ))}
              </Box>
            )}
          </>
        )}

        {/* Quick Stats */}
        <Box sx={{ mt: 4, pt: 3, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="subtitle1" gutterBottom fontWeight="medium">
            Statistiques
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="error.main" fontWeight="bold">
                  {alerts.out_of_stock.count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Ruptures
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={6}>
              <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="warning.main" fontWeight="bold">
                  {alerts.low_stock.count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Stock Bas
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={6}>
              <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="info.main" fontWeight="bold">
                  {alerts.expiring_soon.count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Expirent bientôt
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={6}>
              <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="secondary.main" fontWeight="bold">
                  {alerts.top_selling_low_stock.count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Populaires & Stock Bas
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </CardContent>
    </Card>
  );
};

export default InventoryAlerts;


/** import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  Chip,
  Button,
} from '@mui/material';
import {
  Warning,
  Error,
  Inventory,
  ArrowForward,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const InventoryAlerts = ({ alerts = {} }) => {
  const navigate = useNavigate();

  const alertTypes = [
    {
      key: 'out_of_stock',
      title: 'En rupture de stock',
      icon: <Error color="error" />,
      color: 'error',
      data: alerts.out_of_stock?.products || [],
    },
    {
      key: 'low_stock',
      title: 'Stock faible',
      icon: <Warning color="warning" />,
      color: 'warning',
      data: alerts.low_stock?.products || [],
    },
    {
      key: 'expiring_soon',
      title: 'Expiration proche',
      icon: <Warning color="info" />,
      color: 'info',
      data: alerts.expiring_soon?.products || [],
    },
  ];

  const handleViewAll = () => {
    navigate('/products', { state: { filter: 'low_stock' } });
  };

  const getSeverity = (alert) => {
    if (alert.status === 'RUPTURE') return 'error';
    if (alert.status === 'ALERTE') return 'warning';
    return 'info';
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 2,
          }}
        >
          <Typography variant="h6" fontWeight="bold">
            Alertes de stock
          </Typography>
          <Button
            size="small"
            endIcon={<ArrowForward />}
            onClick={handleViewAll}
          >
            Tout voir
          </Button>
        </Box>

        {alertTypes.map((alertType) => (
          <Box key={alertType.key} sx={{ mb: 3 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                mb: 1,
              }}
            >
              {alertType.icon}
              <Typography variant="subtitle2" fontWeight="medium">
                {alertType.title}
              </Typography>
              <Chip
                label={alertType.data.length}
                size="small"
                color={alertType.color}
                sx={{ ml: 'auto' }}
              />
            </Box>

            <List dense>
              {alertType.data.slice(0, 3).map((product, index) => (
                <motion.div
                  key={product.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <ListItem
                    sx={{
                      px: 0,
                      py: 0.5,
                      '&:hover': {
                        backgroundColor: 'action.hover',
                        borderRadius: 1,
                      },
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Inventory fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body2" noWrap>
                          {product.name}
                        </Typography>
                      }
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip
                            label={
                              product.status === 'RUPTURE'
                                ? 'Rupture'
                                : product.status === 'ALERTE'
                                ? 'Faible'
                                : 'Expire'
                            }
                            size="small"
                            color={getSeverity(product)}
                            variant="outlined"
                          />
                          <Typography variant="caption" color="text.secondary">
                            Stock: {product.current_stock || 0}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                </motion.div>
              ))}
            </List>

            {alertType.data.length > 3 && (
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ display: 'block', textAlign: 'center', mt: 1 }}
              >
                +{alertType.data.length - 3} autres
              </Typography>
            )}
          </Box>
        ))}

        {Object.keys(alerts).length === 0 && (
          <Box
            sx={{
              textAlign: 'center',
              py: 4,
            }}
          >
            <Inventory
              sx={{
                fontSize: 48,
                color: 'text.disabled',
                mb: 2,
              }}
            />
            <Typography variant="body2" color="text.secondary">
              Aucune alerte pour le moment
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default InventoryAlerts;**/

