import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Tooltip,
  Chip,
  Grid,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  LinearProgress,
  Divider,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Fab,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  FilterList as FilterListIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  LocalShipping as ReceiveIcon,
  Receipt as ReceiptIcon,
  Business as BusinessIcon,
  CalendarToday as CalendarIcon,
  AttachMoney as MoneyIcon,
} from '@mui/icons-material';
import { DataGrid } from '@mui/x-data-grid';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { motion } from 'framer-motion';

import { inventoryService } from '../../services/inventory';
import { formatCurrency, formatDate } from '../../utils/formatters';
import LoadingSpinner from '../common/LoadingSpinner';
import { useAuth } from '../../context/AuthContext';
import { usePermissions } from '../../hooks/useAuth';
import toast from 'react-hot-toast';

// ------------------------------------------------------------
// Formulaire de création de commande
// ------------------------------------------------------------
const PurchaseOrderForm = ({ open, onClose }) => {
  const queryClient = useQueryClient();
  const [supplierId, setSupplierId] = useState('');
  const [expectedDelivery, setExpectedDelivery] = useState('');
  const [notes, setNotes] = useState('');
  const [items, setItems] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [unitPrice, setUnitPrice] = useState(0);

  const { data: suppliers = [] } = useQuery(
    'suppliers-for-po',
    () => inventoryService.getSuppliers({ active_only: true, limit: 100 }),
    { staleTime: 5 * 60 * 1000 }
  );

  const { data: products = [] } = useQuery(
    'products-for-po',
    () => inventoryService.getProducts({ active_only: true, limit: 100 }),
    { staleTime: 5 * 60 * 1000 }
  );

  const createMutation = useMutation(
    (data) => inventoryService.createPurchaseOrder(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('purchase-orders');
        toast.success('Commande créée avec succès');
        onClose();
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Erreur lors de la création');
      },
    }
  );

  const handleAddItem = () => {
    if (!selectedProduct) {
      toast.error('Veuillez sélectionner un produit');
      return;
    }
    if (quantity <= 0) {
      toast.error('La quantité doit être supérieure à 0');
      return;
    }
    if (unitPrice <= 0) {
      toast.error('Le prix unitaire doit être supérieur à 0');
      return;
    }

    const existingIndex = items.findIndex(
      (item) => item.product_id === selectedProduct.id
    );
    if (existingIndex >= 0) {
      const updated = [...items];
      updated[existingIndex].quantity += quantity;
      setItems(updated);
    } else {
      setItems([
        ...items,
        {
          product_id: selectedProduct.id,
          product_name: selectedProduct.name,
          quantity,
          unit_price: unitPrice,
        },
      ]);
    }

    setSelectedProduct(null);
    setQuantity(1);
    setUnitPrice(0);
  };

  const handleRemoveItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    if (!supplierId) {
      toast.error('Veuillez sélectionner un fournisseur');
      return;
    }
    if (items.length === 0) {
      toast.error('Ajoutez au moins un article');
      return;
    }

    createMutation.mutate({
      supplier_id: supplierId,
      expected_delivery: expectedDelivery || null,
      notes: notes || null,
      items: items.map(({ product_id, quantity, unit_price }) => ({
        product_id,
        quantity,
        unit_price,
      })),
    });
  };

  const totalAmount = items.reduce(
    (sum, item) => sum + item.quantity * item.unit_price,
    0
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <ReceiptIcon color="primary" />
        <Typography variant="h6">Nouvelle commande fournisseur</Typography>
      </DialogTitle>
      <DialogContent dividers>
        <Stack spacing={3}>
          <FormControl fullWidth>
            <InputLabel>Fournisseur *</InputLabel>
            <Select
              value={supplierId}
              onChange={(e) => setSupplierId(e.target.value)}
              label="Fournisseur *"
            >
              {suppliers.map((s) => (
                <MenuItem key={s.id} value={s.id}>
                  {s.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label="Date de livraison prévue"
            type="date"
            value={expectedDelivery}
            onChange={(e) => setExpectedDelivery(e.target.value)}
            InputLabelProps={{ shrink: true }}
            fullWidth
          />

          <TextField
            label="Notes"
            multiline
            rows={2}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            fullWidth
          />

          <Divider />

          <Typography variant="subtitle1" fontWeight="bold">
            Articles commandés
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={5}>
              <FormControl fullWidth size="small">
                <InputLabel>Produit</InputLabel>
                <Select
                  value={selectedProduct?.id || ''}
                  onChange={(e) => {
                    const product = products.find((p) => p.id === e.target.value);
                    setSelectedProduct(product);
                    setUnitPrice(product?.purchase_price || 0);
                  }}
                  label="Produit"
                >
                  {products.map((p) => (
                    <MenuItem key={p.id} value={p.id}>
                      {p.name} (SKU: {p.sku || 'N/A'})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6} sm={2}>
              <TextField
                label="Qté"
                type="number"
                size="small"
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value) || 0)}
                InputProps={{ inputProps: { min: 1 } }}
                fullWidth
              />
            </Grid>
            <Grid item xs={6} sm={3}>
              <TextField
                label="Prix unitaire"
                type="number"
                size="small"
                value={unitPrice}
                onChange={(e) => setUnitPrice(parseFloat(e.target.value) || 0)}
                InputProps={{
                  startAdornment: <InputAdornment position="start">F</InputAdornment>,
                  inputProps: { min: 0, step: 100 },
                }}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={2}>
              <Button
                variant="contained"
                onClick={handleAddItem}
                fullWidth
                sx={{ height: '100%' }}
              >
                Ajouter
              </Button>
            </Grid>
          </Grid>

          {items.length > 0 ? (
            <List>
              {items.map((item, index) => (
                <ListItem
                  key={index}
                  divider
                  secondaryAction={
                    <IconButton edge="end" onClick={() => handleRemoveItem(index)}>
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemText
                    primary={item.product_name}
                    secondary={`Quantité: ${item.quantity} x ${formatCurrency(item.unit_price)} = ${formatCurrency(
                      item.quantity * item.unit_price
                    )}`}
                  />
                </ListItem>
              ))}
              <ListItem>
                <ListItemText
                  primary={<Typography fontWeight="bold">Total</Typography>}
                  secondary={
                    <Typography variant="h6" color="primary.main" fontWeight="bold">
                      {formatCurrency(totalAmount)}
                    </Typography>
                  }
                />
              </ListItem>
            </List>
          ) : (
            <Alert severity="info">Aucun article ajouté.</Alert>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Annuler</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={createMutation.isLoading}
        >
          {createMutation.isLoading ? 'Création...' : 'Créer la commande'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// ------------------------------------------------------------
// Formulaire de réception de commande
// ------------------------------------------------------------
const ReceiveOrderForm = ({ open, onClose, order }) => {
  const queryClient = useQueryClient();
  const [receivedItems, setReceivedItems] = useState([]);

  React.useEffect(() => {
    if (order?.items) {
      setReceivedItems(
        order.items.map((item) => ({
          id: item.id,
          product_name: item.product_name,
          ordered_quantity: item.quantity,
          received_quantity: item.received_quantity || 0,
          unit_price: item.unit_price,
        }))
      );
    }
  }, [order]);

  const receiveMutation = useMutation(
    (data) => inventoryService.receivePurchaseOrder(order.id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('purchase-orders');
        toast.success('Commande réceptionnée avec succès');
        onClose();
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Erreur lors de la réception');
      },
    }
  );

  const handleQuantityChange = (itemId, value) => {
    setReceivedItems(
      receivedItems.map((item) =>
        item.id === itemId
          ? { ...item, received_quantity: Math.max(0, Math.min(item.ordered_quantity, parseInt(value) || 0)) }
          : item
      )
    );
  };

  const handleSubmit = () => {
    const itemsToReceive = receivedItems
      .filter((item) => item.received_quantity > 0)
      .map((item) => ({
        id: item.id,
        received_quantity: item.received_quantity,
      }));

    if (itemsToReceive.length === 0) {
      toast.error('Veuillez saisir au moins une quantité reçue');
      return;
    }

    receiveMutation.mutate(itemsToReceive);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <ReceiveIcon color="success" />
        <Typography variant="h6">Réception de commande</Typography>
      </DialogTitle>
      <DialogContent dividers>
        <Typography variant="subtitle2" gutterBottom>
          Commande n° {order?.order_number}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Fournisseur: {order?.supplier_name}
        </Typography>
        <Divider sx={{ my: 2 }} />
        <Stack spacing={2}>
          {receivedItems.map((item) => (
            <Box key={item.id}>
              <Typography variant="body2" fontWeight="medium">
                {item.product_name}
              </Typography>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Commandé: {item.ordered_quantity}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="Reçu"
                    type="number"
                    size="small"
                    value={item.received_quantity}
                    onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                    InputProps={{ inputProps: { min: 0, max: item.ordered_quantity } }}
                    fullWidth
                  />
                </Grid>
              </Grid>
              <Divider sx={{ my: 1 }} />
            </Box>
          ))}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Annuler</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          color="success"
          disabled={receiveMutation.isLoading}
        >
          {receiveMutation.isLoading ? 'Traitement...' : 'Confirmer la réception'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// ------------------------------------------------------------
// Composant principal : Liste des commandes
// ------------------------------------------------------------
export default function PurchaseOrderList() {
  const { isAdmin, isManager } = useAuth();
  const permissions = usePermissions();
  const canManage = permissions.includes('manage_purchase_orders') || isAdmin || isManager;

  const [filters, setFilters] = useState({
    supplier_id: '',
    status: '',
    start_date: '',
    end_date: '',
    search: '',
  });
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openReceiveDialog, setOpenReceiveDialog] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [openDetailsDialog, setOpenDetailsDialog] = useState(false);

  const queryClient = useQueryClient();

  // Récupération des fournisseurs pour les filtres
  const { data: suppliers = [] } = useQuery(
    'suppliers-for-po-filter',
    () => inventoryService.getSuppliers({ active_only: true, limit: 100 }),
    { staleTime: 5 * 60 * 1000 }
  );

  // Récupération des commandes
  const { data, isLoading, refetch } = useQuery(
    ['purchase-orders', { page, pageSize, ...filters }],
    () => inventoryService.getPurchaseOrders({
      skip: (page - 1) * pageSize,
      limit: pageSize,
      supplier_id: filters.supplier_id || undefined,
      status: filters.status || undefined,
      start_date: filters.start_date || undefined,
      end_date: filters.end_date || undefined,
    }),
    { keepPreviousData: true }
  );

  const deleteMutation = useMutation(
    (id) => inventoryService.deletePurchaseOrder(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('purchase-orders');
        toast.success('Commande supprimée');
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Erreur lors de la suppression');
      },
    }
  );

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const clearFilters = () => {
    setFilters({
      supplier_id: '',
      status: '',
      start_date: '',
      end_date: '',
      search: '',
    });
    setPage(1);
  };

  const handleReceiveClick = (order) => {
    setSelectedOrder(order);
    setOpenReceiveDialog(true);
  };

  const handleDetailsClick = (order) => {
    setSelectedOrder(order);
    setOpenDetailsDialog(true);
  };

  const handleDeleteClick = (id) => {
    if (window.confirm('Supprimer définitivement cette commande ?')) {
      deleteMutation.mutate(id);
    }
  };

  const getStatusChip = (status) => {
    const config = {
      PENDING: { label: 'En attente', color: 'warning' },
      ORDERED: { label: 'Commandé', color: 'info' },
      RECEIVED: { label: 'Reçu', color: 'success' },
      CANCELLED: { label: 'Annulé', color: 'error' },
    };
    const { label, color } = config[status] || { label: status, color: 'default' };
    return <Chip label={label} size="small" color={color} />;
  };

  const columns = [
    {
      field: 'order_number',
      headerName: 'N° Commande',
      width: 160,
      renderCell: (params) => (
        <Typography fontWeight="medium">{params.value}</Typography>
      ),
    },
    {
      field: 'supplier_name',
      headerName: 'Fournisseur',
      width: 200,
    },
    {
      field: 'order_date',
      headerName: 'Date',
      width: 150,
      renderCell: (params) => formatDate(params.value, 'dd/MM/yyyy'),
    },
    {
      field: 'expected_delivery',
      headerName: 'Livraison prévue',
      width: 150,
      renderCell: (params) =>
        params.value ? formatDate(params.value, 'dd/MM/yyyy') : '-',
    },
    {
      field: 'total_amount',
      headerName: 'Total',
      width: 130,
      renderCell: (params) => formatCurrency(params.value || 0),
    },
    {
      field: 'status',
      headerName: 'Statut',
      width: 130,
      renderCell: (params) => getStatusChip(params.value),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 200,
      sortable: false,
      renderCell: (params) => (
        <Stack direction="row" spacing={1}>
          <Tooltip title="Voir détails">
            <IconButton size="small" onClick={() => handleDetailsClick(params.row)}>
              <VisibilityIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          {params.row.status === 'PENDING' && canManage && (
            <>
              <Tooltip title="Modifier (à venir)">
                <IconButton size="small">
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Réceptionner">
                <IconButton
                  size="small"
                  color="success"
                  onClick={() => handleReceiveClick(params.row)}
                >
                  <ReceiveIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Supprimer">
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => handleDeleteClick(params.row.id)}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </>
          )}
          {params.row.status === 'RECEIVED' && (
            <Chip label="Reçu" size="small" color="success" variant="outlined" />
          )}
        </Stack>
      ),
    },
  ];

  if (isLoading) return <LoadingSpinner />;

  return (
    <Box>
      {/* Filtres */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterListIcon /> Filtres
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Recherche"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                  endAdornment: filters.search && (
                    <IconButton size="small" onClick={() => handleFilterChange('search', '')}>
                      <ClearIcon />
                    </IconButton>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Fournisseur</InputLabel>
                <Select
                  value={filters.supplier_id}
                  onChange={(e) => handleFilterChange('supplier_id', e.target.value)}
                  label="Fournisseur"
                >
                  <MenuItem value="">Tous</MenuItem>
                  {suppliers.map((s) => (
                    <MenuItem key={s.id} value={s.id}>
                      {s.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Statut</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  label="Statut"
                >
                  <MenuItem value="">Tous</MenuItem>
                  <MenuItem value="PENDING">En attente</MenuItem>
                  <MenuItem value="ORDERED">Commandé</MenuItem>
                  <MenuItem value="RECEIVED">Reçu</MenuItem>
                  <MenuItem value="CANCELLED">Annulé</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                size="small"
                label="Date début"
                type="date"
                value={filters.start_date}
                onChange={(e) => handleFilterChange('start_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                size="small"
                label="Date fin"
                type="date"
                value={filters.end_date}
                onChange={(e) => handleFilterChange('end_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={1}>
              <Button
                variant="outlined"
                onClick={clearFilters}
                startIcon={<RefreshIcon />}
                fullWidth
              >
                Reset
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tableau des commandes */}
      <Card>
        <CardContent sx={{ p: 0, '&:last-child': { pb: 0 } }}>
          <DataGrid
            rows={data?.data || []}
            columns={columns}
            pageSize={pageSize}
            rowsPerPageOptions={[10, 20, 50, 100]}
            pagination
            paginationMode="server"
            rowCount={data?.total || 0}
            page={page - 1}
            onPageChange={(newPage) => setPage(newPage + 1)}
            onPageSizeChange={(newSize) => setPageSize(newSize)}
            disableSelectionOnClick
            autoHeight
            loading={isLoading}
            localeText={{
              noRowsLabel: 'Aucune commande trouvée',
              footerTotalRows: 'Total:',
            }}
            sx={{
              border: 'none',
              '& .MuiDataGrid-columnHeaders': {
                backgroundColor: 'background.paper',
              },
            }}
          />
        </CardContent>
      </Card>

      {/* Bouton de création */}
      {canManage && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3 }}
          style={{ position: 'fixed', bottom: 32, right: 32 }}
        >
          <Fab
            variant="extended"
            color="primary"
            onClick={() => setOpenCreateDialog(true)}
            sx={{
              bgcolor: 'primary.main',
              '&:hover': { bgcolor: 'primary.dark', transform: 'scale(1.05)' },
              transition: 'all 0.2s',
            }}
          >
            <AddIcon sx={{ mr: 1 }} />
            Nouvelle commande
          </Fab>
        </motion.div>
      )}

      {/* Dialog de création */}
      <PurchaseOrderForm
        open={openCreateDialog}
        onClose={() => setOpenCreateDialog(false)}
      />

      {/* Dialog de réception */}
      {selectedOrder && (
        <ReceiveOrderForm
          open={openReceiveDialog}
          onClose={() => {
            setOpenReceiveDialog(false);
            setSelectedOrder(null);
          }}
          order={selectedOrder}
        />
      )}

      {/* Dialog de détails */}
      <Dialog
        open={openDetailsDialog}
        onClose={() => setOpenDetailsDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}
      >
        <DialogTitle>
          Détails de la commande {selectedOrder?.order_number}
        </DialogTitle>
        <DialogContent dividers>
          {selectedOrder && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Fournisseur
                </Typography>
                <Typography variant="body1" gutterBottom>
                  {selectedOrder.supplier_name}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Date de commande
                </Typography>
                <Typography variant="body1" gutterBottom>
                  {formatDate(selectedOrder.order_date, 'dd/MM/yyyy HH:mm')}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Livraison prévue
                </Typography>
                <Typography variant="body1" gutterBottom>
                  {selectedOrder.expected_delivery
                    ? formatDate(selectedOrder.expected_delivery, 'dd/MM/yyyy')
                    : 'Non spécifiée'}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Statut
                </Typography>
                <Box>{getStatusChip(selectedOrder.status)}</Box>
              </Grid>
              {selectedOrder.notes && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Notes
                  </Typography>
                  <Typography variant="body1">{selectedOrder.notes}</Typography>
                </Grid>
              )}
              <Grid item xs={12}>
                <Divider sx={{ my: 1 }} />
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Articles
                </Typography>
                <List dense>
                  {selectedOrder.items.map((item) => (
                    <ListItem key={item.id}>
                      <ListItemText
                        primary={item.product_name}
                        secondary={`Quantité: ${item.quantity} x ${formatCurrency(
                          item.unit_price
                        )} = ${formatCurrency(item.quantity * item.unit_price)}`}
                      />
                      <Chip
                        label={`Reçu: ${item.received_quantity || 0}/${item.quantity}`}
                        size="small"
                        color={
                          item.received_quantity === item.quantity
                            ? 'success'
                            : item.received_quantity > 0
                            ? 'info'
                            : 'default'
                        }
                      />
                    </ListItem>
                  ))}
                  <ListItem>
                    <ListItemText
                      primary={<Typography fontWeight="bold">Total</Typography>}
                      secondary={
                        <Typography variant="h6" color="primary.main" fontWeight="bold">
                          {formatCurrency(selectedOrder.total_amount)}
                        </Typography>
                      }
                    />
                  </ListItem>
                </List>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDetailsDialog(false)}>Fermer</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}