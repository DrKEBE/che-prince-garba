import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Button,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import {
  Edit,
  Delete,
  MoreVert,
  Phone,
  Email,
  LocationOn,
  Inventory,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { formatCurrency } from '../../utils/formatters';

const SupplierCard = ({ supplier, onEdit, onDelete, canManage }) => {
  const [anchorEl, setAnchorEl] = useState(null);

  const productsCount = supplier.product_count || 0;
  const totalSpent = supplier.total_spent || 0;

  return (
    <motion.div whileHover={{ y: -4 }}>
      <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', borderRadius: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="h6" component="h3" fontWeight="bold" noWrap>
                {supplier.name}
              </Typography>
              {supplier.contact_person && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Contact: {supplier.contact_person}
                </Typography>
              )}
            </Box>
            {canManage && (
              <IconButton size="small" onClick={(e) => setAnchorEl(e.currentTarget)}>
                <MoreVert />
              </IconButton>
            )}
          </Box>

          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
            {supplier.phone && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Phone fontSize="small" color="action" />
                <Typography variant="body2">{supplier.phone}</Typography>
              </Box>
            )}
            {supplier.email && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Email fontSize="small" color="action" />
                <Typography variant="body2" noWrap>{supplier.email}</Typography>
              </Box>
            )}
            {supplier.address && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocationOn fontSize="small" color="action" />
                <Typography variant="body2" noWrap>{supplier.address}</Typography>
              </Box>
            )}
          </Box>

          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Box>
              <Typography variant="caption" color="text.secondary">Produits fournis</Typography>
              <Typography variant="h6" color="primary.main" fontWeight="bold">
                {productsCount}
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="caption" color="text.secondary">Total achat</Typography>
              <Typography variant="h6" color="success.main" fontWeight="bold">
                {formatCurrency(totalSpent)}
              </Typography>
            </Box>
          </Box>

          <Chip
            label={supplier.is_active ? 'Actif' : 'Inactif'}
            size="small"
            color={supplier.is_active ? 'success' : 'default'}
            sx={{ mt: 2 }}
          />
        </CardContent>

        <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
          <MenuItem onClick={() => { onEdit(supplier); setAnchorEl(null); }}>
            <Edit fontSize="small" sx={{ mr: 1 }} /> Modifier
          </MenuItem>
          <MenuItem onClick={() => { onDelete(supplier.id); setAnchorEl(null); }} sx={{ color: 'error.main' }}>
            <Delete fontSize="small" sx={{ mr: 1 }} /> Désactiver
          </MenuItem>
        </Menu>
      </Card>
    </motion.div>
  );
};

export default SupplierCard;