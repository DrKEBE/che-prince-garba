// frontend\src\pages\Dashboard.jsx
import React, { useState } from 'react';
import {
  Grid,
  Box,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  IconButton,
  Menu,
  MenuItem,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  MoreVert,
  ShoppingCart,
  People,
  Inventory,
  AttachMoney,
  CalendarToday,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';

import StatsCard from '../components/dashboard/StatsCard';
import SalesChart from '../components/dashboard/SalesChart';
import InventoryAlerts from '../components/dashboard/InventoryAlerts';
import { dashboardService } from '../services/dashboard';

export default function Dashboard() {
  const [timeRange, setTimeRange] = useState('week');
  const [anchorEl, setAnchorEl] = useState(null);

  const { data: stats, isLoading: statsLoading } = useQuery(
    ['dashboard', 'stats'],
    () => dashboardService.getStats(),
    { 
      refetchInterval: 30000,
      staleTime: 10000 
    }
  );

  const { data: realtimeUpdates, isLoading: updatesLoading } = useQuery(
    ['dashboard', 'realtime-updates'],
    () => dashboardService.getRealtimeUpdates(),
    { 
      refetchInterval: 15000,
      staleTime: 5000 
    }
  );

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleTimeRangeChange = (range) => {
    setTimeRange(range);
    handleMenuClose();
  };

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return '0 F';
    return new Intl.NumberFormat('fr-CI', {
      style: 'currency',
      currency: 'XOF',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  if (statsLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <LinearProgress sx={{ width: '50%' }} />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Tableau de bord
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Bienvenue sur votre espace de gestion Luxe Beauté
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Chiffre d'affaires"
            value={formatCurrency(stats?.daily_revenue || 0)}
            icon={<AttachMoney />}
            color="primary"
            trend={stats?.revenue_trend || 0}
            subtitle="Aujourd'hui"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Ventes"
            value={stats?.total_sales || 0}
            icon={<ShoppingCart />}
            color="success"
            trend={10}
            subtitle="Total"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Clients"
            value={stats?.total_clients || 0}
            icon={<People />}
            color="info"
            trend={stats?.client_trend || 0}
            subtitle="Nouveaux ce mois"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Produits"
            value={stats?.total_products || 0}
            icon={<Inventory />}
            color="warning"
            trend={-2}
            subtitle={`${stats?.out_of_stock || 0} en rupture`}
          />
        </Grid>
      </Grid>

      {/* Charts and Alerts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={8}>
          <SalesChart />
        </Grid>
        <Grid item xs={12} lg={4}>
          <InventoryAlerts />
        </Grid>
      </Grid>

      {/* Real-time Updates */}
      {realtimeUpdates && !updatesLoading && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card sx={{ mt: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="medium">
                Activités en temps réel
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <ShoppingCart sx={{ mr: 2, color: 'primary.main' }} />
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="body2">
                        Ventes aujourd'hui
                      </Typography>
                      <Typography variant="h6" fontWeight="bold">
                        {realtimeUpdates.today_sales} ventes
                      </Typography>
                    </Box>
                    <Chip
                      label={formatCurrency(realtimeUpdates.today_revenue)}
                      color="primary"
                      size="small"
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CalendarToday sx={{ mr: 2, color: 'success.main' }} />
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="body2">
                        Rendez-vous
                      </Typography>
                      <Typography variant="h6" fontWeight="bold">
                        {realtimeUpdates.today_appointments?.total || 0} prévus
                      </Typography>
                    </Box>
                    <Chip
                      label={`${realtimeUpdates.today_appointments?.upcoming?.length || 0} prochains`}
                      color="success"
                      size="small"
                    />
                  </Box>
                </Grid>
              </Grid>
              
              {/* Recent sales */}
              {realtimeUpdates.recent_sales && realtimeUpdates.recent_sales.length > 0 && (
                <Box sx={{ mt: 3, pt: 3, borderTop: 1, borderColor: 'divider' }}>
                  <Typography variant="subtitle2" gutterBottom color="text.secondary">
                    Dernières ventes
                  </Typography>
                  <Grid container spacing={1}>
                    {realtimeUpdates.recent_sales.slice(0, 3).map((sale, index) => (
                      <Grid item xs={12} key={index}>
                        <Box sx={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center',
                          py: 1,
                          px: 2,
                          bgcolor: 'action.hover',
                          borderRadius: 1
                        }}>
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              {sale.client_name || 'Client non renseigné'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {sale.invoice_number} • {sale.time}
                            </Typography>
                          </Box>
                          <Typography variant="body2" fontWeight="bold">
                            {formatCurrency(sale.amount)}
                          </Typography>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}
    </Box>
  );
}