// frontend\src\pages\Sales.jsx
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Tabs,
  Tab,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Tooltip,
  Grid,
  CircularProgress,
} from '@mui/material';
import {
  Add,
  Receipt,
  Refresh,
  FilterList,
  Print,
  Download,
  Visibility,
  Edit,
  MoneyOff,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import DataTable from '../components/common/DataTable';
import SaleForm from '../components/sales/SaleForm';
import Invoice from '../components/sales/Invoice';
import { saleService } from '../services/sales';
import { useAuth } from '../context/AuthContext';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function Sales() {
  const [tabValue, setTabValue] = useState(0);
  const [openSaleForm, setOpenSaleForm] = useState(false);
  const [selectedSale, setSelectedSale] = useState(null);
  const [viewInvoice, setViewInvoice] = useState(false);
  const [invoiceData, setInvoiceData] = useState(null); // NOUVEAU ÉTAT
  const [invoiceLoading, setInvoiceLoading] = useState(false); // NOUVEAU ÉTAT
  const [startDate, setStartDate] = useState(
    format(new Date().setDate(new Date().getDate() - 30), 'yyyy-MM-dd')
  );
  const [endDate, setEndDate] = useState(format(new Date(), 'yyyy-MM-dd'));

  const { isAdmin, isManager, isCashier } = useAuth();

  const { data: sales, isLoading, refetch } = useQuery(
    ['sales', { start_date: startDate, end_date: endDate }],
    () => saleService.getSales({ start_date: startDate, end_date: endDate }),
    { refetchOnWindowFocus: false }
  );

  const { data: dailyStats } = useQuery(
    'daily-sales',
    saleService.getDailySales,
    { refetchInterval: 60000 }
  );

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleOpenSaleForm = (sale = null) => {
    setSelectedSale(sale);
    setOpenSaleForm(true);
  };

  const handleCloseSaleForm = () => {
    setOpenSaleForm(false);
    setSelectedSale(null);
    refetch();
  };

  const handleViewInvoice = async (sale) => {
    try {
      setInvoiceLoading(true);
      // Récupérer les données complètes avec les items
      const fullSaleData = await saleService.getSaleById(sale.id);
      setInvoiceData(fullSaleData);
      setViewInvoice(true);
    } catch (error) {
      console.error('Erreur récupération facture:', error);
      // Vous pouvez ajouter une notification ici
      toast.error('Impossible de charger la facture');
    } finally {
      setInvoiceLoading(false);
    }
  };

  const handleCloseInvoice = () => {
    setViewInvoice(false);
    setSelectedSale(null);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-CI', {
      style: 'currency',
      currency: 'XOF',
      minimumFractionDigits: 0,
    }).format(value);
  };

  const getPaymentStatusColor = (status) => {
    switch (status) {
      case 'PAID':
        return 'success';
      case 'PENDING':
        return 'warning';
      case 'PARTIAL':
        return 'info';
      default:
        return 'default';
    }
  };

  const columns = [
    {
      field: 'invoice_number',
      headerName: 'Facture',
      flex: 1,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2" fontWeight="medium">
            {params.row.invoice_number}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {format(new Date(params.row.sale_date), 'dd MMM yyyy HH:mm', {
              locale: fr,
            })}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'client',
      headerName: 'Client',
      flex: 1,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.row.client_name || 'Non spécifié'}
        </Typography>
      ),
    },
    {
      field: 'amount',
      headerName: 'Montant',
      flex: 1,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="medium">
          {formatCurrency(params.row.final_amount)}
        </Typography>
      ),
    },
    {
      field: 'payment',
      headerName: 'Paiement',
      flex: 1,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2">{params.row.payment_method}</Typography>
          <Chip
            label={params.row.payment_status}
            size="small"
            color={getPaymentStatusColor(params.row.payment_status)}
            sx={{ height: 20, fontSize: '0.7rem' }}
          />
        </Box>
      ),
    },
    {
      field: 'profit',
      headerName: 'Profit',
      flex: 1,
      renderCell: (params) => (
        <Typography
          variant="body2"
          color={params.row.total_profit > 0 ? 'success.main' : 'error.main'}
          fontWeight="medium"
        >
          {formatCurrency(params.row.total_profit)}
        </Typography>
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      flex: 1,
      renderCell: (params) => (
        <Box>
          <Tooltip title="Voir facture">
            <IconButton
              size="small"
              onClick={() => handleViewInvoice(params.row)}
            >
              <Receipt fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Détails">
            <IconButton
              size="small"
              onClick={() => handleOpenSaleForm(params.row)}
            >
              <Visibility fontSize="small" />
            </IconButton>
          </Tooltip>
          {params.row.is_refundable && (
            <Tooltip title="Remboursement">
              <IconButton size="small" color="warning">
                <MoneyOff fontSize="small" />
              </IconButton>
            </Tooltip>
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
            Gestion des ventes
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {dailyStats ? `${dailyStats.total_sales} ventes aujourd'hui` : 'Chargement...'}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => refetch()}
          >
            Actualiser
          </Button>
          {(isAdmin || isManager || isCashier) && (
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => handleOpenSaleForm()}
              sx={{
                bgcolor: 'primary.main',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
              }}
            >
              Nouvelle vente
            </Button>
          )}
        </Box>
      </Box>

      {/* Stats Cards */}
      {dailyStats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" color="primary.main">
                  {formatCurrency(dailyStats.total_amount)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Chiffre d'affaires
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" color="success.main">
                  {dailyStats.total_items}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Articles vendus
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" color="info.main">
                  {formatCurrency(dailyStats.total_profit)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Profit total
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" color="warning.main">
                  {formatCurrency(dailyStats.avg_ticket)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Panier moyen
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Toutes les ventes" />
              <Tab label="En attente" />
              <Tab label="Remboursements" />
              <Tab label="Rapports" />
            </Tabs>
          </Box>
        </CardContent>
      </Card>

      {/* Sales Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card>
          <CardContent sx={{ p: 0 }}>
            <DataTable
              rows={sales || []}
              columns={columns}
              loading={isLoading}
              getRowId={(row) => row.id}
              pageSize={10}
              rowsPerPageOptions={[10, 25, 50]}
              checkboxSelection={false}
              sx={{ height: 600 }}
            />
          </CardContent>
        </Card>
      </motion.div>

      {/* Sale Form Dialog */}
      {/* Sale Form Dialog */}
      <Dialog
        open={openSaleForm}
        onClose={handleCloseSaleForm}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            minHeight: '80vh',
          },
        }}
      >
        <DialogTitle>
          {selectedSale ? 'Détails de la vente' : 'Nouvelle vente'}
        </DialogTitle>
        <DialogContent dividers>
          <SaleForm
            sale={selectedSale}
            onSuccess={handleCloseSaleForm}
            onCancel={handleCloseSaleForm}
          />
        </DialogContent>
      </Dialog>

      {/* Invoice Dialog */}
      <Dialog
        open={viewInvoice}
        onClose={handleCloseInvoice}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
          },
        }}
      >
        <DialogContent sx={{ p: 0 }}>
          {invoiceLoading ? (
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center',
                minHeight: 400 
              }}
            >
              <Box sx={{ textAlign: 'center' }}>
                <CircularProgress size={60} />
                <Typography variant="body2" sx={{ mt: 2 }}>
                  Chargement de la facture...
                </Typography>
              </Box>
            </Box>
          ) : invoiceData ? (
            <Invoice sale={invoiceData} />
          ) : (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="error" gutterBottom>
                Erreur de chargement
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Impossible de charger les données de la facture.
              </Typography>
              <Button 
                variant="outlined" 
                sx={{ mt: 2 }}
                onClick={handleCloseInvoice}
              >
                Fermer
              </Button>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
}