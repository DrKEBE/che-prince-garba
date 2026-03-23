// src/pages/Clients.jsx
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Avatar,
  Badge,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Person,
  Phone,
  Email,
  Loyalty,
  TrendingUp,
  FilterList,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import DataTable from '../components/common/DataTable';
import ClientForm from '../components/clients/ClientForm';
import { clientService } from '../services/clients';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Clients() {
  const [openForm, setOpenForm] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);
  const [viewMode, setViewMode] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [clientToDelete, setClientToDelete] = useState(null);

  const { isAdmin, isManager } = useAuth();
  const queryClient = useQueryClient();

  const { data: clients, isLoading } = useQuery(
    'clients',
    () => clientService.getClients(),
    { refetchOnWindowFocus: false }
  );

  const { data: topClients } = useQuery(
    'top-clients',
    () => clientService.getTopClients(5),
    { refetchOnWindowFocus: false }
  );

  const deleteMutation = useMutation(
    (id) => clientService.deleteClient(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('clients');
        toast.success('Client supprimé avec succès');
        setDeleteDialog(false);
      },
      onError: (error) => {
        toast.error('Erreur lors de la suppression');
      },
    }
  );

  const handleOpenForm = (client = null, view = false) => {
    setSelectedClient(client);
    setViewMode(view);
    setOpenForm(true);
  };

  const handleCloseForm = () => {
    setOpenForm(false);
    setSelectedClient(null);
    setViewMode(false);
  };

  const handleDeleteClick = (client) => {
    setClientToDelete(client);
    setDeleteDialog(true);
  };

  const handleConfirmDelete = () => {
    if (clientToDelete) {
      deleteMutation.mutate(clientToDelete.id);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-CI', {
      style: 'currency',
      currency: 'XOF',
      minimumFractionDigits: 0,
    }).format(value);
  };

  const getClientTypeColor = (type) => {
    switch (type) {
      case 'VIP':
        return 'primary';
      case 'FIDELITE':
        return 'success';
      case 'WHOLESALER':
        return 'warning';
      default:
        return 'default';
    }
  };

  const columns = [
    {
      field: 'client',
      headerName: 'Client',
      flex: 2,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar
            sx={{
              width: 40,
              height: 40,
              mr: 2,
              bgcolor: 'primary.light',
            }}
          >
            {params.row.full_name?.[0] || 'C'}
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {params.row.full_name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {params.row.phone}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'email',
      headerName: 'Email',
      flex: 2,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.row.email || 'Non spécifié'}
        </Typography>
      ),
    },
    {
      field: 'type',
      headerName: 'Type',
      flex: 1,
      renderCell: (params) => (
        <Chip
          label={params.row.client_type}
          size="small"
          color={getClientTypeColor(params.row.client_type)}
        />
      ),
    },
    {
      field: 'purchases',
      headerName: 'Achats',
      flex: 1,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2" fontWeight="medium">
            {formatCurrency(params.row.total_purchases || 0)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {params.row.total_transactions || 0} transactions
          </Typography>
        </Box>
      ),
    },
    {
      field: 'loyalty',
      headerName: 'Fidélité',
      flex: 1,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Loyalty sx={{ mr: 0.5, color: 'warning.main', fontSize: 16 }} />
          <Typography variant="body2">
            {params.row.loyalty_points || 0} pts
          </Typography>
        </Box>
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      flex: 1,
      renderCell: (params) => (
        <Box>
          <Tooltip title="Voir">
            <IconButton
              size="small"
              onClick={() => handleOpenForm(params.row, true)}
            >
              <Visibility fontSize="small" />
            </IconButton>
          </Tooltip>
          {(isAdmin || isManager) && (
            <>
              <Tooltip title="Modifier">
                <IconButton
                  size="small"
                  onClick={() => handleOpenForm(params.row)}
                >
                  <Edit fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Supprimer">
                <IconButton
                  size="small"
                  onClick={() => handleDeleteClick(params.row)}
                  color="error"
                >
                  <Delete fontSize="small" />
                </IconButton>
              </Tooltip>
            </>
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
            Gestion des clients
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {clients?.length || 0} clients enregistrés
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenForm()}
          sx={{
            bgcolor: 'primary.main',
            '&:hover': {
              bgcolor: 'primary.dark',
            },
          }}
        >
          Nouveau client
        </Button>
      </Box>

      {/* Top Clients */}
      {topClients && topClients.clients.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom fontWeight="medium">
              🏆 Meilleurs clients
            </Typography>
            <Grid container spacing={2}>
              {topClients.clients.map((client, index) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={client.id}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card
                      variant="outlined"
                      sx={{
                        height: '100%',
                        '&:hover': {
                          borderColor: 'primary.main',
                        },
                      }}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Badge
                            badgeContent={index + 1}
                            color="primary"
                            sx={{ mr: 2 }}
                          >
                            <Avatar
                              sx={{
                                width: 48,
                                height: 48,
                                bgcolor: 'primary.light',
                              }}
                            >
                              {client.full_name?.[0]}
                            </Avatar>
                          </Badge>
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              {client.full_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {client.phone}
                            </Typography>
                          </Box>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Total dépensé
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {formatCurrency(client.total_spent)}
                            </Typography>
                          </Box>
                          <TrendingUp sx={{ color: 'success.main' }} />
                        </Box>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Clients Table */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <DataTable
            rows={clients || []}
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

      {/* Client Form Dialog */}
      <Dialog
        open={openForm}
        onClose={handleCloseForm}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle>
          {viewMode
            ? 'Détails du client'
            : selectedClient
            ? 'Modifier le client'
            : 'Nouveau client'}
        </DialogTitle>
        <DialogContent dividers>
          <ClientForm
            client={selectedClient}
            viewMode={viewMode}
            onSuccess={handleCloseForm}
            onCancel={handleCloseForm}
          />
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog}
        onClose={() => setDeleteDialog(false)}
        PaperProps={{
          sx: {
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle>Confirmer la suppression</DialogTitle>
        <DialogContent>
          <Typography>
            Êtes-vous sûr de vouloir supprimer le client "
            {clientToDelete?.full_name}" ?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Toutes les données associées seront également supprimées.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>Annuler</Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={deleteMutation.isLoading}
          >
            {deleteMutation.isLoading ? 'Suppression...' : 'Supprimer'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}