import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Pagination,
  useTheme,
  useMediaQuery,
  Button,
  Typography,
  Chip,
} from '@mui/material';
import { ViewModule, ViewList } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { inventoryService } from '../../services/inventory';
import ProductCard from './ProductCard';
import DataTable from '../common/DataTable';
import ProductFilter from './ProductFilter';
import LoadingSpinner from '../common/LoadingSpinner';
import toast from 'react-hot-toast';

const ProductList = ({ canManage, onEdit, onAdd, refreshTrigger }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState([]);
  const [viewMode, setViewMode] = useState(isMobile ? 'grid' : 'table');
  const [filters, setFilters] = useState({});
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0 });

  useEffect(() => {
    loadProducts();
  }, [filters, pagination.page, refreshTrigger]);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const params = {
        skip: (pagination.page - 1) * pagination.limit,
        limit: pagination.limit,
        ...filters,
      };
      const data = await inventoryService.getProducts(params);
      setProducts(data);
      // Si l'API renvoie le total, le mettre à jour
      // Ici on suppose que le backend renvoie directement la liste, pas de métadonnées
      setPagination(prev => ({ ...prev, total: data.length < prev.limit ? prev.skip + data.length : prev.skip + prev.limit + 1 }));
    } catch (error) {
      toast.error('Erreur chargement produits');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleDelete = async (id) => {
    try {
      await inventoryService.deleteProduct(id);
      toast.success('Produit désactivé');
      loadProducts();
    } catch (error) {
      toast.error('Erreur lors de la désactivation');
    }
  };

  // Colonnes pour le mode tableau
  const columns = [
    {
      field: 'name',
      headerName: 'Produit',
      flex: 2,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {params.row.images?.[0] ? (
            <Box
              component="img"
              src={`http://localhost:8000/uploads/products/${params.row.images[0]}`}
              sx={{ width: 40, height: 40, borderRadius: 1, objectFit: 'cover' }}
            />
          ) : (
            <Box sx={{ width: 40, height: 40, borderRadius: 1, bgcolor: 'grey.200' }} />
          )}
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {params.row.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {params.row.sku}
            </Typography>
          </Box>
        </Box>
      ),
    },
    { field: 'category', headerName: 'Catégorie', width: 150 },
    {
      field: 'current_stock',
      headerName: 'Stock',
      width: 120,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2" fontWeight="bold">
            {params.row.current_stock || 0}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            seuil: {params.row.alert_threshold}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'selling_price',
      headerName: 'Prix',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="bold" color="primary.main">
          {params.row.selling_price?.toLocaleString()} F
        </Typography>
      ),
    },
    {
      field: 'status',
      headerName: 'Statut',
      width: 120,
      renderCell: (params) => {
        const stock = params.row.current_stock || 0;
        const threshold = params.row.alert_threshold;
        let color = 'success';
        let label = 'En stock';
        if (stock <= 0) { color = 'error'; label = 'Rupture'; }
        else if (stock <= threshold) { color = 'warning'; label = 'Faible'; }
        return <Chip label={label} size="small" color={color} />;
      },
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 150,
      renderCell: (params) => (
        <Box>
          <Button size="small" onClick={() => onEdit(params.row)}>Modifier</Button>
          <Button size="small" color="error" onClick={() => handleDelete(params.row.id)}>
            Désactiver
          </Button>
        </Box>
      ),
    },
  ];

  if (loading && products.length === 0) return <LoadingSpinner />;

  return (
    <Box>
      {/* Filtres */}
      <ProductFilter onFilterChange={handleFilterChange} compact />

      {/* Contrôles d'affichage */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle1">
          {products.length} produit(s) affiché(s)
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant={viewMode === 'grid' ? 'contained' : 'outlined'}
            size="small"
            onClick={() => setViewMode('grid')}
            startIcon={<ViewModule />}
          >
            Grille
          </Button>
          <Button
            variant={viewMode === 'table' ? 'contained' : 'outlined'}
            size="small"
            onClick={() => setViewMode('table')}
            startIcon={<ViewList />}
          >
            Tableau
          </Button>
        </Box>
      </Box>

      {/* Affichage */}
      <AnimatePresence>
        {viewMode === 'grid' ? (
          <Grid container spacing={3}>
            {products.map((product, index) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <ProductCard
                    product={product}
                    onEdit={onEdit}
                    onDelete={handleDelete}
                    canManage={canManage}
                  />
                </motion.div>
              </Grid>
            ))}
          </Grid>
        ) : (
          <DataTable
            rows={products}
            columns={columns}
            loading={loading}
            getRowId={(row) => row.id}
            pageSize={pagination.limit}
          />
        )}
      </AnimatePresence>

      {/* Pagination */}
      {pagination.total > pagination.limit && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={Math.ceil(pagination.total / pagination.limit)}
            page={pagination.page}
            onChange={(e, page) => setPagination(prev => ({ ...prev, page }))}
            color="primary"
            shape="rounded"
          />
        </Box>
      )}
    </Box>
  );
};

export default ProductList;