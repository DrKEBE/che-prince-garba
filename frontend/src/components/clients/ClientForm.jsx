import React from 'react';
import {
  Box,
  Grid,
  TextField,
  Button,
  MenuItem,
  Typography,
  Divider,
  Chip,
  Avatar,
  InputAdornment,
} from '@mui/material';
import {
  Person,
  Phone,
  Email,
  Home,
  Cake,
  Female,
  Male,
  Loyalty,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useMutation, useQueryClient } from 'react-query';
import { clientService } from '../../services/clients';
import toast from 'react-hot-toast';

const validationSchema = Yup.object({
  full_name: Yup.string().required('Le nom complet est requis'),
  phone: Yup.string()
    .required('Le téléphone est requis')
    .matches(/^[0-9+\-\s()]{8,20}$/, 'Numéro de téléphone invalide'),
  email: Yup.string().email('Email invalide'),
  address: Yup.string(),
  city: Yup.string(),
  postal_code: Yup.string(),
  country: Yup.string(),
  client_type: Yup.string(),
  birth_date: Yup.date(),
  gender: Yup.string(),
  notes: Yup.string(),
});

const ClientForm = ({ client, viewMode = false, onSuccess, onCancel }) => {
  const isEdit = !!client;
  const queryClient = useQueryClient();

  const createMutation = useMutation(
    (data) => clientService.createClient(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('clients');
        toast.success('Client créé avec succès');
        onSuccess();
      },
      onError: (error) => {
        toast.error('Erreur lors de la création');
      },
    }
  );

  const updateMutation = useMutation(
    (data) => clientService.updateClient(client.id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('clients');
        toast.success('Client mis à jour avec succès');
        onSuccess();
      },
      onError: (error) => {
        toast.error('Erreur lors de la mise à jour');
      },
    }
  );

  const formik = useFormik({
    initialValues: {
      full_name: client?.full_name || '',
      phone: client?.phone || '',
      email: client?.email || '',
      address: client?.address || 'ATT Bougou 320',
      city: client?.city || '',
      postal_code: client?.postal_code || '',
      country: client?.country || "Côte d'Ivoire",
      client_type: client?.client_type || 'REGULAR',
      birth_date: client?.birth_date ? new Date(client.birth_date).toISOString().split('T')[0] : '',
      gender: client?.gender || '',
      notes: client?.notes || '',
      preferences: client?.preferences || {},
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

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-CI', {
      style: 'currency',
      currency: 'XOF',
      minimumFractionDigits: 0,
    }).format(value);
  };

  return (
    <Box component="form" onSubmit={formik.handleSubmit}>
      <Grid container spacing={3}>
        {/* Left Column - Basic Info */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nom complet"
                name="full_name"
                value={formik.values.full_name}
                onChange={formik.handleChange}
                error={formik.touched.full_name && Boolean(formik.errors.full_name)}
                helperText={formik.touched.full_name && formik.errors.full_name}
                disabled={viewMode}
                InputProps={{
                  startAdornment: (
                    <Person sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Téléphone"
                name="phone"
                value={formik.values.phone}
                onChange={formik.handleChange}
                error={formik.touched.phone && Boolean(formik.errors.phone)}
                helperText={formik.touched.phone && formik.errors.phone}
                disabled={viewMode}
                InputProps={{
                  startAdornment: (
                    <Phone sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                }}
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
                disabled={viewMode}
                InputProps={{
                  startAdornment: (
                    <Email sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Adresse"
                name="address"
                value={formik.values.address}
                onChange={formik.handleChange}
                disabled={viewMode}
                InputProps={{
                  startAdornment: (
                    <Home sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Ville"
                name="city"
                value={formik.values.city}
                onChange={formik.handleChange}
                disabled={viewMode}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Code postal"
                name="postal_code"
                value={formik.values.postal_code}
                onChange={formik.handleChange}
                disabled={viewMode}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Type de client"
                name="client_type"
                value={formik.values.client_type}
                onChange={formik.handleChange}
                disabled={viewMode}
              >
                <MenuItem value="REGULAR">Standard</MenuItem>
                <MenuItem value="VIP">VIP</MenuItem>
                <MenuItem value="FIDELITE">Fidélité</MenuItem>
                <MenuItem value="WHOLESALER">Revendeur</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Date de naissance"
                name="birth_date"
                type="date"
                value={formik.values.birth_date}
                onChange={formik.handleChange}
                disabled={viewMode}
                InputLabelProps={{ shrink: true }}
                InputProps={{
                  startAdornment: (
                    <Cake sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Genre"
                name="gender"
                value={formik.values.gender}
                onChange={formik.handleChange}
                disabled={viewMode}
              >
                <MenuItem value="">Non spécifié</MenuItem>
                <MenuItem value="MALE">Homme</MenuItem>
                <MenuItem value="FEMALE">Femme</MenuItem>
              </TextField>
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
                disabled={viewMode}
                helperText="Informations supplémentaires sur le client"
              />
            </Grid>
          </Grid>
        </Grid>

        {/* Right Column - Stats & Actions */}
        <Grid item xs={12} md={4}>
          {/* Client Stats (for existing clients) */}
          {isEdit && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Box
                sx={{
                  p: 3,
                  borderRadius: 2,
                  backgroundColor: 'background.paper',
                  border: '1px solid',
                  borderColor: 'divider',
                  mb: 3,
                }}
              >
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Statistiques du client
                </Typography>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar
                    sx={{
                      width: 64,
                      height: 64,
                      mr: 2,
                      bgcolor: 'primary.light',
                      fontSize: 24,
                    }}
                  >
                    {formik.values.full_name?.[0] || 'C'}
                  </Avatar>
                  <Box>
                    <Typography variant="body2" fontWeight="medium">
                      {formik.values.full_name}
                    </Typography>
                    <Chip
                      label={formik.values.client_type}
                      size="small"
                      color="primary"
                      sx={{ mt: 0.5 }}
                    />
                  </Box>
                </Box>

                <Divider sx={{ my: 2 }} />

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Total achats
                    </Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatCurrency(client.total_purchases || 0)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Transactions
                    </Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {client.total_transactions || 0}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Points fidélité
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Loyalty sx={{ mr: 0.5, color: 'warning.main', fontSize: 16 }} />
                      <Typography variant="body2" fontWeight="bold">
                        {client.loyalty_points || 0}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Dernier achat
                    </Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {client.last_purchase
                        ? new Date(client.last_purchase).toLocaleDateString('fr-FR')
                        : 'Jamais'}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </motion.div>
          )}

          {/* Form Actions */}
          {!viewMode && (
            <Box
              sx={{
                p: 3,
                borderRadius: 2,
                backgroundColor: 'background.paper',
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Enregistrer
              </Typography>

              <Button
                fullWidth
                variant="contained"
                size="large"
                type="submit"
                disabled={createMutation.isLoading || updateMutation.isLoading}
                sx={{
                  mb: 2,
                  py: 1.5,
                  bgcolor: 'primary.main',
                  '&:hover': {
                    bgcolor: 'primary.dark',
                  },
                }}
              >
                {createMutation.isLoading || updateMutation.isLoading
                  ? 'Enregistrement...'
                  : isEdit
                  ? 'Mettre à jour'
                  : 'Créer le client'}
              </Button>

              <Button
                fullWidth
                variant="outlined"
                onClick={onCancel}
                disabled={createMutation.isLoading || updateMutation.isLoading}
              >
                Annuler
              </Button>
            </Box>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default ClientForm;