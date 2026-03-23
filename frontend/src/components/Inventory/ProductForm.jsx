import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Chip,
  IconButton,
  Avatar,
  LinearProgress,
  Alert,
  FormHelperText,
} from '@mui/material';
import { AddPhotoAlternate, Delete, AttachMoney, LocalOffer, Inventory, Category } from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { motion } from 'framer-motion';
import { inventoryService } from '../../services/inventory';
import { PRODUCT_CATEGORIES, PRODUCT_BRANDS } from '../../constants/config';
import toast from 'react-hot-toast';

const validationSchema = Yup.object({
  name: Yup.string().required('Nom requis'),
  category: Yup.string().required('Catégorie requise'),
  purchase_price: Yup.number()
    .required('Prix d\'achat requis')
    .min(0, 'Doit être positif'),
  selling_price: Yup.number()
    .required('Prix de vente requis')
    .min(0, 'Doit être positif')
    .moreThan(Yup.ref('purchase_price'), 'Le prix de vente doit être supérieur au prix d\'achat'),
  alert_threshold: Yup.number()
    .required('Seuil d\'alerte requis')
    .min(0, 'Doit être positif'),
  sku: Yup.string().nullable(),
  barcode: Yup.string().nullable(),
});

const ProductForm = ({ open, onClose, onSuccess, product = null }) => {
  const isEdit = !!product;
  const [uploading, setUploading] = useState(false);
  const [images, setImages] = useState(product?.images || []);
  const [suppliers, setSuppliers] = useState([]);
  const [loadingSuppliers, setLoadingSuppliers] = useState(false);

  useEffect(() => {
    if (open) {
      loadSuppliers();
    }
  }, [open]);

  const loadSuppliers = async () => {
    setLoadingSuppliers(true);
    try {
      const data = await inventoryService.getSuppliers({ active_only: true, limit: 100 });
      setSuppliers(data);
    } catch (error) {
      console.error('Erreur chargement fournisseurs', error);
    } finally {
      setLoadingSuppliers(false);
    }
  };

  const formik = useFormik({
    initialValues: {
      name: product?.name || '',
      category: product?.category || '',
      brand: product?.brand || '',
      description: product?.description || '',
      purchase_price: product?.purchase_price || '',
      selling_price: product?.selling_price || '',
      alert_threshold: product?.alert_threshold || 10,
      sku: product?.sku || '',
      barcode: product?.barcode || '',
      supplier_id: product?.supplier_id || '',
      initial_stock: 0,
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        if (isEdit) {
          await inventoryService.updateProduct(product.id, values);
        } else {
          await inventoryService.createProduct(values, values.supplier_id || null);
        }
        onSuccess();
        onClose();
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Erreur lors de l\'enregistrement');
      }
    },
  });

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // En mode création, on ne peut pas uploader tant que le produit n'a pas d'ID
    if (!isEdit) {
      toast.error('Veuillez d\'abord créer le produit avant d\'ajouter des images');
      return;
    }

    setUploading(true);
    try {
      const res = await inventoryService.uploadProductImage(product.id, file);
      setImages([...images, res.filename]);
      toast.success('Image ajoutée');
    } catch (error) {
      toast.error('Erreur upload');
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveImage = (index) => {
    setImages(images.filter((_, i) => i !== index));
    // TODO: appeler API pour supprimer l'image si besoin
  };

  const margin = formik.values.purchase_price && formik.values.selling_price
    ? ((formik.values.selling_price - formik.values.purchase_price) / formik.values.purchase_price * 100).toFixed(1)
    : 0;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
      <DialogTitle sx={{ fontWeight: 600 }}>
        {isEdit ? 'Modifier le produit' : 'Ajouter un nouveau produit'}
      </DialogTitle>
      <form onSubmit={formik.handleSubmit}>
        <DialogContent dividers>
          <Grid container spacing={3}>
            {/* Colonne gauche - Infos */}
            <Grid item xs={12} md={8}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Nom du produit"
                    name="name"
                    value={formik.values.name}
                    onChange={formik.handleChange}
                    error={formik.touched.name && Boolean(formik.errors.name)}
                    helperText={formik.touched.name && formik.errors.name}
                    InputProps={{ startAdornment: <Inventory sx={{ mr: 1, color: 'text.secondary' }} /> }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth error={formik.touched.category && Boolean(formik.errors.category)}>
                    <InputLabel>Catégorie</InputLabel>
                    <Select
                      name="category"
                      value={formik.values.category}
                      onChange={formik.handleChange}
                      label="Catégorie"
                    >
                      {PRODUCT_CATEGORIES.map(cat => (
                        <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                      ))}
                    </Select>
                    {formik.touched.category && formik.errors.category && (
                      <FormHelperText>{formik.errors.category}</FormHelperText>
                    )}
                  </FormControl>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Marque</InputLabel>
                    <Select
                      name="brand"
                      value={formik.values.brand}
                      onChange={formik.handleChange}
                      label="Marque"
                    >
                      <MenuItem value="">Aucune</MenuItem>
                      {PRODUCT_BRANDS.map(brand => (
                        <MenuItem key={brand} value={brand}>{brand}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Prix d'achat (FCFA)"
                    name="purchase_price"
                    type="number"
                    value={formik.values.purchase_price}
                    onChange={formik.handleChange}
                    error={formik.touched.purchase_price && Boolean(formik.errors.purchase_price)}
                    helperText={formik.touched.purchase_price && formik.errors.purchase_price}
                    InputProps={{ startAdornment: <AttachMoney sx={{ mr: 1, color: 'text.secondary' }} /> }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Prix de vente (FCFA)"
                    name="selling_price"
                    type="number"
                    value={formik.values.selling_price}
                    onChange={formik.handleChange}
                    error={formik.touched.selling_price && Boolean(formik.errors.selling_price)}
                    helperText={formik.touched.selling_price && formik.errors.selling_price}
                    InputProps={{ startAdornment: <LocalOffer sx={{ mr: 1, color: 'text.secondary' }} /> }}
                  />
                </Grid>

                {margin > 0 && (
                  <Grid item xs={12}>
                    <Alert severity={margin >= 30 ? 'success' : margin >= 20 ? 'info' : 'warning'} sx={{ borderRadius: 2 }}>
                      Marge bénéficiaire: <strong>{margin}%</strong>
                    </Alert>
                  </Grid>
                )}

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Seuil d'alerte"
                    name="alert_threshold"
                    type="number"
                    value={formik.values.alert_threshold}
                    onChange={formik.handleChange}
                    error={formik.touched.alert_threshold && Boolean(formik.errors.alert_threshold)}
                    helperText={formik.touched.alert_threshold && formik.errors.alert_threshold}
                  />
                </Grid>

                {!isEdit && (
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Stock initial"
                      name="initial_stock"
                      type="number"
                      value={formik.values.initial_stock}
                      onChange={formik.handleChange}
                      helperText="Quantité en stock à la création"
                    />
                  </Grid>
                )}

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="SKU"
                    name="sku"
                    value={formik.values.sku}
                    onChange={formik.handleChange}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Code-barres"
                    name="barcode"
                    value={formik.values.barcode}
                    onChange={formik.handleChange}
                  />
                </Grid>

                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Fournisseur principal</InputLabel>
                    <Select
                      name="supplier_id"
                      value={formik.values.supplier_id}
                      onChange={formik.handleChange}
                      label="Fournisseur principal"
                    >
                      <MenuItem value="">Aucun</MenuItem>
                      {suppliers.map(s => (
                        <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    name="description"
                    multiline
                    rows={3}
                    value={formik.values.description}
                    onChange={formik.handleChange}
                  />
                </Grid>
              </Grid>
            </Grid>

            {/* Colonne droite - Images */}
            <Grid item xs={12} md={4}>
              <Box sx={{ border: '2px dashed', borderColor: 'divider', borderRadius: 3, p: 3, textAlign: 'center', height: '100%' }}>
                <Typography variant="subtitle2" gutterBottom>Images</Typography>

                {uploading && <LinearProgress sx={{ mb: 2 }} />}

                <Button
                  component="label"
                  variant="outlined"
                  startIcon={<AddPhotoAlternate />}
                  disabled={uploading || (!isEdit && images.length === 0)}
                  sx={{ mb: 2 }}
                >
                  Ajouter une image
                  <input type="file" hidden accept="image/*" onChange={handleImageUpload} />
                </Button>

                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
                  {images.map((img, index) => (
                    <Box key={index} sx={{ position: 'relative', width: '80px', height: '80px' }}>
                      <Avatar
                        src={`http://localhost:8000/uploads/products/${img}`}
                        variant="rounded"
                        sx={{ width: '100%', height: '100%' }}
                      />
                      <IconButton
                        size="small"
                        sx={{ position: 'absolute', top: -8, right: -8, bgcolor: 'background.paper' }}
                        onClick={() => handleRemoveImage(index)}
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                    </Box>
                  ))}
                </Box>

                {!isEdit && (
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
                    Les images pourront être ajoutées après la création.
                  </Typography>
                )}
              </Box>
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ p: 3 }}>
          <Button onClick={onClose}>Annuler</Button>
          <Button type="submit" variant="contained" disabled={formik.isSubmitting}>
            {formik.isSubmitting ? 'Enregistrement...' : isEdit ? 'Mettre à jour' : 'Créer'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default ProductForm;