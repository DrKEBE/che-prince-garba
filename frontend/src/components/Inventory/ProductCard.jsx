import React, { useState } from 'react';
import {
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  IconButton,
  Menu,
  MenuItem,
  LinearProgress,
  Avatar,
} from '@mui/material';
import {
  Edit,
  Delete,
  MoreVert,
  Inventory,
  ShoppingCart,
  Warning,
  CheckCircle,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { formatCurrency } from '../../utils/formatters';

const ProductCard = ({ product, onEdit, onDelete, canManage }) => {
  const [anchorEl, setAnchorEl] = useState(null);

  const stock = product.current_stock || 0;
  const threshold = product.alert_threshold;
  let stockStatus = { label: 'En stock', color: 'success', icon: CheckCircle };
  if (stock <= 0) stockStatus = { label: 'Rupture', color: 'error', icon: Warning };
  else if (stock <= threshold) stockStatus = { label: 'Stock faible', color: 'warning', icon: Warning };

  const margin = product.margin || 0;
  const marginColor = margin >= 30 ? 'success' : margin >= 20 ? 'info' : 'warning';

  return (
    <motion.div whileHover={{ y: -4, transition: { duration: 0.2 } }}>
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          borderRadius: 3,
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        {/* Image */}
        <Box sx={{ position: 'relative', pt: '75%', bgcolor: 'grey.100' }}>
          {product.images?.[0] ? (
            <CardMedia
              component="img"
              image={`http://localhost:8000/uploads/products/${product.images[0]}`}
              alt={product.name}
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />
          ) : (
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'grey.200',
              }}
            >
              <Inventory sx={{ fontSize: 48, color: 'grey.400' }} />
            </Box>
          )}
          <Chip
            label={stockStatus.label}
            size="small"
            color={stockStatus.color}
            icon={stockStatus.icon}
            sx={{
              position: 'absolute',
              top: 12,
              left: 12,
              fontWeight: 'bold',
              backdropFilter: 'blur(4px)',
              bgcolor: 'rgba(255,255,255,0.9)',
            }}
          />
          {canManage && (
            <IconButton
              size="small"
              sx={{ position: 'absolute', top: 12, right: 12, bgcolor: 'background.paper' }}
              onClick={(e) => setAnchorEl(e.currentTarget)}
            >
              <MoreVert />
            </IconButton>
          )}
        </Box>

        <CardContent sx={{ flexGrow: 1, p: 2 }}>
          <Typography variant="h6" component="h3" noWrap sx={{ fontWeight: 600, mb: 0.5 }}>
            {product.name}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom noWrap>
            {product.category} {product.brand && `• ${product.brand}`}
          </Typography>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', mt: 1 }}>
            <Typography variant="h5" color="primary.main" fontWeight="bold">
              {formatCurrency(product.selling_price)}
            </Typography>
            <Chip
              label={`Marge ${margin.toFixed(1)}%`}
              size="small"
              color={marginColor}
              variant="outlined"
            />
          </Box>

          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Stock: <strong>{stock}</strong> / {threshold}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={Math.min((stock / threshold) * 100, 100)}
              color={stockStatus.color}
              sx={{ mt: 0.5, height: 6, borderRadius: 3 }}
            />
          </Box>

          {product.supplier_info && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Fournisseur: {product.supplier_info.name}
            </Typography>
          )}
        </CardContent>

        <CardActions sx={{ p: 2, pt: 0 }}>
          <Button
            fullWidth
            variant="outlined"
            size="small"
            startIcon={<ShoppingCart />}
            sx={{ borderRadius: 3 }}
          >
            Vendre
          </Button>
        </CardActions>

        <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
          <MenuItem onClick={() => { onEdit(product); setAnchorEl(null); }}>
            <Edit fontSize="small" sx={{ mr: 1 }} /> Modifier
          </MenuItem>
          <MenuItem onClick={() => { onDelete(product.id); setAnchorEl(null); }} sx={{ color: 'error.main' }}>
            <Delete fontSize="small" sx={{ mr: 1 }} /> Désactiver
          </MenuItem>
        </Menu>
      </Card>
    </motion.div>
  );
};

export default ProductCard;