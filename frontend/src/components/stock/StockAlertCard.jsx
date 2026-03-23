import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  LinearProgress,
  Button,
  Avatar,
  Badge,
  Divider,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  TrendingUp as TrendingUpIcon,
  Refresh as RefreshIcon,
  ShoppingCart as ShoppingCartIcon,
  ArrowForward as ArrowForwardIcon,
  Inventory as InventoryIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { formatDate, formatCurrency } from '../../utils/formatters';

const StockAlerts = ({ alerts, loading, onRefresh, onReorder }) => {
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

  if (!alerts || Object.keys(alerts).length === 0) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Box sx={{ textAlign: 'center' }}>
            <CheckCircleIcon color="success" sx={{ fontSize: 48, mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Aucune alerte active
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Tous les stocks sont optimaux
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const totalAlerts = 
    (alerts.out_of_stock?.count || 0) + 
    (alerts.low_stock?.count || 0) + 
    (alerts.expiring_soon?.count || 0);

  const criticalAlerts = alerts.out_of_stock?.count || 0;

  return (
    <Card sx={{ height: '100%', borderRadius: 3 }}>
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
        subheader="Surveillez les niveaux de stock critiques"
        action={
          <Tooltip title="Rafraîchir">
            <IconButton onClick={onRefresh}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        }
      />
      
      <Divider />
      
      <CardContent>
        {/* Statistiques rapides */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={4}>
            <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="error.main" fontWeight="bold">
                {alerts.out_of_stock?.count || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ruptures
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={4}>
            <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="warning.main" fontWeight="bold">
                {alerts.low_stock?.count || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Stock Bas
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={4}>
            <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" color="info.main" fontWeight="bold">
                {alerts.expiring_soon?.count || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Expirent bientôt
              </Typography>
            </Card>
          </Grid>
        </Grid>

        {/* Liste des alertes */}
        <Box sx={{ maxHeight: 400, overflow: 'auto', pr: 1 }}>
          {/* Alertes de rupture */}
          {alerts.out_of_stock?.products?.map((alert, index) => (
            <motion.div
              key={`out-${index}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <AlertCard
                alert={alert}
                type="RUPTURE"
                onReorder={onReorder}
                severity="error"
              />
            </motion.div>
          ))}

          {/* Alertes stock bas */}
          {alerts.low_stock?.products?.map((alert, index) => (
            <motion.div
              key={`low-${index}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <AlertCard
                alert={alert}
                type="ALERTE"
                onReorder={onReorder}
                severity="warning"
              />
            </motion.div>
          ))}

          {/* Alertes expiration */}
          {alerts.expiring_soon?.products?.map((alert, index) => (
            <motion.div
              key={`expire-${index}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <AlertCard
                alert={alert}
                type="EXPIRE"
                onReorder={onReorder}
                severity="info"
              />
            </motion.div>
          ))}
        </Box>

        {/* Actions globales */}
        <Box sx={{ mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<ShoppingCartIcon />}
                onClick={() => onReorder && onReorder(null)}
              >
                Commander tout
              </Button>
            </Grid>
            <Grid item xs={6}>
              <Button
                fullWidth
                variant="contained"
                endIcon={<ArrowForwardIcon />}
                onClick={onRefresh}
              >
                Voir toutes les alertes
              </Button>
            </Grid>
          </Grid>
        </Box>
      </CardContent>
    </Card>
  );
};

// Composant de carte d'alerte
const AlertCard = ({ alert, type, onReorder, severity }) => {
  const getSeverityIcon = () => {
    switch (type) {
      case 'RUPTURE':
        return <ErrorIcon />;
      case 'ALERTE':
        return <WarningIcon />;
      case 'EXPIRE':
        return <ScheduleIcon />;
      default:
        return <WarningIcon />;
    }
  };

  const getSeverityColor = () => {
    switch (severity) {
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  const getAlertMessage = () => {
    switch (type) {
      case 'RUPTURE':
        return 'Rupture de stock - Produit indisponible';
      case 'ALERTE':
        return `Stock faible: ${alert.current_stock} unités restantes`;
      case 'EXPIRE':
        return `Expire le ${formatDate(alert.expiration_date)}`;
      default:
        return 'Alerte de stock';
    }
  };

  return (
    <Card
      variant="outlined"
      sx={{
        mb: 2,
        borderLeft: `4px solid`,
        borderLeftColor: `${getSeverityColor()}.main`,
        '&:hover': {
          boxShadow: 2,
          transform: 'translateY(-2px)',
          transition: 'all 0.3s ease',
        },
      }}
    >
      <CardContent sx={{ p: 2 }}>
        <Grid container alignItems="center" spacing={2}>
          <Grid item>
            <Avatar
              sx={{
                bgcolor: `${getSeverityColor()}.main`,
                color: 'white',
              }}
            >
              {getSeverityIcon()}
            </Avatar>
          </Grid>
          
          <Grid item xs>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="subtitle1" fontWeight="medium">
                {alert.name || alert.product?.name}
              </Typography>
              <Chip
                label={type === 'EXPIRE' ? 'Expiration' : type}
                size="small"
                color={getSeverityColor()}
                variant="outlined"
              />
            </Box>
            
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {getAlertMessage()}
            </Typography>

            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 1 }}>
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
                </Typography>
              )}
              
              {alert.days_until_expiry !== undefined && (
                <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <ScheduleIcon fontSize="small" />
                  {alert.days_until_expiry} jours restants
                </Typography>
              )}
            </Box>
          </Grid>
          
          <Grid item>
            {type !== 'EXPIRE' && (
              <Button
                size="small"
                variant="contained"
                color={getSeverityColor()}
                startIcon={<ShoppingCartIcon />}
                onClick={() => onReorder && onReorder(alert)}
                sx={{ minWidth: 120 }}
              >
                Réapprovisionner
              </Button>
            )}
          </Grid>
        </Grid>
        
        {/* Barre de progression pour les alertes de stock */}
        {(type === 'ALERTE' || type === 'RUPTURE') && alert.threshold && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress
              variant="determinate"
              value={Math.min(100, ((alert.current_stock || 0) / alert.threshold) * 100)}
              color={getSeverityColor()}
              sx={{ height: 6, borderRadius: 3 }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              {Math.round(((alert.current_stock || 0) / alert.threshold) * 100)}% du seuil minimum
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default StockAlerts;