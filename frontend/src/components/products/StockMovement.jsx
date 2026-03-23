// frontend/src/components/products/StockMovement.jsx (version améliorée)

import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Chip,
  Stack,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress,
  Grid,
  Tooltip,
  Paper,
  InputAdornment,
  Tabs,
  Tab,
  Fade,
  Grow,
} from '@mui/material';
import {
  Add as AddIcon,
  Inventory as InventoryIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  SwapHoriz as SwapHorizIcon,
  History as HistoryIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  AttachMoney as MoneyIcon,
  FilterList as FilterListIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  Download as DownloadIcon,
  Timeline as TimelineIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { DataGrid } from '@mui/x-data-grid';
import { frFR } from '@mui/x-data-grid/locales';
import { formatCurrency, formatDate } from '../../utils/formatters';
import { productService } from '../../services/products';
import { STOCK_MOVEMENT_TYPES } from '../../constants/config';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 24,
    },
  },
};

const COLORS = ['#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#8A2BE2'];

const StockMovement = ({ productId, productName, productPurchasePrice, onMovementCreated }) => {
  const queryClient = useQueryClient();
  const [openDialog, setOpenDialog] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [newMovement, setNewMovement] = useState({
    product_id: productId,
    movement_type: 'IN',
    quantity: 1,
    reason: '',
    reference: '',
    supplier_id: '',
    notes: '',
    expiration_date: '',
  });

  // Effet pour réinitialiser le formulaire si le produit change
  useEffect(() => {
    setNewMovement(prev => ({
      ...prev,
      product_id: productId,
    }));
  }, [productId]);

  // Calcul du coût unitaire automatique selon le type et le prix d'achat
  const getAutoUnitCost = () => {
    if (['IN', 'OUT', 'ADJUSTMENT', 'DAMAGED', 'RETURN'].includes(newMovement.movement_type)) {
      return productPurchasePrice ? parseFloat(productPurchasePrice) : 0;
    }
    return null; // Pas de coût pour les autres types
  };

  // Coût total calculé
  const totalCost = useMemo(() => {
    const unitCost = getAutoUnitCost();
    return unitCost ? unitCost * newMovement.quantity : 0;
  }, [newMovement.movement_type, newMovement.quantity, productPurchasePrice]);

  // Vérification que le prix d'achat est défini pour les entrées
  const isPurchasePriceMissing = () => {
    return ['IN', 'RETURN'].includes(newMovement.movement_type) && 
           (!productPurchasePrice || productPurchasePrice <= 0);
  };

  // Charger les mouvements
  const {
    data: movements = [],
    isLoading,
    error,
    refetch,
  } = useQuery(
    ['productMovements', productId],
    () => productService.getProductMovements(productId),
    {
      enabled: !!productId,
      refetchOnWindowFocus: false,
      select: (data) => {
        return data.sort((a, b) => new Date(b.movement_date) - new Date(a.movement_date));
      },
    }
  );

  // Mutation pour créer un mouvement
  const createMovementMutation = useMutation(
    (movementData) => productService.createStockMovement(movementData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['productMovements', productId]);
        toast.success('Mouvement enregistré avec succès');
        setOpenDialog(false);
        resetForm();
        if (onMovementCreated) onMovementCreated();
      },
      onError: (err) => {
        toast.error(err.response?.data?.detail || 'Erreur lors de la création');
      },
    }
  );

  // Calculs statistiques
  const stats = useMemo(() => {
    let stockIn = 0,
      stockOut = 0,
      totalValue = 0,
      lastMovement = null;
    const monthlyData = {};
    const typeCount = { IN: 0, OUT: 0, ADJUSTMENT: 0, RETURN: 0, DAMAGED: 0 };

    movements.forEach((m) => {
      const month = new Date(m.movement_date).toLocaleString('default', {
        month: 'short',
        year: 'numeric',
      });
      if (!monthlyData[month]) {
        monthlyData[month] = { month, IN: 0, OUT: 0, ADJUSTMENT: 0, RETURN: 0, DAMAGED: 0 };
      }
      monthlyData[month][m.movement_type] += m.quantity;

      if (['IN', 'RETURN', 'ADJUSTMENT'].includes(m.movement_type)) {
        stockIn += m.quantity;
        totalValue += m.total_cost || m.quantity * (m.unit_cost || 0);
      } else {
        stockOut += m.quantity;
        totalValue -= m.total_cost || m.quantity * (m.unit_cost || 0);
      }

      typeCount[m.movement_type]++;

      if (!lastMovement || new Date(m.movement_date) > new Date(lastMovement.movement_date)) {
        lastMovement = m;
      }
    });

    const currentStock = stockIn - stockOut;
    const stockValue = totalValue;

    return {
      currentStock,
      stockValue,
      stockIn,
      stockOut,
      lastMovement,
      monthlyData: Object.values(monthlyData).sort(
        (a, b) => new Date(a.month) - new Date(b.month)
      ),
      typeCount,
    };
  }, [movements]);

  // Mouvements filtrés
  const filteredMovements = useMemo(() => {
    return movements.filter((m) => {
      const matchesSearch =
        searchTerm === '' ||
        m.reason?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.reference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.notes?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = filterType === 'all' || m.movement_type === filterType;
      const matchesDate =
        (!dateRange.start || new Date(m.movement_date) >= new Date(dateRange.start)) &&
        (!dateRange.end || new Date(m.movement_date) <= new Date(dateRange.end));
      return matchesSearch && matchesType && matchesDate;
    });
  }, [movements, searchTerm, filterType, dateRange]);

  const resetForm = () => {
    setNewMovement({
      product_id: productId,
      movement_type: 'IN',
      quantity: 1,
      reason: '',
      reference: '',
      supplier_id: '',
      notes: '',
      expiration_date: '',
    });
  };

  const handleCreateMovement = () => {
    if (newMovement.quantity <= 0) {
      toast.error('La quantité doit être supérieure à 0');
      return;
    }

    // Vérification du prix d'achat pour les entrées
    if (isPurchasePriceMissing()) {
      toast.error('Le prix d\'achat du produit n\'est pas défini. Veuillez d\'abord renseigner un prix d\'achat.');
      return;
    }

    // Préparer les données : on ajoute unit_cost seulement si pertinent
    const movementData = {
      product_id: newMovement.product_id,
      movement_type: newMovement.movement_type,
      quantity: newMovement.quantity,
    };

    // Ajouter le coût unitaire automatique pour les types concernés
    const autoUnitCost = getAutoUnitCost();
    if (autoUnitCost !== null) {
      movementData.unit_cost = autoUnitCost;
    }

    // Ajouter les champs optionnels s'ils sont remplis
    if (newMovement.reason) movementData.reason = newMovement.reason;
    if (newMovement.reference) movementData.reference = newMovement.reference;
    if (newMovement.supplier_id) movementData.supplier_id = newMovement.supplier_id;
    if (newMovement.notes) movementData.notes = newMovement.notes;
    if (newMovement.expiration_date) movementData.expiration_date = newMovement.expiration_date;

    createMovementMutation.mutate(movementData);
  };

  const handleInputChange = (field, value) => {
    setNewMovement((prev) => ({ ...prev, [field]: value }));
  };

  const getStockStatusColor = (stock) => {
    if (stock <= 0) return 'error';
    if (stock <= 5) return 'warning';
    return 'success';
  };

  // Colonnes pour la DataGrid
  const columns = [
    {
      field: 'movement_date',
      headerName: 'Date',
      width: 160,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2">{formatDate(params.value, 'short')}</Typography>
          <Typography variant="caption" color="text.secondary">
            {formatDate(params.value, 'relative')}
          </Typography>
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
          IN: { label: 'Entrée', color: 'success', icon: <ArrowUpwardIcon fontSize="small" /> },
          OUT: { label: 'Sortie', color: 'error', icon: <ArrowDownwardIcon fontSize="small" /> },
          ADJUSTMENT: { label: 'Ajustement', color: 'warning', icon: <SwapHorizIcon fontSize="small" /> },
          RETURN: { label: 'Retour', color: 'info', icon: <RefreshIcon fontSize="small" /> },
          DAMAGED: { label: 'Détérioré', color: 'error', icon: <DeleteIcon fontSize="small" /> },
        }[type] || { label: type, color: 'default', icon: <InventoryIcon fontSize="small" /> };

        return (
          <Chip
            icon={config.icon}
            label={config.label}
            size="small"
            color={config.color}
            variant="outlined"
            sx={{ fontWeight: 'medium', borderRadius: 2 }}
          />
        );
      },
    },
    {
      field: 'quantity',
      headerName: 'Quantité',
      width: 110,
      renderCell: (params) => {
        const isPositive = ['IN', 'RETURN', 'ADJUSTMENT'].includes(params.row.movement_type);
        return (
          <Typography
            variant="body2"
            color={isPositive ? 'success.main' : 'error.main'}
            fontWeight="bold"
          >
            {isPositive ? '+' : '-'}
            {params.value}
          </Typography>
        );
      },
    },
    {
      field: 'unit_cost',
      headerName: 'Coût unitaire',
      width: 130,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value ? formatCurrency(params.value) : '—'}
        </Typography>
      ),
    },
    {
      field: 'total_cost',
      headerName: 'Coût total',
      width: 130,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="medium">
          {params.value ? formatCurrency(params.value) : '—'}
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
            {params.value || '—'}
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: 'reference',
      headerName: 'Référence',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2" color="text.secondary">
          {params.value || '—'}
        </Typography>
      ),
    },
    {
      field: 'created_at',
      headerName: 'Enregistré le',
      width: 150,
      renderCell: (params) => (
        <Typography variant="caption" color="text.secondary">
          {formatDate(params.value, 'relative')}
        </Typography>
      ),
    },
  ];

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      {/* En-tête avec statistiques */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <motion.div variants={itemVariants}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                borderRadius: 4,
                background: 'linear-gradient(135deg, #8A2BE2 0%, #9D4EDD 100%)',
                color: 'white',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <Box sx={{ position: 'absolute', top: -10, right: -10, opacity: 0.1 }}>
                <InventoryIcon sx={{ fontSize: 100 }} />
              </Box>
              <Typography variant="overline" sx={{ opacity: 0.8 }}>
                Stock actuel
              </Typography>
              <Typography variant="h3" fontWeight="bold">
                {stats.currentStock}
              </Typography>
              <Chip
                label={stats.currentStock <= 0 ? 'Rupture' : stats.currentStock <= 5 ? 'Faible' : 'Normal'}
                size="small"
                color={getStockStatusColor(stats.currentStock)}
                sx={{ mt: 1, backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }}
              />
            </Paper>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div variants={itemVariants}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                borderRadius: 4,
                background: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
                color: 'white',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <Box sx={{ position: 'absolute', top: -10, right: -10, opacity: 0.1 }}>
                <MoneyIcon sx={{ fontSize: 100 }} />
              </Box>
              <Typography variant="overline" sx={{ opacity: 0.8 }}>
                Valeur du stock
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {formatCurrency(stats.stockValue)}
              </Typography>
            </Paper>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div variants={itemVariants}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                borderRadius: 4,
                background: 'linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)',
                color: 'white',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <Box sx={{ position: 'absolute', top: -10, right: -10, opacity: 0.1 }}>
                <ArrowUpwardIcon sx={{ fontSize: 100 }} />
              </Box>
              <Typography variant="overline" sx={{ opacity: 0.8 }}>
                Entrées totales
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {stats.stockIn}
              </Typography>
            </Paper>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={3}>
          <motion.div variants={itemVariants}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                borderRadius: 4,
                background: 'linear-gradient(135deg, #EF4444 0%, #F87171 100%)',
                color: 'white',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <Box sx={{ position: 'absolute', top: -10, right: -10, opacity: 0.1 }}>
                <ArrowDownwardIcon sx={{ fontSize: 100 }} />
              </Box>
              <Typography variant="overline" sx={{ opacity: 0.8 }}>
                Sorties totales
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {stats.stockOut}
              </Typography>
            </Paper>
          </motion.div>
        </Grid>
      </Grid>

      {/* Onglets : Historique / Graphiques avec bouton Nouveau mouvement */}
      <Card sx={{ mb: 3, borderRadius: 4, overflow: 'hidden' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', px: 3, pt: 2 }}>
          <Tabs
            value={activeTab}
            onChange={(e, v) => setActiveTab(v)}
            sx={{ '& .MuiTab-root': { minWidth: 120 } }}
          >
            <Tab icon={<HistoryIcon />} label="Historique" iconPosition="start" />
            <Tab icon={<TimelineIcon />} label="Tendances" iconPosition="start" />
            <Tab icon={<PieChart />} label="Répartition" iconPosition="start" />
          </Tabs>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
            sx={{ borderRadius: 8, px: 3 }}
          >
            Nouveau mouvement
          </Button>
        </Box>
        <Divider />

        <CardContent>
          {/* Onglet Historique */}
          {activeTab === 0 && (
            <Fade in timeout={500}>
              <Box>
                {/* Barre de filtres */}
                <Stack direction="row" spacing={2} sx={{ mb: 3 }} alignItems="center">
                  <TextField
                    size="small"
                    placeholder="Rechercher..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon fontSize="small" />
                        </InputAdornment>
                      ),
                      endAdornment: searchTerm && (
                        <InputAdornment position="end">
                          <IconButton size="small" onClick={() => setSearchTerm('')}>
                            <ClearIcon fontSize="small" />
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                    sx={{ minWidth: 250 }}
                  />

                  <FormControl size="small" sx={{ minWidth: 150 }}>
                    <InputLabel>Type</InputLabel>
                    <Select
                      value={filterType}
                      label="Type"
                      onChange={(e) => setFilterType(e.target.value)}
                    >
                      <MenuItem value="all">Tous</MenuItem>
                      {Object.entries(STOCK_MOVEMENT_TYPES).map(([key, label]) => (
                        <MenuItem key={key} value={key}>
                          {label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <TextField
                    size="small"
                    type="date"
                    label="Du"
                    value={dateRange.start}
                    onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                    InputLabelProps={{ shrink: true }}
                  />
                  <TextField
                    size="small"
                    type="date"
                    label="Au"
                    value={dateRange.end}
                    onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                    InputLabelProps={{ shrink: true }}
                  />

                  <Box sx={{ flex: 1 }} />

                  <Tooltip title="Exporter">
                    <IconButton onClick={() => {}}>
                      <DownloadIcon />
                    </IconButton>
                  </Tooltip>
                </Stack>

                {/* Tableau */}
                {isLoading ? (
                  <Box sx={{ p: 4, textAlign: 'center' }}>
                    <LinearProgress sx={{ mb: 2 }} />
                    <Typography variant="body2" color="text.secondary">
                      Chargement de l'historique...
                    </Typography>
                  </Box>
                ) : error ? (
                  <Alert severity="error" sx={{ borderRadius: 2 }}>
                    {error.message}
                  </Alert>
                ) : filteredMovements.length === 0 ? (
                  <Box sx={{ p: 6, textAlign: 'center' }}>
                    <InventoryIcon sx={{ fontSize: 80, color: 'grey.400', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      Aucun mouvement trouvé
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {searchTerm || filterType !== 'all' || dateRange.start
                        ? 'Essayez de modifier vos filtres'
                        : 'Commencez par créer un mouvement'}
                    </Typography>
                  </Box>
                ) : (
                  <Box sx={{ height: 450, width: '100%' }}>
                    <DataGrid
                      rows={filteredMovements}
                      columns={columns}
                      pageSize={10}
                      rowsPerPageOptions={[10, 25, 50, 100]}
                      disableSelectionOnClick
                      loading={isLoading}
                      localeText={frFR.components.MuiDataGrid.defaultProps.localeText}
                      sx={{
                        border: 'none',
                        '& .MuiDataGrid-columnHeaders': {
                          backgroundColor: 'background.paper',
                          borderBottom: '2px solid',
                          borderColor: 'divider',
                        },
                      }}
                    />
                  </Box>
                )}
              </Box>
            </Fade>
          )}

          {/* Onglet Tendances */}
          {activeTab === 1 && (
            <Fade in timeout={500}>
              <Box sx={{ height: 400 }}>
                {stats.monthlyData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={stats.monthlyData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="colorIn" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10B981" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorOut" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#EF4444" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <ChartTooltip />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="IN"
                        stroke="#10B981"
                        fillOpacity={1}
                        fill="url(#colorIn)"
                        name="Entrées"
                      />
                      <Area
                        type="monotone"
                        dataKey="OUT"
                        stroke="#EF4444"
                        fillOpacity={1}
                        fill="url(#colorOut)"
                        name="Sorties"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography color="text.secondary">
                      Pas assez de données pour afficher les tendances
                    </Typography>
                  </Box>
                )}
              </Box>
            </Fade>
          )}

          {/* Onglet Répartition */}
          {activeTab === 2 && (
            <Fade in timeout={500}>
              <Box sx={{ height: 400, display: 'flex', justifyContent: 'center' }}>
                {movements.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={Object.entries(stats.typeCount)
                          .filter(([_, count]) => count > 0)
                          .map(([type, count]) => ({
                            name: STOCK_MOVEMENT_TYPES[type] || type,
                            value: count,
                          }))}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(entry) => `${entry.name}: ${entry.value}`}
                        outerRadius={150}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {Object.entries(stats.typeCount)
                          .filter(([_, count]) => count > 0)
                          .map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                      </Pie>
                      <ChartTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography color="text.secondary">
                      Aucune donnée de répartition
                    </Typography>
                  </Box>
                )}
              </Box>
            </Fade>
          )}
        </CardContent>
      </Card>

      {/* Dialog pour créer un mouvement */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 4,
            overflow: 'hidden',
          },
        }}
        TransitionComponent={Grow}
      >
        <DialogTitle sx={{ bgcolor: 'primary.main', color: 'white', py: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AddIcon />
            <Typography variant="h6">Nouveau mouvement de stock</Typography>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ mt: 2 }}>
          <Grid container spacing={3}>
            {/* Section 1 : Type et quantité */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <InventoryIcon fontSize="small" /> Type et quantité
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Type de mouvement</InputLabel>
                <Select
                  value={newMovement.movement_type}
                  label="Type de mouvement"
                  onChange={(e) => handleInputChange('movement_type', e.target.value)}
                >
                  {Object.entries(STOCK_MOVEMENT_TYPES).map(([key, label]) => (
                    <MenuItem key={key} value={key}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {key === 'IN' && <ArrowUpwardIcon color="success" />}
                        {key === 'OUT' && <ArrowDownwardIcon color="error" />}
                        {key === 'ADJUSTMENT' && <SwapHorizIcon color="warning" />}
                        {key === 'RETURN' && <RefreshIcon color="info" />}
                        {key === 'DAMAGED' && <DeleteIcon color="error" />}
                        {label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Quantité"
                type="number"
                fullWidth
                value={newMovement.quantity}
                onChange={(e) => handleInputChange('quantity', parseInt(e.target.value) || 0)}
                InputProps={{
                  inputProps: { min: 1 },
                  startAdornment: <InputAdornment position="start"><InventoryIcon color="action" /></InputAdornment>,
                }}
              />
            </Grid>

            {/* Section 2 : Informations financières (lecture seule) */}
            <Grid item xs={12}>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                <MoneyIcon fontSize="small" /> Impact financier
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Coût unitaire"
                fullWidth
                value={getAutoUnitCost() !== null ? formatCurrency(getAutoUnitCost()) : 'Non applicable'}
                InputProps={{ readOnly: true, startAdornment: <InputAdornment position="start"><InfoIcon color="action" /></InputAdornment> }}
                variant="filled"
                size="small"
                helperText="Basé sur le prix d'achat du produit"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Coût total estimé"
                fullWidth
                value={totalCost > 0 ? formatCurrency(totalCost) : '—'}
                InputProps={{ readOnly: true, startAdornment: <InputAdornment position="start"><MoneyIcon color="action" /></InputAdornment> }}
                variant="filled"
                size="small"
              />
            </Grid>

            {/* Section 3 : Détails du mouvement */}
            <Grid item xs={12}>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2" color="primary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <HistoryIcon fontSize="small" /> Détails
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Raison"
                fullWidth
                value={newMovement.reason}
                onChange={(e) => handleInputChange('reason', e.target.value)}
                placeholder="Ex: Réapprovisionnement, Vente, etc."
                InputProps={{ startAdornment: <InputAdornment position="start"><HistoryIcon color="action" /></InputAdornment> }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Référence"
                fullWidth
                value={newMovement.reference}
                onChange={(e) => handleInputChange('reference', e.target.value)}
                placeholder="Numéro de commande, facture..."
                InputProps={{ startAdornment: <InputAdornment position="start"><FilterListIcon color="action" /></InputAdornment> }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                label="Date d'expiration"
                type="date"
                fullWidth
                value={newMovement.expiration_date}
                onChange={(e) => handleInputChange('expiration_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
                InputProps={{ startAdornment: <InputAdornment position="start"><TimelineIcon color="action" /></InputAdornment> }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Notes"
                fullWidth
                multiline
                rows={3}
                value={newMovement.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                placeholder="Informations complémentaires"
                InputProps={{
                  startAdornment: <InputAdornment position="start" sx={{ alignSelf: 'flex-start', mt: 1 }}><HistoryIcon color="action" /></InputAdornment>,
                }}
              />
            </Grid>
          </Grid>

          {/* Alerte si prix d'achat manquant */}
          {isPurchasePriceMissing() && (
            <Alert severity="warning" sx={{ mt: 3, borderRadius: 2 }}>
              <Typography variant="body2">
                <strong>Attention :</strong> Le prix d'achat de ce produit n'est pas défini.
                Veuillez d'abord renseigner un prix d'achat dans la fiche produit avant de faire une entrée.
              </Typography>
            </Alert>
          )}

          {/* Résumé du mouvement */}
          {newMovement.quantity > 0 && !isPurchasePriceMissing() && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
              <Alert
                severity="info"
                icon={<MoneyIcon />}
                sx={{ mt: 3, borderRadius: 3, border: '1px solid', borderColor: 'info.light' }}
              >
                <Typography variant="subtitle2" gutterBottom>
                  Résumé du mouvement
                </Typography>
                <Stack direction="row" spacing={4} flexWrap="wrap">
                  <Box>
                    <Typography variant="caption" color="text.secondary">Type</Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {STOCK_MOVEMENT_TYPES[newMovement.movement_type]}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">Quantité</Typography>
                    <Typography variant="body2" fontWeight="bold" color={['IN', 'RETURN', 'ADJUSTMENT'].includes(newMovement.movement_type) ? 'success.main' : 'error.main'}>
                      {['IN', 'RETURN', 'ADJUSTMENT'].includes(newMovement.movement_type) ? '+' : '-'}
                      {newMovement.quantity}
                    </Typography>
                  </Box>
                  {totalCost > 0 && (
                    <Box>
                      <Typography variant="caption" color="text.secondary">Coût total</Typography>
                      <Typography variant="body2" fontWeight="bold">{formatCurrency(totalCost)}</Typography>
                    </Box>
                  )}
                </Stack>
              </Alert>
            </motion.div>
          )}
        </DialogContent>

        <DialogActions sx={{ p: 3, pt: 0 }}>
          <Button onClick={() => setOpenDialog(false)} disabled={createMovementMutation.isLoading}>
            Annuler
          </Button>
          <Button
            variant="contained"
            onClick={handleCreateMovement}
            disabled={
              createMovementMutation.isLoading ||
              newMovement.quantity <= 0 ||
              isPurchasePriceMissing()
            }
            startIcon={
              createMovementMutation.isLoading ? (
                <LinearProgress size={20} color="inherit" />
              ) : newMovement.movement_type === 'IN' ? (
                <ArrowUpwardIcon />
              ) : (
                <ArrowDownwardIcon />
              )
            }
            sx={{ bgcolor: 'primary.main', '&:hover': { bgcolor: 'primary.dark' } }}
          >
            {createMovementMutation.isLoading ? 'Enregistrement...' : 'Enregistrer le mouvement'}
          </Button>
        </DialogActions>
      </Dialog>
    </motion.div>
  );
};

export default StockMovement;