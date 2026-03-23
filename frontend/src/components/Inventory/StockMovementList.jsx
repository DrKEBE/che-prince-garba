import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  IconButton,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TablePagination,
} from '@mui/material';
import {
  Add,
  Refresh,
  TrendingUp,
  TrendingDown,
  SwapHoriz,
  Delete,
  History,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { inventoryService } from '../../services/inventory';
import { formatDate, formatCurrency } from '../../utils/formatters';
import { STOCK_MOVEMENT_TYPES } from '../../constants/config';
import LoadingSpinner from '../common/LoadingSpinner';
import StockMovementForm from './StockMovementForm';

const StockMovementList = ({ canManage, onAdd, refreshTrigger }) => {
  const [movements, setMovements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [openForm, setOpenForm] = useState(false);

  useEffect(() => {
    loadMovements();
  }, [refreshTrigger]);

  const loadMovements = async () => {
    setLoading(true);
    try {
      const data = await inventoryService.getStockMovements();
      setMovements(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getMovementIcon = (type) => {
    switch (type) {
      case 'IN': return <TrendingUp color="success" />;
      case 'OUT': return <TrendingDown color="error" />;
      case 'ADJUSTMENT': return <SwapHoriz color="warning" />;
      case 'RETURN': return <Refresh color="info" />;
      case 'DAMAGED': return <Delete color="error" />;
      default: return <History />;
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
      {/* En-tête avec statistiques rapides */}
      <Card sx={{ mb: 3, borderRadius: 3 }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <History /> Historique des mouvements
            </Typography>
            {canManage && (
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setOpenForm(true)}
                sx={{ borderRadius: 3 }}
              >
                Nouveau mouvement
              </Button>
            )}
          </Stack>

          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Chip
              icon={<TrendingUp />}
              label={`Entrées: ${movements.filter(m => m.movement_type === 'IN').reduce((acc, m) => acc + m.quantity, 0)}`}
              color="success"
              variant="outlined"
            />
            <Chip
              icon={<TrendingDown />}
              label={`Sorties: ${movements.filter(m => m.movement_type === 'OUT').reduce((acc, m) => acc + m.quantity, 0)}`}
              color="error"
              variant="outlined"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Tableau des mouvements */}
      <TableContainer component={Paper} sx={{ borderRadius: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Produit</TableCell>
              <TableCell align="right">Quantité</TableCell>
              <TableCell align="right">Coût total</TableCell>
              <TableCell>Raison</TableCell>
              <TableCell>Fournisseur</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {movements.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((movement) => (
              <TableRow key={movement.id} hover>
                <TableCell>
                  <Typography variant="body2">{formatDate(movement.movement_date)}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatDate(movement.movement_date, 'relative')}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    icon={getMovementIcon(movement.movement_type)}
                    label={STOCK_MOVEMENT_TYPES[movement.movement_type] || movement.movement_type}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>{movement.product_name}</TableCell>
                <TableCell align="right">
                  <Typography
                    fontWeight="bold"
                    color={movement.movement_type === 'IN' ? 'success.main' : 'error.main'}
                  >
                    {movement.movement_type === 'IN' ? '+' : '-'}{movement.quantity}
                  </Typography>
                </TableCell>
                <TableCell align="right">{movement.total_cost ? formatCurrency(movement.total_cost) : '-'}</TableCell>
                <TableCell>{movement.reason || '-'}</TableCell>
                <TableCell>{movement.supplier_name || '-'}</TableCell>
              </TableRow>
            ))}
            {movements.length === 0 && (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                  <Typography variant="body1" color="text.secondary">
                    Aucun mouvement enregistré
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[10, 20, 50]}
          component="div"
          count={movements.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Lignes par page"
        />
      </TableContainer>

      {/* Modal de création de mouvement */}
      <StockMovementForm
        open={openForm}
        onClose={() => setOpenForm(false)}
        onSuccess={() => {
          setOpenForm(false);
          loadMovements();
        }}
      />
    </Box>
  );
};

export default StockMovementList;