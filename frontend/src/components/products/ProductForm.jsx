// src/components/products/ProductForm.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  TextField,
  Button,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Chip,
  IconButton,
  Avatar,
  Autocomplete,
  LinearProgress,
  Alert,
  FormHelperText,
} from '@mui/material';
import Typography from '@mui/material/Typography';
import {
  AddPhotoAlternate,
  Delete,
  LocalOffer,
  Category,
  Inventory,
  AttachMoney,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { productService } from '../../services/products';
import toast from 'react-hot-toast';

const categories = [
    "Soins Visage",
    "Soins Corps",
    "Soins Capillaires",
    "Lait",
    "Crème",
    "Pommade",
    "Maquillage",
    "Déodorants",
    "Parfums",
    "Huiles",
    "Sérums",
    "Gommage",
    "Shampoing",
    "Mèches",
    "Accessoires",
];


const validationSchema = Yup.object({
  name: Yup.string().required('Le nom est requis'),
  category: Yup.string().required('La catégorie est requise'),
  brand: Yup.string(),
  purchase_price: Yup.number()
    .required('Le prix d\'achat est requis')
    .min(0, 'Le prix doit être positif'),
  selling_price: Yup.number()
    .required('Le prix de vente est requis')
    .min(0, 'Le prix doit être positif')
    .test(
      'greater-than-purchase',
      'Le prix de vente doit être supérieur au prix d\'achat',
      function (value) {
        const { purchase_price } = this.parent;
        return value > purchase_price;
      }
    ),
  alert_threshold: Yup.number()
    .required('Le seuil d\'alerte est requis')
    .min(0, 'Le seuil doit être positif'),
  sku: Yup.string(),
  barcode: Yup.string(),
  description: Yup.string(),
});

export default function ProductForm({ product, onSuccess, onCancel }) {
  const [uploading, setUploading] = useState(false);
  const [uploadedImages, setUploadedImages] = useState([]);
  const queryClient = useQueryClient();

  const { data: brands = [] } = useQuery(
    'product-brands',
    productService.getBrands,
    {
      staleTime: 1000 * 60 * 5,
    }
  );

  const isEdit = !!product;

  const createMutation = useMutation(
    (data) => productService.createProduct(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('products');
        toast.success('Produit créé avec succès');
        onSuccess();
      },
      onError: (error) => {
        toast.error('Erreur lors de la création');
      },
    }
  );

  const updateMutation = useMutation(
    (data) => productService.updateProduct(product.id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('products');
        toast.success('Produit mis à jour avec succès');
        onSuccess();
      },
      onError: (error) => {
        toast.error('Erreur lors de la mise à jour');
      },
    }
  );

  const formik = useFormik({
    initialValues: {
      name: product?.name || '',
      category: product?.category || '',
      brand: product?.brand || '',
      purchase_price: product?.purchase_price || '',
      selling_price: product?.selling_price || '',
      alert_threshold: product?.alert_threshold || 10,
      sku: product?.sku || '',
      barcode: product?.barcode || '',
      description: product?.description || '',
      initial_stock: product?.current_stock || 0,
    },
    validationSchema,
    onSubmit: (values) => {
      if (isEdit) {
        updateMutation.mutate(values);
      } else {
        createMutation.mutate(values);
      }
    },
  });

  useEffect(() => {
    if (product?.images) {
      setUploadedImages(product.images);
    }
  }, [product]);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const productId = product?.id || 'new';
      const response = await productService.uploadProductImage(productId, formData);
      
      setUploadedImages([...uploadedImages, response.image]);
      toast.success('Image téléchargée avec succès');
    } catch (error) {
      toast.error('Erreur lors du téléchargement de l\'image');
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveImage = (index) => {
    setUploadedImages(uploadedImages.filter((_, i) => i !== index));
  };

  const calculateMargin = () => {
    const purchase = parseFloat(formik.values.purchase_price) || 0;
    const selling = parseFloat(formik.values.selling_price) || 0;
    
    if (purchase <= 0 || selling <= 0) return 0;
    
    const margin = ((selling - purchase) / purchase) * 100;
    return margin.toFixed(1);
  };

  const margin = calculateMargin();

  return (
    <Box component="form" onSubmit={formik.handleSubmit}>
      <Grid container spacing={3}>
        {/* Left Column - Basic Info */}
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
                InputProps={{
                  startAdornment: (
                    <Inventory sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Catégorie</InputLabel>
                <Select
                  name="category"
                  value={formik.values.category}
                  onChange={formik.handleChange}
                  label="Catégorie"
                  startAdornment={
                    <Category sx={{ mr: 1, color: 'text.secondary' }} />
                  }
                >
                  {categories.map((category) => (
                    <MenuItem key={category} value={category}>
                      {category}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Autocomplete
                freeSolo
                options={brands}
                value={formik.values.brand || ''}
                onChange={(event, newValue) => {
                  formik.setFieldValue('brand', newValue || '');
                }}
                onInputChange={(event, newInputValue) => {
                  formik.setFieldValue('brand', newInputValue);
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Marque"
                    fullWidth
                    helperText="Choisissez ou tapez une nouvelle marque"
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Prix d'achat (FCFA)"
                name="purchase_price"
                type="number"
                value={formik.values.purchase_price}
                onChange={formik.handleChange}
                error={
                  formik.touched.purchase_price &&
                  Boolean(formik.errors.purchase_price)
                }
                helperText={
                  formik.touched.purchase_price && formik.errors.purchase_price
                }
                InputProps={{
                  startAdornment: (
                    <AttachMoney sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                }}
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
                error={
                  formik.touched.selling_price &&
                  Boolean(formik.errors.selling_price)
                }
                helperText={
                  formik.touched.selling_price && formik.errors.selling_price
                }
                InputProps={{
                  startAdornment: (
                    <LocalOffer sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                }}
              />
            </Grid>

            {margin > 0 && (
              <Grid item xs={12}>
                <Alert
                  severity={margin >= 30 ? 'success' : margin >= 20 ? 'info' : 'warning'}
                  sx={{ borderRadius: 2 }}
                >
                  Marge bénéficiaire: <strong>{margin}%</strong>
                  {margin >= 30
                    ? ' - Excellente marge!'
                    : margin >= 20
                    ? ' - Bonne marge'
                    : ' - Marge faible, à revoir'}
                </Alert>
              </Grid>
            )}

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Seuil d'alerte stock"
                name="alert_threshold"
                type="number"
                value={formik.values.alert_threshold}
                onChange={formik.handleChange}
                error={
                  formik.touched.alert_threshold &&
                  Boolean(formik.errors.alert_threshold)
                }
                helperText={
                  formik.touched.alert_threshold && formik.errors.alert_threshold
                }
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
                helperText="Code produit unique"
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
              <TextField
                fullWidth
                label="Description"
                name="description"
                multiline
                rows={4}
                value={formik.values.description}
                onChange={formik.handleChange}
                helperText="Description détaillée du produit"
              />
            </Grid>
          </Grid>
        </Grid>

        {/* Right Column - Images */}
        <Grid item xs={12} md={4}>
          <Box
            sx={{
              border: '2px dashed',
              borderColor: 'divider',
              borderRadius: 3,
              p: 3,
              textAlign: 'center',
              height: '100%',
            }}
          >
            <Typography variant="h6" gutterBottom>
              Images du produit
            </Typography>

            {uploading && <LinearProgress sx={{ mb: 2 }} />}

            {/* Upload Button */}
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button
                component="label"
                variant="outlined"
                startIcon={<AddPhotoAlternate />}
                sx={{ mb: 3 }}
                disabled={uploading}
              >
                Ajouter une image
                <input
                  type="file"
                  hidden
                  accept="image/*"
                  onChange={handleImageUpload}
                />
              </Button>
            </motion.div>

            {/* Image Previews */}
            <Grid container spacing={1}>
              {uploadedImages.map((image, index) => (
                <Grid item xs={6} key={index}>
                  <Box
                    sx={{
                      position: 'relative',
                      borderRadius: 2,
                      overflow: 'hidden',
                    }}
                  >
                    <Avatar
                      src={`http://localhost:8000/uploads/products/${image}`}
                      variant="rounded"
                      sx={{ width: '100%', height: 100 }}
                    />
                    <IconButton
                      size="small"
                      sx={{
                        position: 'absolute',
                        top: 4,
                        right: 4,
                        bgcolor: 'rgba(0,0,0,0.5)',
                        color: 'white',
                        '&:hover': {
                          bgcolor: 'rgba(0,0,0,0.7)',
                        },
                      }}
                      onClick={() => handleRemoveImage(index)}
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                  </Box>
                </Grid>
              ))}
            </Grid>

            {uploadedImages.length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Aucune image ajoutée. Ajoutez des images pour mieux présenter votre produit.
              </Typography>
            )}
          </Box>
        </Grid>
      </Grid>

      {/* Form Actions */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'flex-end',
          gap: 2,
          mt: 4,
          pt: 2,
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <Button onClick={onCancel} disabled={createMutation.isLoading}>
          Annuler
        </Button>
        <Button
          type="submit"
          variant="contained"
          disabled={createMutation.isLoading || updateMutation.isLoading}
          sx={{
            bgcolor: 'primary.main',
            minWidth: 120,
          }}
        >
          {createMutation.isLoading || updateMutation.isLoading
            ? 'Enregistrement...'
            : isEdit
            ? 'Mettre à jour'
            : 'Créer'}
        </Button>
      </Box>
    </Box>
  );
}