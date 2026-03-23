import React from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Typography,
  LinearProgress,
  Alert,
} from '@mui/material';
import { formatCurrency, formatDate } from '../../utils/formatters';

const StockMovementHistory = ({ movements, loading, error }) => {
  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
          Chargement de l'historique...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!movements || movements.length === 0) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          Aucun mouvement de stock enregistré.
        </Typography>
      </Box>
    );
  }

  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Date</TableCell>
            <TableCell>Type</TableCell>
            <TableCell align="right">Quantité</TableCell>
            <TableCell align="right">Coût unitaire</TableCell>
            <TableCell align="right">Coût total</TableCell>
            <TableCell>Raison</TableCell>
            <TableCell>Référence</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {movements.map((movement) => (
            <TableRow key={movement.id}>
              <TableCell>
                <Typography variant="body2">
                  {formatDate(movement.movement_date, 'short')}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatDate(movement.movement_date, 'relative')}
                </Typography>
              </TableCell>
              <TableCell>
                <Chip
                  label={movement.movement_type}
                  size="small"
                  color={movement.movement_type === 'IN' ? 'success' : 'error'}
                  variant="outlined"
                />
              </TableCell>
              <TableCell align="right">
                <Typography
                  variant="body2"
                  fontWeight="bold"
                  color={movement.movement_type === 'IN' ? 'success.main' : 'error.main'}
                >
                  {movement.movement_type === 'IN' ? '+' : '-'}{movement.quantity}
                </Typography>
              </TableCell>
              <TableCell align="right">
                {movement.unit_cost ? formatCurrency(movement.unit_cost) : '—'}
              </TableCell>
              <TableCell align="right">
                {movement.total_cost ? formatCurrency(movement.total_cost) : '—'}
              </TableCell>
              <TableCell>{movement.reason || '—'}</TableCell>
              <TableCell>{movement.reference || '—'}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default StockMovementHistory;