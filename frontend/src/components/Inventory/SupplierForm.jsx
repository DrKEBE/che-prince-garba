import React, { useState } from 'react';
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
  Stack,
  FormHelperText,
} from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { inventoryService } from '../../services/inventory';
import { CITIES_CI } from '../../constants/config';
import toast from 'react-hot-toast';

const validationSchema = Yup.object({
  name: Yup.string().required('Nom requis'),
  contact_person: Yup.string(),
  phone: Yup.string(),
  email: Yup.string().email('Email invalide'),
  address: Yup.string(),
  city: Yup.string(),
  country: Yup.string(),
  payment_terms: Yup.string(),
  credit_limit: Yup.number().nullable().min(0, 'Doit être positif'),
  notes: Yup.string(),
});

const SupplierForm = ({ open, onClose, onSuccess, supplier = null }) => {
  const isEdit = !!supplier;

  const formik = useFormik({
    initialValues: {
      name: supplier?.name || '',
      contact_person: supplier?.contact_person || '',
      phone: supplier?.phone || '',
      email: supplier?.email || '',
      address: supplier?.address || 'ATT Bougou 320',
      city: supplier?.city || '',
      country: supplier?.country || 'Côte d\'Ivoire',
      payment_terms: supplier?.payment_terms || '',
      credit_limit: supplier?.credit_limit || '',
      notes: supplier?.notes || '',
      is_active: supplier?.is_active ?? true,
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        if (isEdit) {
          await inventoryService.updateSupplier(supplier.id, values);
        } else {
          await inventoryService.createSupplier(values);
        }
        toast.success(isEdit ? 'Fournisseur mis à jour' : 'Fournisseur créé');
        onSuccess();
        onClose();
      } catch (error) {
        toast.error(error.response?.data?.detail || 'Erreur');
      }
    },
  });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
      <DialogTitle sx={{ fontWeight: 600 }}>
        {isEdit ? 'Modifier le fournisseur' : 'Nouveau fournisseur'}
      </DialogTitle>
      <form onSubmit={formik.handleSubmit}>
        <DialogContent dividers>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nom de l'entreprise"
                name="name"
                value={formik.values.name}
                onChange={formik.handleChange}
                error={formik.touched.name && Boolean(formik.errors.name)}
                helperText={formik.touched.name && formik.errors.name}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Personne de contact"
                name="contact_person"
                value={formik.values.contact_person}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Téléphone"
                name="phone"
                value={formik.values.phone}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formik.values.email}
                onChange={formik.handleChange}
                error={formik.touched.email && Boolean(formik.errors.email)}
                helperText={formik.touched.email && formik.errors.email}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Ville</InputLabel>
                <Select
                  name="city"
                  value={formik.values.city}
                  onChange={formik.handleChange}
                  label="Ville"
                >
                  <MenuItem value="">Non spécifiée</MenuItem>
                  {CITIES_CI.map(city => (
                    <MenuItem key={city} value={city}>{city}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Adresse"
                name="address"
                multiline
                rows={2}
                value={formik.values.address}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Conditions de paiement"
                name="payment_terms"
                placeholder="Ex: 30 jours"
                value={formik.values.payment_terms}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Limite de crédit (FCFA)"
                name="credit_limit"
                type="number"
                value={formik.values.credit_limit}
                onChange={formik.handleChange}
                InputProps={{ inputProps: { min: 0 } }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                name="notes"
                multiline
                rows={3}
                value={formik.values.notes}
                onChange={formik.handleChange}
              />
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

export default SupplierForm;