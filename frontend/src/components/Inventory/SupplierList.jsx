import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  IconButton,
  Stack,
  TablePagination,
} from '@mui/material';
import { Edit, Delete, Business } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { inventoryService } from '../../services/inventory';
import LoadingSpinner from '../common/LoadingSpinner';
import SupplierCard from './SupplierCard';

const SupplierList = ({ canManage, onEdit, onAdd, refreshTrigger }) => {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(12);

  useEffect(() => {
    loadSuppliers();
  }, [refreshTrigger]);

  const loadSuppliers = async () => {
    setLoading(true);
    try {
      const data = await inventoryService.getSuppliers({ active_only: true, limit: 200 });
      setSuppliers(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Désactiver ce fournisseur ?')) {
      try {
        await inventoryService.deleteSupplier(id);
        toast.success('Fournisseur désactivé');
        loadSuppliers();
      } catch (error) {
        toast.error('Erreur');
      }
    }
  };

  const handleChangePage = (event, newPage) => setPage(newPage);
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (loading) return <LoadingSpinner />;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 3 }}>
        {canManage && (
          <Button variant="contained" startIcon={<Business />} onClick={onAdd}>
            Nouveau fournisseur
          </Button>
        )}
      </Box>

      <Grid container spacing={3}>
        {suppliers.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((supplier, index) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={supplier.id}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <SupplierCard
                supplier={supplier}
                onEdit={onEdit}
                onDelete={handleDelete}
                canManage={canManage}
              />
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {suppliers.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary">
            Aucun fournisseur trouvé
          </Typography>
        </Box>
      )}

      <TablePagination
        component="div"
        count={suppliers.length}
        page={page}
        onPageChange={handleChangePage}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        rowsPerPageOptions={[12, 24, 48]}
        labelRowsPerPage="Fournisseurs par page"
        sx={{ mt: 2 }}
      />
    </Box>
  );
};

export default SupplierList;