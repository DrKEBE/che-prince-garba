import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Box,
  Typography,
  Alert,
  LinearProgress,
  Chip,
  Divider,
  Stepper,
  Step,
  StepLabel,
  Autocomplete,
} from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  SwapHoriz as SwapHorizIcon,
  Inventory as InventoryIcon,
  AttachMoney as MoneyIcon,
  CalendarToday as CalendarIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { fr } from 'date-fns/locale';
import { formatCurrency } from '../../utils/formatters';
import { STOCK_MOVEMENT_TYPES } from '../../constants/config';

const StockMovementForm = ({ open, onClose, onSubmit, product, loading }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [movement, setMovement] = useState({
    product_id: product?.id || '',
    movement_type: 'IN',
    quantity: 1,
    unit_cost: product?.purchase_price || 0,
    reason: '',
    reference: '',
    supplier_id: '',
    notes: '',
    expiration_date: null,
    movement_date: new Date(),
  });
  const [errors, setErrors] = useState({});
  const [selectedProduct, setSelectedProduct] = useState(product || null);
  const [availableProducts, setAvailableProducts] = useState([]);

  const steps = ['Sélection du produit', 'Type et quantité', 'Détails'];

  // Simuler la récupération des produits
  useEffect(() => {
    if (open) {
      // En production, on ferait un appel API
      const mockProducts = [
        { id: '1', name: 'Crème Hydratante Luxe', sku: 'CHL-001', purchase_price: 25000 },
        { id: '2', name: 'Parfum Exclusif', sku: 'PE-002', purchase_price: 45000 },
        { id: '3', name: 'Sérum Anti-âge', sku: 'SAA-003', purchase_price: 35000 },
      ];
      setAvailableProducts(mockProducts);
    }
  }, [open]);

  useEffect(() => {
    if (product) {
      setSelectedProduct(product);
      setMovement(prev => ({
        ...prev,
        product_id: product.id,
        unit_cost: product.purchase_price || prev.unit_cost,
      }));
    }
  }, [product]);

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const validateStep = (step) => {
    const newErrors = {};
    
    switch (step) {
      case 0:
        if (!movement.product_id) {
          newErrors.product_id = 'Veuillez sélectionner un produit';
        }
        break;
      case 1:
        if (!movement.movement_type) {
          newErrors.movement_type = 'Veuillez sélectionner un type';
        }
        if (!movement.quantity || movement.quantity <= 0) {
          newErrors.quantity = 'La quantité doit être supérieure à 0';
        }
        break;
      case 2:
        if (!movement.reason) {
          newErrors.reason = 'Veuillez indiquer une raison';
        }
        break;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateStep(activeStep)) {
      const submissionData = {
        ...movement,
        movement_date: movement.movement_date.toISOString(),
        expiration_date: movement.expiration_date ? movement.expiration_date.toISOString() : null,
      };
      onSubmit(submissionData);
    }
  };

  const handleChange = (field, value) => {
    setMovement(prev => ({ ...prev, [field]: value }));
    // Effacer l'erreur pour ce champ
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const handleProductSelect = (product) => {
    setSelectedProduct(product);
    handleChange('product_id', product?.id || '');
    handleChange('unit_cost', product?.purchase_price || 0);
  };

  const getMovementIcon = (type) => {
    switch (type) {
      case 'IN': return <AddIcon color="success" />;
      case 'OUT': return <RemoveIcon color="error" />;
      case 'ADJUSTMENT': return <SwapHorizIcon color="warning" />;
      default: return <InventoryIcon />;
    }
  };

  const getMovementColor = (type) => {
    switch (type) {
      case 'IN': return 'success';
      case 'OUT': return 'error';
      case 'ADJUSTMENT': return 'warning';
      default: return 'default';
    }
  };

  const getMovementDescription = (type) => {
    switch (type) {
      case 'IN': return 'Ajouter du stock (réception, retour, etc.)';
      case 'OUT': return 'Retirer du stock (vente, perte, etc.)';
      case 'ADJUSTMENT': return 'Ajuster le stock (inventaire, correction)';
      case 'RETURN': return 'Retour client';
      case 'DAMAGED': return 'Produit endommagé';
      default: return '';
    }
  };

  const calculateTotalCost = () => {
    return (movement.quantity || 0) * (movement.unit_cost || 0);
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Sélectionnez le produit concerné par le mouvement
            </Typography>
            
            <FormControl fullWidth sx={{ mt: 2 }} error={!!errors.product_id}>
              <Autocomplete
                options={availableProducts}
                getOptionLabel={(option) => `${option.name} (${option.sku})`}
                value={selectedProduct}
                onChange={(event, newValue) => handleProductSelect(newValue)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Produit"
                    error={!!errors.product_id}
                    helperText={errors.product_id}
                    placeholder="Rechercher un produit..."
                  />
                )}
                renderOption={(props, option) => (
                  <li {...props}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <InventoryIcon color="primary" />
                      <Box>
                        <Typography variant="body1">{option.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          SKU: {option.sku} • Prix: {formatCurrency(option.purchase_price)}
                        </Typography>
                      </Box>
                    </Box>
                  </li>
                )}
              />
            </FormControl>

            {selectedProduct && (
              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Informations du produit
                </Typography>
                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Nom:</Typography>
                    <Typography variant="body2">{selectedProduct.name}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">SKU:</Typography>
                    <Typography variant="body2">{selectedProduct.sku}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Prix d'achat:</Typography>
                    <Typography variant="body2">{formatCurrency(selectedProduct.purchase_price)}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">Stock actuel:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {selectedProduct.current_stock || 0} unités
                    </Typography>
                  </Grid>
                </Grid>
              </Alert>
            )}
          </motion.div>
        );

      case 1:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Définissez le type et la quantité du mouvement
            </Typography>

            <Grid container spacing={3} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <FormControl fullWidth error={!!errors.movement_type}>
                  <InputLabel>Type de mouvement</InputLabel>
                  <Select
                    value={movement.movement_type}
                    label="Type de mouvement"
                    onChange={(e) => handleChange('movement_type', e.target.value)}
                  >
                    {Object.entries(STOCK_MOVEMENT_TYPES).map(([key, label]) => (
                      <MenuItem key={key} value={key}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getMovementIcon(key)}
                          {label}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                  {errors.movement_type && (
                    <Typography variant="caption" color="error" sx={{ mt: 1 }}>
                      {errors.movement_type}
                    </Typography>
                  )}
                </FormControl>

                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    {getMovementDescription(movement.movement_type)}
                  </Typography>
                </Alert>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  label="Quantité"
                  type="number"
                  fullWidth
                  value={movement.quantity}
                  onChange={(e) => handleChange('quantity', parseInt(e.target.value) || 0)}
                  error={!!errors.quantity}
                  helperText={errors.quantity || "Nombre d'unités"}
                  InputProps={{
                    inputProps: { min: 1 },
                  }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  label="Coût unitaire (FCFA)"
                  type="number"
                  fullWidth
                  value={movement.unit_cost}
                  onChange={(e) => handleChange('unit_cost', parseFloat(e.target.value) || 0)}
                  InputProps={{
                    startAdornment: <MoneyIcon color="action" sx={{ mr: 1 }} />,
                  }}
                />
              </Grid>
            </Grid>

            {/* Résumé du coût */}
            <Card sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Récapitulatif
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Quantité totale:
                  </Typography>
                  <Typography variant="h6">
                    {movement.quantity} unités
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    Coût total:
                  </Typography>
                  <Typography variant="h6" color="primary.main" fontWeight="bold">
                    {formatCurrency(calculateTotalCost())}
                  </Typography>
                </Grid>
              </Grid>
            </Card>
          </motion.div>
        );

      case 2:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Ajoutez des détails supplémentaires sur le mouvement
            </Typography>

            <Grid container spacing={3} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  label="Raison"
                  fullWidth
                  value={movement.reason}
                  onChange={(e) => handleChange('reason', e.target.value)}
                  error={!!errors.reason}
                  helperText={errors.reason || "Ex: Réapprovisionnement, Vente client, Inventaire..."}
                  required
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  label="Référence"
                  fullWidth
                  value={movement.reference}
                  onChange={(e) => handleChange('reference', e.target.value)}
                  helperText="Numéro de commande, de facture, etc."
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={fr}>
                  <DatePicker
                    label="Date du mouvement"
                    value={movement.movement_date}
                    onChange={(date) => handleChange('movement_date', date)}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </LocalizationProvider>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  label="Notes"
                  fullWidth
                  multiline
                  rows={3}
                  value={movement.notes}
                  onChange={(e) => handleChange('notes', e.target.value)}
                  helperText="Informations complémentaires"
                />
              </Grid>

              <Grid item xs={12}>
                <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={fr}>
                  <DatePicker
                    label="Date d'expiration (optionnel)"
                    value={movement.expiration_date}
                    onChange={(date) => handleChange('expiration_date', date)}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        fullWidth
                        helperText="Pour les produits avec date de péremption"
                      />
                    )}
                  />
                </LocalizationProvider>
              </Grid>
            </Grid>

            {/* Récapitulatif final */}
            <Card sx={{ mt: 3, p: 2, bgcolor: 'primary.light', color: 'white' }}>
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Récapitulatif du mouvement
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography variant="caption">Produit:</Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {selectedProduct?.name || 'Non sélectionné'}
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="caption">Type:</Typography>
                  <Chip
                    icon={getMovementIcon(movement.movement_type)}
                    label={STOCK_MOVEMENT_TYPES[movement.movement_type]}
                    color={getMovementColor(movement.movement_type)}
                    size="small"
                    sx={{ color: 'white' }}
                  />
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="caption">Quantité:</Typography>
                  <Typography variant="h6" fontWeight="bold">
                    {movement.quantity}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Divider sx={{ my: 1, bgcolor: 'rgba(255,255,255,0.3)' }} />
                  <Typography variant="body2">
                    Coût total: {formatCurrency(calculateTotalCost())}
                  </Typography>
                </Grid>
              </Grid>
            </Card>
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          minHeight: '70vh',
        },
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <InventoryIcon color="primary" />
          <Typography variant="h6" fontWeight="bold">
            {product ? 'Ajuster le stock' : 'Nouveau mouvement de stock'}
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {/* Stepper */}
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <LinearProgress sx={{ width: '100%' }} />
          </Box>
        ) : (
          renderStepContent(activeStep)
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3, justifyContent: 'space-between' }}>
        <Box>
          {activeStep > 0 && (
            <Button onClick={handleBack} disabled={loading}>
              Retour
            </Button>
          )}
        </Box>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button onClick={onClose} disabled={loading}>
            Annuler
          </Button>
          
          {activeStep < steps.length - 1 ? (
            <Button
              variant="contained"
              onClick={handleNext}
              disabled={loading}
            >
              Suivant
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={loading}
              startIcon={<CheckCircleIcon />}
              sx={{
                background: 'linear-gradient(135deg, #FF9EB5 0%, #C7B9FF 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #FF8DA5 0%, #B5A8FF 100%)',
                },
              }}
            >
              {loading ? 'Enregistrement...' : 'Enregistrer le mouvement'}
            </Button>
          )}
        </Box>
      </DialogActions>
    </Dialog>
  );
};

export default StockMovementForm;