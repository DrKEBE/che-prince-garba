import React from 'react';
import { Tabs, Tab, Badge, Box } from '@mui/material';
import {
  Inventory as ProductIcon,
  Warehouse as StockIcon,
  LocalShipping as SupplierIcon,
  ShoppingCart as OrderIcon,
  Dashboard as DashboardIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const InventoryTabs = ({ value, onChange, counts = {} }) => {
  const tabs = [
    { label: 'Tableau de bord', icon: <DashboardIcon />, value: 'dashboard' },
    { label: 'Produits', icon: <ProductIcon />, value: 'products', count: counts.products },
    { label: 'Stock', icon: <StockIcon />, value: 'stock' },
    { label: 'Fournisseurs', icon: <SupplierIcon />, value: 'suppliers', count: counts.suppliers },
    { label: 'Commandes', icon: <OrderIcon />, value: 'orders', count: counts.orders },
  ];

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
      <Tabs
        value={value}
        onChange={onChange}
        variant="scrollable"
        scrollButtons="auto"
        allowScrollButtonsMobile
        sx={{
          '& .MuiTab-root': {
            minHeight: 64,
            flexDirection: 'row',
            alignItems: 'center',
            gap: 1,
            fontWeight: 600,
            fontSize: '0.95rem',
            transition: 'all 0.2s',
            '&:hover': {
              color: 'primary.main',
              backgroundColor: 'rgba(138, 43, 226, 0.05)',
            },
          },
          '& .Mui-selected': {
            color: 'primary.main',
          },
        }}
      >
        {tabs.map((tab) => (
          <Tab
            key={tab.value}
            value={tab.value}
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {tab.icon}
                {tab.label}
                {tab.count !== undefined && (
                  <Badge
                    badgeContent={tab.count}
                    color="primary"
                    max={99}
                    sx={{ ml: 1 }}
                  />
                )}
              </Box>
            }
          />
        ))}
      </Tabs>
    </Box>
  );
};

export default InventoryTabs;