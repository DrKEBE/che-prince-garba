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
  Stack,
  Alert,
} from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { inventoryService } from '../../services/inventory';
import { STOCK_MOVEMENT_TYPES } from '../../constants/config';
import toast from 'react-hot-toast';

const validationSchema = Yup.object({
  product_id: Yup.string().required('Produit requis'),
  movement_type: Yup.string().required('Type requis'),
  quantity: Yup.number().required('Quantité requise').positive('Doit être positif'),
  unit_cost: Yup.number().nullable().min(0, 'Doit être positif'),
  reason: Yup.string(),
  reference: Yup.string(),
  supplier_id: Yup.string().nullable(),
  notes: Yup.string(),
});

const StockMovementForm = ({ open, onClose, onSuccess }) => {
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);

  useEffect(() => {
    if (open) {
      loadProducts();
      loadSuppliers();
    }
  }, [open]);

  const loadProducts = async () => {
    try {
      const data = await inventoryService.getProducts({ include_inactive: false, limit: 500 });
      setProducts(data);
    } catch (error) {
      console.error(error);
    }
  };

  const loadSuppliers = async () => {
    try {
      const data = await inventoryService.getSuppliers({ active_only: true, limit: 100 });
      setSuppliers(data);
    } catch (error) {
      console.error(error);
    }
  };

  const formik = useFormik({
    initialValues: {
      product_id: '',
      movement_type: 'IN',
      quantity: 1,
      unit_cost: '',
      reason: '',
      reference: '',
      supplier_id: '',
      notes: '',
      movement_date: new Date().toISOString().slice(0, 16), // format datetime-local
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        const payload = {
          ...values,
          quantity: parseInt(values.quantity, 10),
          unit_cost: values.unit_cost ? parseFloat(values.unit_cost) : undefined,
        };
        await inventoryService.createStockMovement(payload);
        toast.success('Mouvement enregistré');
        onSuccess();
        onClose();
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Erreur lors de l\'enregistrement');
      }
    },
  });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
      <DialogTitle sx={{ fontWeight: 600 }}>Nouveau mouvement de stock</DialogTitle>
      <form onSubmit={formik.handleSubmit}>
        <DialogContent dividers>
          <Stack spacing={3}>
            <FormControl fullWidth error={formik.touched.product_id && Boolean(formik.errors.product_id)}>
              <InputLabel>Produit</InputLabel>
              <Select
                name="product_id"
                value={formik.values.product_id}
                onChange={formik.handleChange}
                label="Produit"
              >
                {products.map(p => (
                  <MenuItem key={p.id} value={p.id}>{p.name} (Stock: {p.current_stock || 0})</MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Type de mouvement</InputLabel>
              <Select
                name="movement_type"
                value={formik.values.movement_type}
                onChange={formik.handleChange}
                label="Type de mouvement"
              >
                {Object.entries(STOCK_MOVEMENT_TYPES).map(([key, label]) => (
                  <MenuItem key={key} value={key}>{label}</MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Quantité"
              name="quantity"
              type="number"
              value={formik.values.quantity}
              onChange={formik.handleChange}
              error={formik.touched.quantity && Boolean(formik.errors.quantity)}
              helperText={formik.touched.quantity && formik.errors.quantity}
              InputProps={{ inputProps: { min: 1 } }}
            />

            <TextField
              fullWidth
              label="Coût unitaire (FCFA)"
              name="unit_cost"
              type="number"
              value={formik.values.unit_cost}
              onChange={formik.handleChange}
              error={formik.touched.unit_cost && Boolean(formik.errors.unit_cost)}
              helperText="Laissez vide pour utiliser le prix d'achat du produit"
            />

            <TextField
              fullWidth
              label="Raison"
              name="reason"
              value={formik.values.reason}
              onChange={formik.handleChange}
              placeholder="Ex: Réapprovisionnement, vente, inventaire..."
            />

            <TextField
              fullWidth
              label="Référence"
              name="reference"
              value={formik.values.reference}
              onChange={formik.handleChange}
              placeholder="Numéro de commande, facture..."
            />

            <FormControl fullWidth>
              <InputLabel>Fournisseur (si entrée)</InputLabel>
              <Select
                name="supplier_id"
                value={formik.values.supplier_id}
                onChange={formik.handleChange}
                label="Fournisseur (si entrée)"
              >
                <MenuItem value="">Aucun</MenuItem>
                {suppliers.map(s => (
                  <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Date du mouvement"
              name="movement_date"
              type="datetime-local"
              value={formik.values.movement_date}
              onChange={formik.handleChange}
              InputLabelProps={{ shrink: true }}
            />

            <TextField
              fullWidth
              label="Notes"
              name="notes"
              multiline
              rows={3}
              value={formik.values.notes}
              onChange={formik.handleChange}
            />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={onClose}>Annuler</Button>
          <Button type="submit" variant="contained" disabled={formik.isSubmitting}>
            {formik.isSubmitting ? 'Enregistrement...' : 'Enregistrer'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default StockMovementForm;