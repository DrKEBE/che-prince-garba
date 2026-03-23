// frontend\src\components\sales\Invoice.jsx
import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Divider,
  Button,
  Chip,
  Paper,
} from '@mui/material';
import {
  Print,
  Download,
  Email,
  Receipt,
  Home,
  Phone,
  Email as EmailIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

const Invoice = ({ sale }) => {
  // Vérification de sécurité robuste
  if (!sale) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="error">
          Aucune donnée de vente disponible
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Impossible d'afficher la facture. Veuillez réessayer.
        </Typography>
      </Box>
    );
  }

  // S'assurer que items existe toujours
  const safeItems = sale.items || [];
  
  if (safeItems.length === 0) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6">
          Facture #{sale.invoice_number || 'N/A'}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Aucun article dans cette vente
        </Typography>
      </Box>
    );
  }

  // Formatteur de devises
  const formatCurrency = (value) => {
    const numValue = typeof value === 'number' ? value : parseFloat(value || 0);
    return new Intl.NumberFormat('fr-CI', {
      style: 'currency',
      currency: 'XOF',
      minimumFractionDigits: 0,
    }).format(numValue);
  };

  // Les autres fonctions restent les mêmes...
  const calculateItemTotal = (item) => {
    const price = parseFloat(item.unit_price || 0);
    const discount = parseFloat(item.discount || 0);
    const quantity = parseFloat(item.quantity || 0);
    
    return (price * quantity) - discount;
  };

  const calculateSubtotal = () => {
    return safeItems.reduce((sum, item) => {
      return sum + calculateItemTotal(item);
    }, 0);
  };

  const calculateTotal = () => {
    const subtotal = calculateSubtotal();
    const discount = parseFloat(sale.discount || 0);
    const tax = parseFloat(sale.tax_amount || 0);
    const shipping = parseFloat(sale.shipping_cost || 0);
    
    return subtotal - discount + tax + shipping;
  };


  const handlePrint = () => {
    window.print();
  };

  const handleDownload = () => {
    // TODO: Implement PDF download
    console.log('Download PDF');
  };

  const handleEmail = () => {
    // TODO: Implement email sending
    console.log('Send email');
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper
        sx={{
          p: 4,
          borderRadius: 3,
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
          maxWidth: 800,
          margin: '0 auto',
        }}
      >
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4 }}>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Receipt sx={{ mr: 3, color: 'primary.main', fontSize: 52 }} />
              <Typography variant="h4" fontWeight="bold" className="gradient-text">
                Luxe Beauté
                CHE PRINCE GARBA
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              Institut de beauté & Cosmétiques
            </Typography>
          </Box>
          
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="h5" fontWeight="bold" color="primary.main">
              FACTURE
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {sale.invoice_number}
            </Typography>
            <Chip
              label={sale.payment_status}
              color={
                sale.payment_status === 'PAID' ? 'success' :
                sale.payment_status === 'PENDING' ? 'warning' : 'default'
              }
              size="small"
              sx={{ mt: 1 }}
            />
          </Box>
        </Box>

        {/* Company Info */}
        <Grid container spacing={4} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              De:
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Home sx={{ mr: 1, color: 'text.secondary', fontSize: 16 }} />
              <Typography variant="body2">
                Luxe Beauté Management
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Home sx={{ mr: 1, color: 'text.secondary', fontSize: 16 }} />
              <Typography variant="body2">
                ATT Bougou, en face du 320 logemenet
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Phone sx={{ mr: 1, color: 'text.secondary', fontSize: 16 }} />
              <Typography variant="body2">
                +223 78 20 28 08
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Client:
            </Typography>
            {sale?.client_name ? (
              <>
                <Typography variant="body2" fontWeight="medium">
                  {sale.client_name}
                </Typography>
                {sale.client_phone && (
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <Phone sx={{ mr: 1, color: 'text.secondary', fontSize: 16 }} />
                    <Typography variant="body2">
                      {sale.client_phone}
                    </Typography>
                  </Box>
                )}
                {sale.client_email && (
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                    <EmailIcon sx={{ mr: 1, color: 'text.secondary', fontSize: 16 }} />
                    <Typography variant="body2">
                      {sale.client_email}
                    </Typography>
                  </Box>
                )}
              </>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Client non spécifié
              </Typography>
            )}
          </Grid>
        </Grid>

        {/* Invoice Details */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Date de la vente: {sale?.sale_date ? format(new Date(sale.sale_date), 'dd MMMM yyyy HH:mm', { locale: fr }) : 'N/A'}          </Typography>
          <Typography variant="body2" color="text.secondary">
            Méthode de paiement: {sale.payment_method}
          </Typography>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Items Table */}
        <Box sx={{ mb: 4 }}>
          <Grid container sx={{ py: 1, borderBottom: 1, borderColor: 'divider' }}>
            <Grid item xs={6}>
              <Typography fontWeight="medium">Description</Typography>
            </Grid>
            <Grid item xs={2} sx={{ textAlign: 'right' }}>
              <Typography fontWeight="medium">Quantité</Typography>
            </Grid>
            <Grid item xs={2} sx={{ textAlign: 'right' }}>
              <Typography fontWeight="medium">Prix unitaire</Typography>
            </Grid>
            <Grid item xs={2} sx={{ textAlign: 'right' }}>
              <Typography fontWeight="medium">Total</Typography>
            </Grid>
          </Grid>

          {safeItems.map((item, index) => (
            <Grid
              key={index}
              container
              sx={{
                py: 2,
                borderBottom: 1,
                borderColor: 'divider',
                '&:last-child': { borderBottom: 'none' },
              }}
            >
              <Grid item xs={6}>
                <Typography variant="body2" fontWeight="medium">
                  {item.product_name}
                </Typography>
                {item.discount > 0 && (
                  <Typography variant="caption" color="text.secondary">
                    Remise: {formatCurrency(item.discount)}
                  </Typography>
                )}
              </Grid>
              <Grid item xs={2} sx={{ textAlign: 'right' }}>
                <Typography variant="body2">{item.quantity}</Typography>
              </Grid>
              <Grid item xs={2} sx={{ textAlign: 'right' }}>
                <Typography variant="body2">{formatCurrency(item.unit_price)}</Typography>
              </Grid>
              <Grid item xs={2} sx={{ textAlign: 'right' }}>
                <Typography variant="body2" fontWeight="medium">
                  {formatCurrency(calculateItemTotal(item))}
                </Typography>
              </Grid>
            </Grid>
          ))}
        </Box>

        {/* Totals */}
        <Box sx={{ width: '50%', ml: 'auto' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography color="text.secondary">Sous-total</Typography>
            <Typography>{formatCurrency(calculateSubtotal())}</Typography>
          </Box>

          {sale.discount > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography color="text.secondary">Remise globale</Typography>
              <Typography color="error.main">-{formatCurrency(sale.discount)}</Typography>
            </Box>
          )}

          {sale.tax_amount > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography color="text.secondary">Taxes</Typography>
              <Typography>+{formatCurrency(sale.tax_amount)}</Typography>
            </Box>
          )}

          {sale.shipping_cost > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography color="text.secondary">Frais de livraison</Typography>
              <Typography>+{formatCurrency(sale.shipping_cost)}</Typography>
            </Box>
          )}

          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4 }}>
            <Typography variant="h6" fontWeight="bold">
              Total
            </Typography>
            <Typography variant="h5" fontWeight="bold" color="primary.main">
              {formatCurrency(calculateTotal())}
            </Typography>
          </Box>
        </Box>

        {/* Footer */}
        <Box
          sx={{
            mt: 6,
            pt: 3,
            borderTop: 1,
            borderColor: 'divider',
            textAlign: 'center',
          }}
        >
          <Typography variant="caption" color="text.secondary" paragraph>
            Merci pour votre confiance! Pour toute question concernant cette facture, 
            veuillez contacter notre service client.
          </Typography>
          <Typography variant="caption" color="text.secondary">
            © {new Date().getFullYear()} Luxe Beauté Management - Tous droits réservés
          </Typography>
        </Box>

        {/* Actions */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            gap: 2,
            mt: 4,
            pt: 3,
            borderTop: 1,
            borderColor: 'divider',
          }}
        >
          <Button
            variant="contained"
            startIcon={<Print />}
            onClick={handlePrint}
          >
            Imprimer
          </Button>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={handleDownload}
          >
            Télécharger PDF
          </Button>
          {sale.client_email && (
            <Button
              variant="outlined"
              startIcon={<Email />}
              onClick={handleEmail}
            >
              Envoyer par email
            </Button>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default Invoice;