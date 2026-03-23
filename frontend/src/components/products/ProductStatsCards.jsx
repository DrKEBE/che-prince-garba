import React from 'react';
import { Grid, Card, CardContent, Typography, Box } from '@mui/material';
import { Inventory, Warning, Error, AttachMoney } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { formatCurrency } from '../../utils/formatters';

const StatCard = ({ icon, label, value, color, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.5 }}
  >
    <Card
      sx={{
        height: '100%',
        background: (theme) => `linear-gradient(135deg, ${theme.palette[color].light} 0%, ${theme.palette[color].main} 100%)`,
        color: 'white',
        borderRadius: 3,
        boxShadow: (theme) => `0 8px 16px ${theme.palette[color].light}40`,
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="caption" sx={{ opacity: 0.8 }}>
              {label}
            </Typography>
            <Typography variant="h4" fontWeight="bold">
              {value}
            </Typography>
          </Box>
          <Box
            sx={{
              p: 1.5,
              borderRadius: '50%',
              bgcolor: 'rgba(255,255,255,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  </motion.div>
);

export default function ProductStatsCards({ stats }) {
  return (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={<Inventory fontSize="large" />}
          label="Total produits"
          value={stats.totalProducts}
          color="primary"
          delay={0.1}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={<AttachMoney fontSize="large" />}
          label="Valeur du stock"
          value={formatCurrency(stats.stockValue)}
          color="success"
          delay={0.2}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={<Warning fontSize="large" />}
          label="Stock faible"
          value={stats.lowStockCount}
          color="warning"
          delay={0.3}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          icon={<Error fontSize="large" />}
          label="Rupture"
          value={stats.outOfStockCount}
          color="error"
          delay={0.4}
        />
      </Grid>
    </Grid>
  );
}