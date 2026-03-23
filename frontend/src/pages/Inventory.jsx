import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  Fab,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { Add as AddIcon, Inventory as InventoryIcon } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import InventoryTabs from '../components/inventory/InventoryTabs';
import InventoryDashboard from '../components/inventory/InventoryDashboard';
import ProductList from '../components/inventory/ProductList';     // contient ProductCard, DataTable, etc.
import SupplierList from '../components/inventory/SupplierList';   // contient SupplierCard, etc.
import StockMovementList from '../components/inventory/StockMovementList'; // historique
import ProductForm from '../components/inventory/ProductForm';
import SupplierForm from '../components/inventory/SupplierForm';
import StockMovementForm from '../components/inventory/StockMovementForm';
import { inventoryService } from '../services/inventory';
import toast from 'react-hot-toast';

const TabPanel = ({ children, value, index, ...props }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    transition={{ duration: 0.3 }}
    style={{ display: value === index ? 'block' : 'none' }}
    {...props}
  >
    {children}
  </motion.div>
);

export default function Inventory() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { isAdmin, isManager, isStockManager } = useAuth();

  const [tabValue, setTabValue] = useState(0);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [openProductForm, setOpenProductForm] = useState(false);
  const [openSupplierForm, setOpenSupplierForm] = useState(false);
  const [openStockForm, setOpenStockForm] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [selectedSupplier, setSelectedSupplier] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const canManage = isAdmin || isManager || isStockManager;

  useEffect(() => {
    loadDashboardStats();
  }, [refreshTrigger]);

  const loadDashboardStats = async () => {
    try {
      const stats = await inventoryService.getDashboardStats();
      setDashboardStats(stats);
    } catch (error) {
      console.error('Erreur chargement dashboard inventaire', error);
    }
  };

  const handleTabChange = (event, newValue) => setTabValue(newValue);

  const handleProductSuccess = () => {
    setOpenProductForm(false);
    setSelectedProduct(null);
    setRefreshTrigger(prev => prev + 1);
    toast.success('Opération réussie');
  };

  const handleSupplierSuccess = () => {
    setOpenSupplierForm(false);
    setSelectedSupplier(null);
    setRefreshTrigger(prev => prev + 1);
    toast.success('Opération réussie');
  };

  const handleStockSuccess = () => {
    setOpenStockForm(false);
    setRefreshTrigger(prev => prev + 1);
    toast.success('Mouvement enregistré');
  };

  const handleEditProduct = (product) => {
    setSelectedProduct(product);
    setOpenProductForm(true);
  };

  const handleEditSupplier = (supplier) => {
    setSelectedSupplier(supplier);
    setOpenSupplierForm(true);
  };

  return (
    <Box sx={{ p: { xs: 2, md: 3 } }}>
      {/* En-tête */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
          flexWrap: 'wrap',
          gap: 2,
        }}
      >
        <Box>
          <Typography
            variant="h4"
            component="h1"
            sx={{
              fontWeight: 700,
              background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            }}
          >
            <InventoryIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />
            Gestion d'inventaire
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            Produits • Stock • Fournisseurs
          </Typography>
        </Box>
      </Box>

      {/* Onglets principaux */}
      <Paper
        elevation={0}
        sx={{
          mb: 3,
          borderRadius: 3,
          bgcolor: 'background.paper',
          border: `1px solid ${theme.palette.divider}`,
        }}
      >
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant={isMobile ? 'scrollable' : 'fullWidth'}
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': { py: 2, fontWeight: 600 },
            '& .Mui-selected': { color: 'primary.main' },
          }}
        >
          <Tab label="Tableau de bord" />
          <Tab label="Produits" />
          <Tab label="Stock & Mouvements" />
          <Tab label="Fournisseurs" />
        </Tabs>
      </Paper>

      {/* Panneaux */}
      <AnimatePresence mode="wait">
        {/* Dashboard */}
        <TabPanel value={tabValue} index={0}>
          <InventoryDashboard
            stats={dashboardStats}
            onRefresh={loadDashboardStats}
            onViewProduct={(product) => {
              setTabValue(1);
              // Émettre un événement pour sélectionner le produit dans la liste
              setTimeout(() => {
                window.dispatchEvent(new CustomEvent('inventory:focusProduct', { detail: product }));
              }, 100);
            }}
          />
        </TabPanel>

        {/* Produits */}
        <TabPanel value={tabValue} index={1}>
          <ProductList
            canManage={canManage}
            onEdit={handleEditProduct}
            onAdd={() => {
              setSelectedProduct(null);
              setOpenProductForm(true);
            }}
            refreshTrigger={refreshTrigger}
          />
        </TabPanel>

        {/* Stock & Mouvements */}
        <TabPanel value={tabValue} index={2}>
          <StockMovementList
            canManage={canManage}
            onAdd={() => setOpenStockForm(true)}
            refreshTrigger={refreshTrigger}
          />
        </TabPanel>

        {/* Fournisseurs */}
        <TabPanel value={tabValue} index={3}>
          <SupplierList
            canManage={canManage}
            onEdit={handleEditSupplier}
            onAdd={() => {
              setSelectedSupplier(null);
              setOpenSupplierForm(true);
            }}
            refreshTrigger={refreshTrigger}
          />
        </TabPanel>
      </AnimatePresence>

      {/* FAB pour ajout rapide (visible sur les onglets Produits/Stock/Fournisseurs) */}
      {canManage && tabValue !== 0 && (
        <Fab
          color="primary"
          sx={{
            position: 'fixed',
            bottom: 32,
            right: 32,
            boxShadow: theme.shadows[8],
            transition: 'transform 0.2s',
            '&:hover': { transform: 'scale(1.1)' },
          }}
          onClick={() => {
            if (tabValue === 1) {
              setSelectedProduct(null);
              setOpenProductForm(true);
            } else if (tabValue === 2) {
              setOpenStockForm(true);
            } else if (tabValue === 3) {
              setSelectedSupplier(null);
              setOpenSupplierForm(true);
            }
          }}
        >
          <AddIcon />
        </Fab>
      )}

      {/* Modales */}
      <ProductForm
        open={openProductForm}
        onClose={() => setOpenProductForm(false)}
        onSuccess={handleProductSuccess}
        product={selectedProduct}
      />
      <SupplierForm
        open={openSupplierForm}
        onClose={() => setOpenSupplierForm(false)}
        onSuccess={handleSupplierSuccess}
        supplier={selectedSupplier}
      />
      <StockMovementForm
        open={openStockForm}
        onClose={() => setOpenStockForm(false)}
        onSuccess={handleStockSuccess}
      />
    </Box>
  );
}