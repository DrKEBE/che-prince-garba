import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Pagination,
  Stack,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  LinearProgress,
  Avatar,
  Grid,
  Badge,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  SwapHoriz as SwapHorizIcon,
  Delete as DeleteIcon,
  History as HistoryIcon,
  CalendarToday as CalendarIcon,
  AttachMoney as MoneyIcon,
  Inventory as InventoryIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { DataGrid } from '@mui/x-data-grid';
import { formatCurrency, formatDate } from '../../utils/formatters';
import stockService from '../../services/stock';
import { STOCK_MOVEMENT_TYPES } from '../../constants/config';

const StockHistory = ({ productId = null, limit = 20 }) => {
  const [movements, setMovements] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedMovement, setSelectedMovement] = useState(null);
  const [openDetails, setOpenDetails] = useState(false);
  const [dateRange, setDateRange] = useState({
    start: null,
    end: null,
  });

  // Charger les mouvements
  const loadMovements = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = {
        skip: (page - 1) * limit,
        limit,
        ...(productId && { product_id: productId }),
        ...(filterType !== 'all' && { movement_type: filterType }),
        ...(searchTerm && { search: searchTerm }),
      };
      
      const data = await stockService.getMovements(params);
      setMovements(data);
      
      // Calculer le nombre total de pages (approximatif)
      // Dans une vraie application, le backend devrait retourner le total
      const hasMore = data.length === limit;
      setTotalPages(hasMore ? page + 1 : page);
    } catch (err) {
      console.error('Error loading stock movements:', err);
      setError('Impossible de charger l\'historique des mouvements');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMovements();
  }, [page, filterType, productId]);

  // Colonnes pour DataGrid
  const columns = [
    {
      field: 'movement_date',
      headerName: 'Date',
      width: 160,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2" fontWeight="medium">
            {formatDate(params.value, 'short')}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {formatDate(params.value, 'relative')}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'product_name',
      headerName: 'Produit',
      width: 200,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar
            sx={{
              width: 32,
              height: 32,
              bgcolor: 'primary.light',
              color: 'primary.contrastText',
            }}
          >
            <InventoryIcon fontSize="small" />
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight="medium" noWrap>
              {params.row.product_name || 'Produit'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {params.row.sku || 'SKU'}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'movement_type',
      headerName: 'Type',
      width: 130,
      renderCell: (params) => {
        const type = params.value;
        const config = {
          IN: { label: 'Entrée', color: 'success', icon: <ArrowUpwardIcon /> },
          OUT: { label: 'Sortie', color: 'error', icon: <ArrowDownwardIcon /> },
          ADJUSTMENT: { label: 'Ajustement', color: 'warning', icon: <SwapHorizIcon /> },
          RETURN: { label: 'Retour', color: 'info', icon: <RefreshIcon /> },
          DAMAGED: { label: 'Détérioré', color: 'error', icon: <DeleteIcon /> },
        }[type] || { label: type, color: 'default', icon: <InventoryIcon /> };

        return (
          <Chip
            icon={config.icon}
            label={config.label}
            size="small"
            color={config.color}
            variant="outlined"
            sx={{ fontWeight: 'medium' }}
          />
        );
      },
    },
    {
      field: 'quantity',
      headerName: 'Quantité',
      width: 120,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          {params.row.movement_type === 'IN' ? (
            <ArrowUpwardIcon fontSize="small" color="success" />
          ) : (
            <ArrowDownwardIcon fontSize="small" color="error" />
          )}
          <Typography
            variant="body2"
            fontWeight="bold"
            color={params.row.movement_type === 'IN' ? 'success.main' : 'error.main'}
          >
            {params.row.movement_type === 'IN' ? '+' : '-'}{params.value}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'unit_cost',
      headerName: 'Coût unitaire',
      width: 140,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value ? formatCurrency(params.value) : 'N/A'}
        </Typography>
      ),
    },
    {
      field: 'total_cost',
      headerName: 'Coût total',
      width: 140,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="medium">
          {params.value ? formatCurrency(params.value) : 'N/A'}
        </Typography>
      ),
    },
    {
      field: 'reason',
      headerName: 'Raison',
      width: 200,
      renderCell: (params) => (
        <Tooltip title={params.value || ''}>
          <Typography variant="body2" noWrap>
            {params.value || 'N/A'}
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: 'reference',
      headerName: 'Référence',
      width: 150,
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 100,
      renderCell: (params) => (
        <Tooltip title="Voir les détails">
          <IconButton
            size="small"
            onClick={() => {
              setSelectedMovement(params.row);
              setOpenDetails(true);
            }}
          >
            <HistoryIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      ),
    },
  ];

  // Calculer les statistiques
  const calculateStats = () => {
    const stats = {
      total_movements: movements.length,
      total_in: movements.filter(m => m.movement_type === 'IN').reduce((sum, m) => sum + m.quantity, 0),
      total_out: movements.filter(m => m.movement_type === 'OUT').reduce((sum, m) => sum + m.quantity, 0),
      total_cost: movements.reduce((sum, m) => sum + (m.total_cost || 0), 0),
    };
    
    return stats;
  };

  const stats = calculateStats();

  const handleExport = async () => {
    try {
      await stockService.exportStockData('csv', {
        product_id: productId,
        movement_type: filterType !== 'all' ? filterType : undefined,
      });
    } catch (err) {
      console.error('Error exporting stock data:', err);
    }
  };

  return (
    <Box>
      {/* En-tête avec filtres */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
            <Box>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <HistoryIcon />
                Historique des mouvements de stock
              </Typography>
              {productId && (
                <Typography variant="body2" color="text.secondary">
                  Produit spécifique
                </Typography>
              )}
            </Box>
            
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleExport}
              disabled={movements.length === 0}
            >
              Exporter
            </Button>
          </Stack>

          <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
            <TextField
              placeholder="Rechercher..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ flex: 1 }}
            />
            
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Type de mouvement</InputLabel>
              <Select
                value={filterType}
                label="Type de mouvement"
                onChange={(e) => setFilterType(e.target.value)}
              >
                <MenuItem value="all">Tous les types</MenuItem>
                {Object.entries(STOCK_MOVEMENT_TYPES).map(([key, label]) => (
                  <MenuItem key={key} value={key}>{label}</MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Tooltip title="Rafraîchir">
              <IconButton onClick={loadMovements} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Stack>

          {/* Statistiques rapides */}
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Total des mouvements
                </Typography>
                <Typography variant="h5" fontWeight="bold">
                  {stats.total_movements}
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Entrées totales
                </Typography>
                <Typography variant="h5" fontWeight="bold" color="success.main">
                  +{stats.total_in}
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Sorties totales
                </Typography>
                <Typography variant="h5" fontWeight="bold" color="error.main">
                  -{stats.total_out}
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Coût total
                </Typography>
                <Typography variant="h5" fontWeight="bold">
                  {formatCurrency(stats.total_cost)}
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tableau des mouvements */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          {loading ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <LinearProgress sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                Chargement de l'historique...
              </Typography>
            </Box>
          ) : error ? (
            <Alert severity="error" sx={{ m: 2 }}>
              {error}
            </Alert>
          ) : movements.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <HistoryIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Aucun mouvement trouvé
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {searchTerm || filterType !== 'all'
                  ? 'Aucun mouvement ne correspond à vos critères'
                  : 'Commencez par créer des mouvements de stock'}
              </Typography>
            </Box>
          ) : (
            <>
              <Box sx={{ height: 500, width: '100%' }}>
                <DataGrid
                  rows={movements}
                  columns={columns}
                  pageSize={10}
                  rowsPerPageOptions={[10, 25, 50]}
                  disableSelectionOnClick
                  loading={loading}
                  localeText={{
                    noRowsLabel: 'Aucun mouvement disponible',
                    footerTotalRows: 'Total:',
                  }}
                  sx={{
                    border: 'none',
                    '& .MuiDataGrid-columnHeaders': {
                      backgroundColor: 'background.paper',
                    },
                  }}
                />
              </Box>
              
              {/* Pagination */}
              {totalPages > 1 && (
                <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={(event, value) => setPage(value)}
                    color="primary"
                  />
                </Box>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Dialog de détails */}
      <Dialog
        open={openDetails}
        onClose={() => setOpenDetails(false)}
        maxWidth="sm"
        fullWidth
      >
        {selectedMovement && (
          <>
            <DialogTitle>
              <Stack direction="row" alignItems="center" spacing={1}>
                <HistoryIcon />
                <Typography variant="h6">Détails du mouvement</Typography>
              </Stack>
            </DialogTitle>
            <DialogContent dividers>
              <Stack spacing={3}>
                {/* Informations de base */}
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Informations générales
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Date
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {formatDate(selectedMovement.movement_date, 'long')}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Type
                      </Typography>
                      <Chip
                        label={STOCK_MOVEMENT_TYPES[selectedMovement.movement_type] || selectedMovement.movement_type}
                        size="small"
                        color={
                          selectedMovement.movement_type === 'IN' ? 'success' :
                          selectedMovement.movement_type === 'OUT' ? 'error' :
                          selectedMovement.movement_type === 'ADJUSTMENT' ? 'warning' : 'default'
                        }
                      />
                    </Grid>
                  </Grid>
                </Box>

                {/* Produit */}
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Produit
                  </Typography>
                  <Stack direction="row" alignItems="center" spacing={2}>
                    <Avatar
                      sx={{
                        bgcolor: 'primary.light',
                        color: 'primary.contrastText',
                      }}
                    >
                      <InventoryIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="body1" fontWeight="medium">
                        {selectedMovement.product_name || 'Produit inconnu'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        SKU: {selectedMovement.sku || 'N/A'}
                      </Typography>
                    </Box>
                  </Stack>
                </Box>

                {/* Quantités et coûts */}
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Détails quantitatifs
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Quantité
                      </Typography>
                      <Typography variant="h5" fontWeight="bold"
                        color={selectedMovement.movement_type === 'IN' ? 'success.main' : 'error.main'}
                      >
                        {selectedMovement.movement_type === 'IN' ? '+' : '-'}{selectedMovement.quantity}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Coût unitaire
                      </Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {selectedMovement.unit_cost ? formatCurrency(selectedMovement.unit_cost) : 'N/A'}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Coût total
                      </Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {selectedMovement.total_cost ? formatCurrency(selectedMovement.total_cost) : 'N/A'}
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>

                {/* Informations supplémentaires */}
                {(selectedMovement.reason || selectedMovement.reference || selectedMovement.notes) && (
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Informations supplémentaires
                    </Typography>
                    <Stack spacing={1}>
                      {selectedMovement.reason && (
                        <Box>
                          <Typography variant="caption" color="text.secondary" display="block">
                            Raison
                          </Typography>
                          <Typography variant="body2">
                            {selectedMovement.reason}
                          </Typography>
                        </Box>
                      )}
                      {selectedMovement.reference && (
                        <Box>
                          <Typography variant="caption" color="text.secondary" display="block">
                            Référence
                          </Typography>
                          <Typography variant="body2">
                            {selectedMovement.reference}
                          </Typography>
                        </Box>
                      )}
                      {selectedMovement.notes && (
                        <Box>
                          <Typography variant="caption" color="text.secondary" display="block">
                            Notes
                          </Typography>
                          <Typography variant="body2">
                            {selectedMovement.notes}
                          </Typography>
                        </Box>
                      )}
                    </Stack>
                  </Box>
                )}

                {/* Métadonnées */}
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Métadonnées
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Créé le
                      </Typography>
                      <Typography variant="body2">
                        {formatDate(selectedMovement.created_at, 'short')}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Mis à jour le
                      </Typography>
                      <Typography variant="body2">
                        {formatDate(selectedMovement.updated_at, 'short')}
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              </Stack>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setOpenDetails(false)}>
                Fermer
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default StockHistory;