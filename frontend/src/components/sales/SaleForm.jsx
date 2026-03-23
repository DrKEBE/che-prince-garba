import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  TextField,
  Button,
  Autocomplete,
  IconButton,
  Typography,
  Divider,
  Chip,
  Alert,
  Paper,
  InputAdornment,
  MenuItem,
} from '@mui/material';
import {
  Add,
  Delete,
  Search,
  Person,
  LocalOffer,
  Receipt,
  Calculate,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { saleService } from '../../services/sales';
import { productService } from '../../services/products';
import { clientService } from '../../services/clients';
import toast from 'react-hot-toast';

const validationSchema = Yup.object({
  client_id: Yup.string(),
  payment_method: Yup.string().required('La méthode de paiement est requise'),
  discount: Yup.number().min(0, 'La remise ne peut pas être négative'),
  tax_amount: Yup.number().min(0, 'Les taxes ne peuvent pas être négatives'),
  shipping_cost: Yup.number().min(0, 'Les frais ne peuvent pas être négatifs'),
  notes: Yup.string(),
  items: Yup.array()
    .of(
      Yup.object({
        product_id: Yup.string().required('Produit requis'),
        quantity: Yup.number()
          .required('Quantité requise')
          .min(1, 'Minimum 1'),
        unit_price: Yup.number()
          .required('Prix requis')
          .min(0, 'Prix non valide'),
        discount: Yup.number().min(0, 'Remise non valide'),
      })
    )
    .min(1, 'Au moins un article est requis'),
});

const SaleForm = ({ sale, onSuccess, onCancel }) => {
  const [products, setProducts] = useState([]);
  const [clients, setClients] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const queryClient = useQueryClient();

  const isEdit = !!sale;

  // Fetch products
  const { data: productsData } = useQuery(
    ['products', 'sale-form'],
    () => productService.getProducts({ include_inactive: false }),
    { refetchOnWindowFocus: false }
  );

  // Fetch clients
  const { data: clientsData } = useQuery(
    ['clients', 'sale-form'],
    () => clientService.getClients(),
    { refetchOnWindowFocus: false }
  );

  useEffect(() => {
    if (productsData) {
      setProducts(productsData);
    }
  }, [productsData]);

  useEffect(() => {
    if (clientsData) {
      setClients(clientsData);
    }
  }, [clientsData]);

  const createMutation = useMutation(
    (data) => saleService.createSale(data),
    {
      onSuccess: (response) => {
        queryClient.invalidateQueries('sales');
        toast.success('Vente créée avec succès!');
        onSuccess();
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Erreur lors de la création');
      },
    }
  );

  const formik = useFormik({
    initialValues: {
      client_id: sale?.client_id || '',
      payment_method: sale?.payment_method || 'CASH',
      discount: sale?.discount || 0,
      tax_amount: sale?.tax_amount || 0,
      shipping_cost: sale?.shipping_cost || 0,
      notes: sale?.notes || '',
      items: sale?.items?.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit_price: item.unit_price,
        discount: item.discount || 0,
      })) || [],
    },
    validationSchema,
    onSubmit: (values) => {
      createMutation.mutate(values);
    },
  });

  const addProductItem = () => {
    if (!selectedProduct) {
      toast.error('Veuillez sélectionner un produit');
      return;
    }

    const currentStock = selectedProduct.current_stock || 0;
    if (currentStock <= 0) {
      toast.error('Produit en rupture de stock');
      return;
    }

    const existingItemIndex = formik.values.items.findIndex(
      item => item.product_id === selectedProduct.id
    );

    if (existingItemIndex >= 0) {
      const items = [...formik.values.items];
      const existingItem = items[existingItemIndex];
      
      if (existingItem.quantity + 1 > currentStock) {
        toast.error(`Stock insuffisant. Disponible: ${currentStock}`);
        return;
      }

      items[existingItemIndex] = {
        ...existingItem,
        quantity: existingItem.quantity + 1,
      };
      formik.setFieldValue('items', items);
    } else {
      if (1 > currentStock) {
        toast.error(`Stock insuffisant. Disponible: ${currentStock}`);
        return;
      }

      const newItem = {
        product_id: selectedProduct.id,
        quantity: 1,
        unit_price: selectedProduct.selling_price,
        discount: 0,
      };
      
      formik.setFieldValue('items', [...formik.values.items, newItem]);
    }

    setSelectedProduct(null);
    setSearchTerm('');
  };

  const removeItem = (index) => {
    const items = [...formik.values.items];
    items.splice(index, 1);
    formik.setFieldValue('items', items);
  };

  const updateItem = (index, field, value) => {
    const items = [...formik.values.items];
    const product = products.find(p => p.id === items[index].product_id);
    
    if (field === 'quantity' && product) {
      const currentStock = product.current_stock || 0;
      if (value > currentStock) {
        toast.error(`Stock insuffisant. Disponible: ${currentStock}`);
        return;
      }
    }

    items[index] = { ...items[index], [field]: value };
    formik.setFieldValue('items', items);
  };

  const calculateItemTotal = (item) => {
    const price = parseFloat(item.unit_price || 0);
    const discount = parseFloat(item.discount || 0);
    const quantity = parseFloat(item.quantity || 0);
    
    return (price * quantity) - discount;
  };

  const calculateSubtotal = () => {
    return formik.values.items.reduce((sum, item) => {
      return sum + calculateItemTotal(item);
    }, 0);
  };

  const calculateTotal = () => {
    const subtotal = calculateSubtotal();
    const discount = parseFloat(formik.values.discount || 0);
    const tax = parseFloat(formik.values.tax_amount || 0);
    const shipping = parseFloat(formik.values.shipping_cost || 0);
    
    return subtotal - discount + tax + shipping;
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-CI', {
      style: 'currency',
      currency: 'XOF',
      minimumFractionDigits: 0,
    }).format(value);
  };

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.sku?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box component="form" onSubmit={formik.handleSubmit}>
      <Grid container spacing={3}>
        {/* Left Column - Product Selection */}
        <Grid item xs={12} md={8}>
          {/* Client Selection */}
          <Paper sx={{ p: 2, mb: 3, borderRadius: 2 }}>
            <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
              Client
            </Typography>
            <Autocomplete
              options={clients}
              getOptionLabel={(option) => `${option.full_name} - ${option.phone}`}
              value={clients.find(c => c.id === formik.values.client_id) || null}
              onChange={(_, value) => {
                formik.setFieldValue('client_id', value?.id || '');
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  placeholder="Rechercher un client..."
                  InputProps={{
                    ...params.InputProps,
                    startAdornment: (
                      <>
                        <Person sx={{ mr: 1, color: 'text.secondary' }} />
                        {params.InputProps.startAdornment}
                      </>
                    ),
                  }}
                />
              )}
            />
          </Paper>

          {/* Product Search */}
          <Paper sx={{ p: 2, mb: 3, borderRadius: 2 }}>
            <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
              Ajouter des produits
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Autocomplete
                fullWidth
                options={filteredProducts}
                getOptionLabel={(option) => `${option.name} - Stock: ${option.current_stock || 0}`}
                value={selectedProduct}
                onChange={(_, value) => setSelectedProduct(value)}
                inputValue={searchTerm}
                onInputChange={(_, value) => setSearchTerm(value)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    placeholder="Rechercher un produit..."
                    size="small"
                  />
                )}
                renderOption={(props, option) => (
                  <li {...props}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                      <Box>
                        <Typography variant="body2">
                          {option.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {option.sku} • Stock: {option.current_stock || 0}
                        </Typography>
                      </Box>
                      <Typography variant="body2" fontWeight="medium">
                        {formatCurrency(option.selling_price)}
                      </Typography>
                    </Box>
                  </li>
                )}
              />
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={addProductItem}
                disabled={!selectedProduct}
              >
                Ajouter
              </Button>
            </Box>

            {/* Product List */}
            <AnimatePresence>
              {formik.values.items.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Receipt sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                    <Typography color="text.secondary">
                      Aucun produit ajouté
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Commencez par rechercher et ajouter des produits
                    </Typography>
                  </Box>
                </motion.div>
              ) : (
                <Box>
                  {formik.values.items.map((item, index) => {
                    const product = products.find(p => p.id === item.product_id);
                    return (
                      <motion.div
                        key={`${item.product_id}-${index}`}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        layout
                      >
                        <Paper sx={{ p: 2, mb: 1, borderRadius: 2 }}>
                          <Grid container alignItems="center" spacing={2}>
                            <Grid item xs={12} sm={4}>
                              <Typography variant="body2" fontWeight="medium">
                                {product?.name || 'Produit inconnu'}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                Stock: {product?.current_stock || 0}
                              </Typography>
                            </Grid>
                            <Grid item xs={6} sm={2}>
                              <TextField
                                size="small"
                                type="number"
                                label="Quantité"
                                value={item.quantity}
                                onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 1)}
                                inputProps={{ min: 1 }}
                                fullWidth
                              />
                            </Grid>
                            <Grid item xs={6} sm={2}>
                              <TextField
                                size="small"
                                type="number"
                                label="Prix unitaire"
                                value={item.unit_price}
                                onChange={(e) => updateItem(index, 'unit_price', parseFloat(e.target.value) || 0)}
                                InputProps={{
                                  startAdornment: (
                                    <InputAdornment position="start">F</InputAdornment>
                                  ),
                                }}
                                fullWidth
                              />
                            </Grid>
                            <Grid item xs={6} sm={2}>
                              <TextField
                                size="small"
                                type="number"
                                label="Remise"
                                value={item.discount}
                                onChange={(e) => updateItem(index, 'discount', parseFloat(e.target.value) || 0)}
                                InputProps={{
                                  startAdornment: (
                                    <InputAdornment position="start">F</InputAdornment>
                                  ),
                                }}
                                fullWidth
                              />
                            </Grid>
                            <Grid item xs={6} sm={2}>
                              <Typography variant="body2" fontWeight="medium" align="right">
                                {formatCurrency(calculateItemTotal(item))}
                              </Typography>
                            </Grid>
                            <Grid item xs={12} sm={1} sx={{ textAlign: 'center' }}>
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => removeItem(index)}
                              >
                                <Delete />
                              </IconButton>
                            </Grid>
                          </Grid>
                        </Paper>
                      </motion.div>
                    );
                  })}
                </Box>
              )}
            </AnimatePresence>
          </Paper>
        </Grid>

        {/* Right Column - Summary */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, borderRadius: 2, position: 'sticky', top: 20 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Récapitulatif
            </Typography>

            <Divider sx={{ my: 2 }} />

            {/* Payment Method */}
            <TextField
              select
              fullWidth
              label="Méthode de paiement"
              name="payment_method"
              value={formik.values.payment_method}
              onChange={formik.handleChange}
              sx={{ mb: 2 }}
            >
              <MenuItem value="CASH">Espèces</MenuItem>
              <MenuItem value="Saraly">Saraly</MenuItem>
              <MenuItem value="CARD">Carte</MenuItem>
              <MenuItem value="BANK_TRANSFER">Virement</MenuItem>
              <MenuItem value="CHECK">Chèque</MenuItem>
            </TextField>

            {/* Totals */}
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography color="text.secondary">Sous-total</Typography>
                <Typography>{formatCurrency(calculateSubtotal())}</Typography>
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography color="text.secondary">Remise globale</Typography>
                <TextField
                  size="small"
                  type="number"
                  name="discount"
                  value={formik.values.discount}
                  onChange={formik.handleChange}
                  sx={{ width: 100 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">F</InputAdornment>
                    ),
                  }}
                />
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography color="text.secondary">Taxes</Typography>
                <TextField
                  size="small"
                  type="number"
                  name="tax_amount"
                  value={formik.values.tax_amount}
                  onChange={formik.handleChange}
                  sx={{ width: 100 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">F</InputAdornment>
                    ),
                  }}
                />
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography color="text.secondary">Frais de livraison</Typography>
                <TextField
                  size="small"
                  type="number"
                  name="shipping_cost"
                  value={formik.values.shipping_cost}
                  onChange={formik.handleChange}
                  sx={{ width: 100 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">F</InputAdornment>
                    ),
                  }}
                />
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" fontWeight="bold">
                  Total
                </Typography>
                <Typography variant="h6" fontWeight="bold" color="primary.main">
                  {formatCurrency(calculateTotal())}
                </Typography>
              </Box>
            </Box>

            {/* Notes */}
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Notes"
              name="notes"
              value={formik.values.notes}
              onChange={formik.handleChange}
              sx={{ mb: 3 }}
            />

            {/* Actions */}
            <Button
              fullWidth
              variant="contained"
              size="large"
              type="submit"
              disabled={createMutation.isLoading || formik.values.items.length === 0}
              sx={{
                mb: 1,
                py: 1.5,
                bgcolor: 'primary.main',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
              }}
            >
              {createMutation.isLoading ? 'Enregistrement...' : 'Finaliser la vente'}
            </Button>

            <Button
              fullWidth
              variant="outlined"
              onClick={onCancel}
              disabled={createMutation.isLoading}
            >
              Annuler
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SaleForm;