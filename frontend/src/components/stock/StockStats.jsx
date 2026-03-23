StockStats.jsx// frontend/src/components/stock/StockStats.jsx
import React from 'react';
import { Grid, Card, Typography, Box } from '@mui/material';
import { useQuery } from 'react-query';
import { dashboardService } from '../../services/dashboard';
import { Inventory, Warning, Error, MonetizationOn } from '@mui/icons-material';
import CountUp from 'react-countup';

export default function StockStats() {
  const { data: stats, isLoading } = useQuery(
    'stock-stats',
    () => dashboardService.getStats(), // on utilise le dashboard existant
    { refetchInterval: 60000 }
  );

  // Extraire les données nécessaires
  const items = [
    {
      label: 'Produits actifs',
      value: stats?.total_products || 0,
      icon: <Inventory sx={{ fontSize: 40 }} />,
      color: 'primary',
    },
    {
      label: 'Valeur du stock',
      value: stats?.stock_value || 0,
      format: (v) => new Intl.NumberFormat('fr-CI', { style: 'currency', currency: 'XOF', minimumFractionDigits: 0 }).format(v),
      icon: <MonetizationOn sx={{ fontSize: 40 }} />,
      color: 'success',
    },
    {
      label: 'Stock faible',
      value: stats?.low_stock || 0,
      icon: <Warning sx={{ fontSize: 40 }} />,
      color: 'warning',
    },
    {
      label: 'Ruptures',
      value: stats?.out_of_stock || 0,
      icon: <Error sx={{ fontSize: 40 }} />,
      color: 'error',
    },
  ];

  if (isLoading) {
    return (
      <Grid container spacing={3}>
        {[1, 2, 3, 4].map((i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card sx={{ p: 2, height: 100 }}>
              <Box className="skeleton" sx={{ height: '100%' }} />
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <Grid container spacing={3}>
      {items.map((item, i) => (
        <Grid item xs={12} sm={6} md={3} key={i}>
          <Card
            sx={{
              p: 2,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: (theme) => theme.shadows[4],
              },
            }}
          >
            <Box
              sx={{
                p: 1.5,
                borderRadius: 2,
                bgcolor: (theme) => theme.palette[item.color].lighter,
              }}
            >
              {item.icon}
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">
                {item.label}
              </Typography>
              <Typography variant="h5" fontWeight="bold">
                <CountUp end={item.value} duration={1} separator=" " />
                {item.format && item.format(item.value).replace(/[0-9.,\s]/g, '')}
              </Typography>
            </Box>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}