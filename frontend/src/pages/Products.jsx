// frontend/src/pages/Products.jsx
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  InputAdornment,
  Fab,
  Tooltip,
  Alert,
  Badge,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Inventory,
  Search,
  FilterList,
  TrendingUp,
  TrendingDown,
  LocalOffer,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import DataTable from '../components/common/DataTable.jsx';
import ProductForm from '../components/products/ProductForm';
import ProductFilter from '../components/products/ProductFilter';
import ProductStockModal from '../components/products/ProductStockModal'; // Import ajouté
import ProductStatsCards from '../components/products/ProductStatsCards';
import { productService } from '../services/products';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Products() {
  const [openForm, setOpenForm] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [productToDelete, setProductToDelete] = useState(null);

  // Nouveaux états pour la gestion du stock
  const [stockModalOpen, setStockModalOpen] = useState(false);
  const [selectedForStock, setSelectedForStock] = useState(null);

  const { isAdmin, isManager } = useAuth();
  const queryClient = useQueryClient();

  const { data: products, isLoading } = useQuery(
    ['products', { search: searchTerm, ...filters }],
    () => productService.getProducts({ search: searchTerm, ...filters }),
    { refetchOnWindowFocus: false }
  );

  const { data: statsData } = useQuery(
    'product-stats',
    () => productService.getProductStats(),
    {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    }
  );

  const deleteMutation = useMutation(
    (id) => productService.deleteProduct(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('products');
        toast.success('Produit créé avec succès', {
          icon: '✅',
          duration: 4000,
          style: { borderRadius: '10px', background: '#333', color: '#fff' }
        });              
        setDeleteDialog(false);
      },
      onError: (error) => {
        toast.error('Erreur lors de la suppression');
      },
    }
  );

  const handleOpenForm = (product = null) => {
    setSelectedProduct(product);
    setOpenForm(true);
  };

  const handleCloseForm = () => {
    setOpenForm(false);
    setSelectedProduct(null);
  };

  const handleDeleteClick = (product) => {
    setProductToDelete(product);
    setDeleteDialog(true);
  };

  const handleConfirmDelete = () => {
    if (productToDelete) {
      deleteMutation.mutate(productToDelete.id);
    }
  };

  // Nouveaux handlers pour le stock
  const handleOpenStockModal = (product) => {
    setSelectedForStock(product);
    setStockModalOpen(true);
  };

  const handleCloseStockModal = () => {
    setStockModalOpen(false);
    setSelectedForStock(null);
  };

  const handleSearch = (value) => {
    setSearchTerm(value);
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-CI', {
      style: 'currency',
      currency: 'XOF',
      minimumFractionDigits: 0,
    }).format(value);
  };

  const getStockStatus = (stock, threshold) => {
    if (stock <= 0) return { label: 'Rupture', color: 'error' };
    if (stock <= threshold) return { label: 'Faible', color: 'warning' };
    return { label: 'En stock', color: 'success' };
  };

  const columns = [
    {
      field: 'name',
      headerName: 'Produit',
      flex: 2,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {params.row.images?.[0] ? (
            <Box
              component="img"
              src={`http://localhost:8000/uploads/products/${params.row.images[0]}`}
              sx={{
                width: 40,
                height: 40,
                borderRadius: 1,
                objectFit: 'cover',
                mr: 2,
              }}
            />
          ) : (
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 1,
                bgcolor: 'primary.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mr: 2,
              }}
            >
              <Inventory sx={{ color: 'white' }} />
            </Box>
          )}
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {params.row.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {params.row.category} • {params.row.sku}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'stock',
      headerName: 'Stock',
      flex: 1,
      renderCell: (params) => {
        const status = getStockStatus(
          params.row.current_stock || 0,
          params.row.alert_threshold
        );
        return (
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {params.row.current_stock || 0}
              <Typography
                component="span"
                variant="caption"
                color="text.secondary"
                sx={{ ml: 0.5 }}
              >
                /{params.row.alert_threshold}
              </Typography>
            </Typography>
            <Chip
              label={status.label}
              size="small"
              color={status.color}
              sx={{ height: 20, fontSize: '0.7rem' }}
            />
          </Box>
        );
      },
    },
    {
      field: 'prices',
      headerName: 'Prix',
      flex: 1,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2" fontWeight="medium">
            {formatCurrency(params.row.selling_price)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Achat: {formatCurrency(params.row.purchase_price)}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'margin',
      headerName: 'Marge',
      flex: 1,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {params.row.margin >= 30 ? (
            <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
          ) : (
            <TrendingDown sx={{ color: 'warning.main', mr: 0.5 }} />
          )}
          <Typography
            variant="body2"
            color={params.row.margin >= 30 ? 'success.main' : 'warning.main'}
            fontWeight="medium"
          >
            {params.row.margin?.toFixed(1) || 0}%
          </Typography>
        </Box>
      ),
    },
    {
      field: 'status',
      headerName: 'Statut',
      flex: 1,
      renderCell: (params) => (
        <Chip
          label={params.row.is_active ? 'Actif' : 'Inactif'}
          color={params.row.is_active ? 'success' : 'default'}
          size="small"
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      flex: 1,
      renderCell: (params) => (
        <Box>
          <Tooltip title="Voir">
            <IconButton size="small" onClick={() => handleOpenForm(params.row)}>
              <Visibility fontSize="small" />
            </IconButton>
          </Tooltip>
          {(isAdmin || isManager) && (
            <>
              <Tooltip title="Modifier">
                <IconButton size="small" onClick={() => handleOpenForm(params.row)}>
                  <Edit fontSize="small" />
                </IconButton>
              </Tooltip>
              {/* Nouveau bouton Gérer le stock */}
              <Tooltip title="Gérer le stock">
                <IconButton size="small" onClick={() => handleOpenStockModal(params.row)}>
                  <Inventory fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Supprimer">
                <IconButton
                  size="small"
                  onClick={() => handleDeleteClick(params.row)}
                  color="error"
                >
                  <Delete fontSize="small" />
                </IconButton>
              </Tooltip>
            </>
          )}
        </Box>
      ),
    },
  ];

  return (
    <Box>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
        }}
      >
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Gestion des produits
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {products?.length || 0} produits enregistrés
          </Typography>
        </Box>
        {(isAdmin || isManager) && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenForm()}
            sx={{
              bgcolor: 'primary.main',
              '&:hover': {
                bgcolor: 'primary.dark',
              },
            }}
          >
            Nouveau produit
          </Button>
        )}
      </Box>

      {/* Cartes de statistiques */}
      {statsData && <ProductStatsCards stats={statsData} />}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <ProductFilter
            onSearch={handleSearch}
            onFilterChange={handleFilterChange}
          />
        </CardContent>
      </Card>

      {/* Products Grid */}
      <AnimatePresence>
        {isLoading ? (
          <Grid container spacing={3}>
            {[1, 2, 3, 4].map((i) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={i}>
                <Card>
                  <Box sx={{ p: 2 }}>
                    <Box className="skeleton" sx={{ height: 200, borderRadius: 1 }} />
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : products && products.length > 0 ? (
          <>
            <DataTable
              rows={products}
              columns={columns}
              loading={isLoading}
              getRowId={(row) => row.id}
              pageSize={10}
              rowsPerPageOptions={[10, 25, 50]}
              checkboxSelection={false}
              sx={{ height: 600 }}
            />
          </>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 8 }}>
                <Inventory sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Aucun produit trouvé
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  {searchTerm || Object.keys(filters).length > 0
                    ? 'Essayez de modifier vos critères de recherche'
                    : 'Commencez par ajouter votre premier produit'}
                </Typography>
                {(isAdmin || isManager) && (
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => handleOpenForm()}
                  >
                    Ajouter un produit
                  </Button>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quick Action FAB */}
      {(isAdmin || isManager) && (
        <Fab
          color="primary"
          aria-label="add"
          sx={{
            position: 'fixed',
            bottom: 32,
            right: 32,
            bgcolor: 'primary.main',
            '&:hover': {
              bgcolor: 'primary.dark',
              transform: 'scale(1.1)',
            },
            transition: 'all 0.2s ease',
          }}
          onClick={() => handleOpenForm()}
        >
          <Add />
        </Fab>
      )}

      {/* Product Form Dialog */}
      <Dialog
        open={openForm}
        onClose={handleCloseForm}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle>
          {selectedProduct ? 'Modifier le produit' : 'Nouveau produit'}
        </DialogTitle>
        <DialogContent dividers>
          <ProductForm
            product={selectedProduct}
            onSuccess={handleCloseForm}
            onCancel={handleCloseForm}
          />
        </DialogContent>
      </Dialog>

      {/* Stock Management Modal - Nouveau */}
      <ProductStockModal
        open={stockModalOpen}
        onClose={handleCloseStockModal}
        product={selectedForStock}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog}
        onClose={() => setDeleteDialog(false)}
        PaperProps={{
          sx: {
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle>Confirmer la suppression</DialogTitle>
        <DialogContent>
          <Typography>
            Êtes-vous sûr de vouloir supprimer le produit "
            {productToDelete?.name}" ?
          </Typography>
          <Alert severity="warning" sx={{ mt: 2 }}>
            Cette action est irréversible. Toutes les données associées seront
            également supprimées.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>Annuler</Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={deleteMutation.isLoading}
          >
            {deleteMutation.isLoading ? 'Suppression...' : 'Supprimer'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}