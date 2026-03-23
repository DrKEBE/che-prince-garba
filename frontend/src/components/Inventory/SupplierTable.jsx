import React, { useState } from 'react';
import {
  Box,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Button,
  Stack,
} from '@mui/material';
import {
  Edit,
  Delete,
  Visibility,
  LocalShipping,
  Inventory,
} from '@mui/icons-material';
import { DataGrid } from '@mui/x-data-grid';
import { formatCurrency, formatDate } from '../../utils/formatters';
import { useAuth } from '../../context/AuthContext';

const SupplierTable = ({
  suppliers = [],
  loading,
  onView,
  onEdit,
  onDelete,
  onViewProducts,
}) => {
  const { isAdmin, isManager } = useAuth();
  const [pageSize, setPageSize] = useState(10);

  const columns = [
    {
      field: 'name',
      headerName: 'Fournisseur',
      flex: 1.5,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <LocalShipping sx={{ mr: 1, color: 'primary.main' }} />
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {params.row.name}
            </Typography>
            {params.row.contact_person && (
              <Typography variant="caption" color="text.secondary">
                Contact: {params.row.contact_person}
              </Typography>
            )}
          </Box>
        </Box>
      ),
    },
    {
      field: 'contact',
      headerName: 'Contact',
      flex: 1,
      renderCell: (params) => (
        <Box>
          {params.row.phone && (
            <Typography variant="body2">{params.row.phone}</Typography>
          )}
          {params.row.email && (
            <Typography variant="caption" color="text.secondary">
              {params.row.email}
            </Typography>
          )}
        </Box>
      ),
    },
    {
      field: 'location',
      headerName: 'Localisation',
      flex: 1,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2">{params.row.city || '—'}</Typography>
          <Typography variant="caption" color="text.secondary">
            {params.row.country}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'product_count',
      headerName: 'Produits',
      width: 100,
      align: 'center',
      headerAlign: 'center',
      renderCell: (params) => (
        <Chip
          label={params.row.product_count || 0}
          size="small"
          icon={<Inventory />}
          variant="outlined"
        />
      ),
    },
    {
      field: 'total_spent',
      headerName: 'Total achats',
      width: 130,
      align: 'right',
      headerAlign: 'right',
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="medium">
          {formatCurrency(params.row.total_spent || 0)}
        </Typography>
      ),
    },
    {
      field: 'is_active',
      headerName: 'Statut',
      width: 100,
      renderCell: (params) => (
        <Chip
          label={params.row.is_active ? 'Actif' : 'Inactif'}
          color={params.row.is_active ? 'success' : 'default'}
          size="small"
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 150,
      sortable: false,
      renderCell: (params) => (
        <Stack direction="row" spacing={1}>
          <Tooltip title="Voir détails">
            <IconButton size="small" onClick={() => onView(params.row)}>
              <Visibility fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Voir produits">
            <IconButton size="small" onClick={() => onViewProducts(params.row)}>
              <Inventory fontSize="small" />
            </IconButton>
          </Tooltip>
          {(isAdmin || isManager) && (
            <>
              <Tooltip title="Modifier">
                <IconButton size="small" onClick={() => onEdit(params.row)}>
                  <Edit fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Désactiver">
                <IconButton
                  size="small"
                  onClick={() => onDelete(params.row)}
                  color="error"
                >
                  <Delete fontSize="small" />
                </IconButton>
              </Tooltip>
            </>
          )}
        </Stack>
      ),
    },
  ];

  return (
    <Box sx={{ height: 600, width: '100%' }}>
      <DataGrid
        rows={suppliers}
        columns={columns}
        pageSize={pageSize}
        onPageSizeChange={(newSize) => setPageSize(newSize)}
        rowsPerPageOptions={[10, 25, 50]}
        pagination
        loading={loading}
        disableSelectionOnClick
        getRowId={(row) => row.id}
        sx={{
          border: 'none',
          '& .MuiDataGrid-columnHeaders': {
            backgroundColor: 'background.paper',
            fontWeight: 600,
          },
        }}
      />
    </Box>
  );
};

export default SupplierTable;