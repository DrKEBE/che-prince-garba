// frontend\src\components\sales\RefundForm.jsx
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Box,
  Stack,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Checkbox,
  FormControlLabel,
  Alert,
  Divider,
  useTheme
} from '@mui/material';
import {
  Close as CloseIcon,
  ArrowBack as ArrowBackIcon,
  ArrowForward as ArrowForwardIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Inventory as InventoryIcon,
  MoneyOff as MoneyOffIcon,
  Receipt as ReceiptIcon
} from '@mui/icons-material';
import PropTypes from 'prop-types';
import { saleService } from '../../services/sales';
import { formatCurrency, formatDate } from '../../utils/formatters';
import { REFUND_STATUS, REFUND_REASONS, REFUND_METHODS } from '../../constants/config';

const steps = ['Sélection des articles', 'Détails du remboursement', 'Confirmation'];

const RefundForm = ({ open, onClose, saleId, onSuccess }) => {
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [saleInfo, setSaleInfo] = useState(null);
  const [selectedItems, setSelectedItems] = useState([]);
  const [refundData, setRefundData] = useState({
    refund_reason: '',
    refund_method: 'CASH',
    notes: '',
    issue_credit_note: false
  });
  const [partialQuantities, setPartialQuantities] = useState({});

  // Charger les articles remboursables
  useEffect(() => {
    if (open && saleId) {
      loadRefundableItems();
    }
  }, [open, saleId]);

  const loadRefundableItems = async () => {
    try {
      setLoading(true);
      const data = await saleService.getRefundableItems(saleId);
      setSaleInfo(data);
      
      // Initialiser les quantités partielles
      const initialQuantities = {};
      data.items.forEach(item => {
        initialQuantities[item.sale_item_id] = item.refundable_quantity;
      });
      setPartialQuantities(initialQuantities);
    } catch (err) {
      setError('Erreur lors du chargement des articles');
    } finally {
      setLoading(false);
    }
  };

  const handleItemToggle = (item) => {
    const isSelected = selectedItems.some(i => i.sale_item_id === item.sale_item_id);
    if (isSelected) {
      setSelectedItems(prev => prev.filter(i => i.sale_item_id !== item.sale_item_id));
    } else {
      setSelectedItems(prev => [...prev, { ...item, refund_quantity: item.refundable_quantity }]);
    }
  };

  const handleQuantityChange = (itemId, quantity) => {
    const maxQty = saleInfo.items.find(i => i.sale_item_id === itemId)?.refundable_quantity || 0;
    const validQty = Math.max(1, Math.min(quantity, maxQty));
    
    setPartialQuantities(prev => ({
      ...prev,
      [itemId]: validQty
    }));

    setSelectedItems(prev =>
      prev.map(item =>
        item.sale_item_id === itemId
          ? { ...item, refund_quantity: validQty }
          : item
      )
    );
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setRefundData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const calculateTotalRefund = () => {
    return selectedItems.reduce((total, item) => {
      const quantity = item.refund_quantity || 1;
      return total + (item.unit_price * quantity);
    }, 0);
  };

  const handleNext = () => {
    if (activeStep === 0 && selectedItems.length === 0) {
      setError('Veuillez sélectionner au moins un article');
      return;
    }
    setError(null);
    setActiveStep(prev => prev + 1);
  };

  const handleBack = () => {
    setError(null);
    setActiveStep(prev => prev - 1);
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      const items = selectedItems.map(item => ({
        sale_item_id: item.sale_item_id,
        quantity: item.refund_quantity,
        refund_price: item.unit_price,
        reason: refundData.refund_reason,
        restocked: true // Par défaut, retour en stock
      }));

      const payload = {
        refund_amount: calculateTotalRefund(),
        refund_reason: refundData.refund_reason,
        refund_method: refundData.refund_method,
        items,
        notes: refundData.notes,
        issue_credit_note: refundData.issue_credit_note
      };

      await saleService.createRefund(saleId, payload);
      
      onSuccess?.({
        message: 'Remboursement créé avec succès',
        refundAmount: calculateTotalRefund()
      });
      
      handleClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du remboursement');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setActiveStep(0);
    setSelectedItems([]);
    setRefundData({
      refund_reason: '',
      refund_method: 'CASH',
      notes: '',
      issue_credit_note: false
    });
    setError(null);
    onClose?.();
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderItemsStep();
      case 1:
        return renderDetailsStep();
      case 2:
        return renderConfirmationStep();
      default:
        return null;
    }
  };

  const renderItemsStep = () => (
    <>
      {saleInfo && (
        <Box mb={3}>
          <Card variant="outlined" sx={{ mb: 2 }}>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Vente #{saleInfo.invoice_number}
                  </Typography>
                  <Typography variant="h6">
                    {saleInfo.client_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(saleInfo.sale_date, 'DD/MM/YYYY HH:mm')}
                  </Typography>
                </Box>
                <Box textAlign="right">
                  <Typography variant="body2" color="text.secondary">
                    Montant total
                  </Typography>
                  <Typography variant="h6" color="primary">
                    {formatCurrency(saleInfo.total_amount)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Déjà remboursé: {formatCurrency(saleInfo.already_refunded)}
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>

          <Typography variant="subtitle1" gutterBottom fontWeight={600}>
            Articles remboursables ({saleInfo.items.length})
          </Typography>

          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      indeterminate={
                        selectedItems.length > 0 &&
                        selectedItems.length < saleInfo.items.length
                      }
                      checked={selectedItems.length === saleInfo.items.length}
                      onChange={() => {
                        if (selectedItems.length === saleInfo.items.length) {
                          setSelectedItems([]);
                        } else {
                          setSelectedItems(saleInfo.items.map(item => ({
                            ...item,
                            refund_quantity: item.refundable_quantity
                          })));
                        }
                      }}
                    />
                  </TableCell>
                  <TableCell>Produit</TableCell>
                  <TableCell align="right">Prix unitaire</TableCell>
                  <TableCell align="center">Quantité</TableCell>
                  <TableCell align="right">Total</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {saleInfo.items.map((item) => {
                  const isSelected = selectedItems.some(i => i.sale_item_id === item.sale_item_id);
                  const quantity = partialQuantities[item.sale_item_id] || item.refundable_quantity;
                  
                  return (
                    <TableRow
                      key={item.sale_item_id}
                      hover
                      sx={{
                        bgcolor: isSelected ? theme.palette.action.selected : 'inherit'
                      }}
                    >
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={isSelected}
                          onChange={() => handleItemToggle(item)}
                        />
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight={600}>
                            {item.product_name}
                          </Typography>
                          {item.product_sku && (
                            <Typography variant="caption" color="text.secondary">
                              SKU: {item.product_sku}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(item.unit_price)}
                      </TableCell>
                      <TableCell align="center">
                        <Stack direction="row" alignItems="center" spacing={1}>
                          {isSelected ? (
                            <>
                              <IconButton
                                size="small"
                                onClick={() => handleQuantityChange(item.sale_item_id, quantity - 1)}
                                disabled={quantity <= 1}
                              >
                                -
                              </IconButton>
                              <TextField
                                size="small"
                                value={quantity}
                                onChange={(e) => handleQuantityChange(item.sale_item_id, parseInt(e.target.value) || 1)}
                                sx={{ width: 60 }}
                                inputProps={{ style: { textAlign: 'center' } }}
                              />
                              <IconButton
                                size="small"
                                onClick={() => handleQuantityChange(item.sale_item_id, quantity + 1)}
                                disabled={quantity >= item.refundable_quantity}
                              >
                                +
                              </IconButton>
                            </>
                          ) : (
                            <Typography>
                              {item.refundable_quantity}/{item.quantity}
                            </Typography>
                          )}
                        </Stack>
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(item.unit_price * quantity)}
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          size="small"
                          label={`Stock: ${item.current_stock}`}
                          variant="outlined"
                          color={item.current_stock < 10 ? 'warning' : 'default'}
                        />
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {selectedItems.length > 0 && (
        <Alert severity="info" icon={<MoneyOffIcon />}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography>
              Total sélectionné: {selectedItems.length} article(s)
            </Typography>
            <Typography variant="h6" color="primary">
              {formatCurrency(calculateTotalRefund())}
            </Typography>
          </Stack>
        </Alert>
      )}
    </>
  );

  const renderDetailsStep = () => (
    <Stack spacing={3}>
      <Box>
        <Typography variant="subtitle1" gutterBottom fontWeight={600}>
          Résumé du remboursement
        </Typography>
        <Card variant="outlined">
          <CardContent>
            <Stack spacing={2}>
              {selectedItems.map((item, index) => (
                <Stack
                  key={index}
                  direction="row"
                  justifyContent="space-between"
                  alignItems="center"
                >
                  <Box>
                    <Typography variant="body2">
                      {item.product_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {item.refund_quantity} × {formatCurrency(item.unit_price)}
                    </Typography>
                  </Box>
                  <Typography variant="body2" fontWeight={600}>
                    {formatCurrency(item.unit_price * item.refund_quantity)}
                  </Typography>
                </Stack>
              ))}
              <Divider />
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="h6">Total remboursement</Typography>
                <Typography variant="h5" color="error">
                  {formatCurrency(calculateTotalRefund())}
                </Typography>
              </Stack>
            </Stack>
          </CardContent>
        </Card>
      </Box>

      <Stack spacing={2}>
        <FormControl fullWidth>
          <InputLabel>Raison du remboursement</InputLabel>
          <Select
            name="refund_reason"
            value={refundData.refund_reason}
            onChange={handleInputChange}
            label="Raison du remboursement"
            required
          >
            {Object.entries(REFUND_REASONS).map(([key, label]) => (
              <MenuItem key={key} value={key}>
                {label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>Méthode de remboursement</InputLabel>
          <Select
            name="refund_method"
            value={refundData.refund_method}
            onChange={handleInputChange}
            label="Méthode de remboursement"
          >
            {Object.entries(REFUND_METHODS).map(([key, label]) => (
              <MenuItem key={key} value={key}>
                {label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <TextField
          name="notes"
          label="Notes supplémentaires"
          value={refundData.notes}
          onChange={handleInputChange}
          multiline
          rows={3}
          fullWidth
        />

        <FormControlLabel
          control={
            <Checkbox
              name="issue_credit_note"
              checked={refundData.issue_credit_note}
              onChange={handleInputChange}
            />
          }
          label="Émettre un avoir pour le client"
        />
      </Stack>
    </Stack>
  );

  const renderConfirmationStep = () => (
    <Stack spacing={3} alignItems="center" textAlign="center">
      <Box
        sx={{
          width: 80,
          height: 80,
          borderRadius: '50%',
          bgcolor: theme.palette.success.light,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 2
        }}
      >
        <CheckCircleIcon sx={{ fontSize: 48, color: 'white' }} />
      </Box>

      <Box>
        <Typography variant="h5" gutterBottom>
          Confirmation du remboursement
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Vous êtes sur le point de créer un remboursement de
        </Typography>
        <Typography variant="h3" color="error" gutterBottom>
          {formatCurrency(calculateTotalRefund())}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          pour {selectedItems.length} article(s)
        </Typography>
      </Box>

      <Card variant="outlined" sx={{ width: '100%' }}>
        <CardContent>
          <Stack spacing={1}>
            <Stack direction="row" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                Numéro de vente
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {saleInfo?.invoice_number}
              </Typography>
            </Stack>
            <Stack direction="row" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                Client
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {saleInfo?.client_name}
              </Typography>
            </Stack>
            <Stack direction="row" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                Méthode
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {REFUND_METHODS[refundData.refund_method]}
              </Typography>
            </Stack>
            <Stack direction="row" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                Raison
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {REFUND_REASONS[refundData.refund_reason]}
              </Typography>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      <Alert severity="warning" sx={{ width: '100%' }}>
        Cette action ne peut pas être annulée. Les articles retournés seront remis en stock.
      </Alert>
    </Stack>
  );

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          minHeight: 500
        }
      }}
    >
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h5" fontWeight={600}>
              Nouveau remboursement
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Étape {activeStep + 1} sur {steps.length}
            </Typography>
          </Box>
          <IconButton onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </Stack>
      </DialogTitle>

      <Divider />

      <DialogContent>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {renderStepContent()}
      </DialogContent>

      <Divider />

      <DialogActions sx={{ p: 3 }}>
        <Button
          onClick={handleBack}
          disabled={activeStep === 0 || loading}
          startIcon={<ArrowBackIcon />}
        >
          Retour
        </Button>
        
        <Box flex={1} />
        
        {activeStep === steps.length - 1 ? (
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={loading}
            startIcon={<CheckCircleIcon />}
            color="error"
            size="large"
          >
            Confirmer le remboursement
          </Button>
        ) : (
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={loading || (activeStep === 0 && selectedItems.length === 0)}
            endIcon={<ArrowForwardIcon />}
          >
            Continuer
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

RefundForm.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  saleId: PropTypes.string.isRequired,
  onSuccess: PropTypes.func
};

export default RefundForm;