// frontend\src\components\products\ProductCard.jsx
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  CardActions,
  CardHeader,
  Typography,
  Box,
  Chip,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  LinearProgress,
  Avatar,
  Badge,
  Stack,
  Divider,
} from '@mui/material';
import {
  Edit as EditIcon,
  Inventory as InventoryIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  ShoppingCart as ShoppingCartIcon,
  LocalOffer as LocalOfferIcon,
  Category as CategoryIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { formatCurrency, formatDate, formatStockStatus } from '../../utils/formatters';
import { productService } from '../../services/products';
import { useNavigate } from 'react-router-dom';

const ProductCard = ({ product, onEdit, onDelete, onStockUpdate, compact = false }) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);

  const open = Boolean(anchorEl);

  const handleMenuClick = (event) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleEdit = () => {
    handleMenuClose();
    if (onEdit) onEdit(product);
  };

  const handleDelete = async () => {
    handleMenuClose();
    if (window.confirm(`Êtes-vous sûr de vouloir désactiver ${product.name} ?`)) {
      setLoading(true);
      try {
        await productService.deleteProduct(product.id);
        if (onDelete) onDelete(product.id);
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleStockUpdate = () => {
    handleMenuClose();
    if (onStockUpdate) onStockUpdate(product);
  };

  const handleViewDetails = () => {
    navigate(`/products/${product.id}`);
  };

  const getStockStatusColor = (status) => {
    switch (status) {
      case 'RUPTURE':
        return 'error';
      case 'ALERTE':
        return 'warning';
      case 'EN_STOCK':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStockStatusIcon = (status) => {
    switch (status) {
      case 'RUPTURE':
        return <ErrorIcon />;
      case 'ALERTE':
        return <WarningIcon />;
      case 'EN_STOCK':
        return <CheckCircleIcon />;
      default:
        return <InventoryIcon />;
    }
  };

  const getStockPercentage = () => {
    if (product.stock <= 0) return 0;
    return Math.min(100, (product.stock / product.alert_threshold) * 100);
  };

  const getPriceMargin = () => {
    const margin = product.selling_price - product.purchase_price;
    const marginPercentage = (margin / product.purchase_price) * 100;
    return { margin, marginPercentage };
  };

  const priceMargin = getPriceMargin();

  if (compact) {
    return (
      <motion.div
        whileHover={{ y: -4, transition: { duration: 0.2 } }}
        whileTap={{ scale: 0.98 }}
      >
        <Card
          sx={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            cursor: 'pointer',
            '&:hover': {
              boxShadow: (theme) => theme.shadows[8],
            },
          }}
          onClick={handleViewDetails}
        >
          {/* Image avec badge de statut */}
          <Box sx={{ position: 'relative' }}>
            <CardMedia
              component="div"
              sx={{
                pt: '100%',
                position: 'relative',
                bgcolor: 'grey.100',
                backgroundImage: product.images && product.images.length > 0 
                  ? `url(/uploads/products/${product.images[0]})`
                  : 'none',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
              }}
            >
              {(!product.images || product.images.length === 0) && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <InventoryIcon sx={{ fontSize: 48, color: 'grey.400' }} />
                </Box>
              )}
            </CardMedia>
            <Box sx={{ position: 'absolute', top: 8, left: 8 }}>
              <Chip
                icon={getStockStatusIcon(product.status)}
                label={product.status}
                size="small"
                color={getStockStatusColor(product.status)}
                sx={{ fontWeight: 'bold', backdropFilter: 'blur(4px)' }}
              />
            </Box>
            <Box sx={{ position: 'absolute', top: 8, right: 8 }}>
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsFavorite(!isFavorite);
                }}
                sx={{
                  backgroundColor: 'white',
                  '&:hover': { backgroundColor: 'grey.100' },
                }}
              >
                {isFavorite ? (
                  <StarIcon sx={{ color: 'warning.main' }} />
                ) : (
                  <StarBorderIcon />
                )}
              </IconButton>
            </Box>
          </Box>

          <CardContent sx={{ flexGrow: 1, p: 2 }}>
            <Typography
              variant="subtitle2"
              color="text.secondary"
              gutterBottom
              sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
            >
              <CategoryIcon fontSize="small" />
              {product.category}
            </Typography>
            
            <Typography variant="h6" component="h3" noWrap gutterBottom>
              {product.name}
            </Typography>

            {product.brand && (
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                Marque: {product.brand}
              </Typography>
            )}

            <Box sx={{ mt: 2 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="h6" color="primary.main" fontWeight="bold">
                  {formatCurrency(product.selling_price)}
                </Typography>
                <Chip
                  label={`${priceMargin.marginPercentage.toFixed(1)}%`}
                  size="small"
                  color="success"
                  variant="outlined"
                  sx={{ fontWeight: 'medium' }}
                />
              </Stack>

              <Typography variant="caption" color="text.secondary">
                Coût: {formatCurrency(product.purchase_price)}
              </Typography>
            </Box>

            <Box sx={{ mt: 2 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={1}>
                <Typography variant="body2" color="text.secondary">
                  Stock: {product.stock}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Seuil: {product.alert_threshold}
                </Typography>
              </Stack>
              <LinearProgress
                variant="determinate"
                value={getStockPercentage()}
                color={getStockStatusColor(product.status)}
                sx={{ mt: 0.5, height: 4, borderRadius: 2 }}
              />
            </Box>
          </CardContent>

          <Divider />
          <CardActions sx={{ p: 1, justifyContent: 'space-between' }}>
            <Button
              size="small"
              startIcon={<ShoppingCartIcon />}
              onClick={(e) => {
                e.stopPropagation();
                // Ajouter au panier
              }}
            >
              Vendre
            </Button>
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                handleMenuClick(e);
              }}
            >
              <MoreVertIcon />
            </IconButton>
          </CardActions>
        </Card>

        {/* Menu contextuel */}
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleMenuClose}
          onClick={(e) => e.stopPropagation()}
        >
          <MenuItem onClick={handleEdit}>
            <EditIcon fontSize="small" sx={{ mr: 1 }} />
            Modifier
          </MenuItem>
          <MenuItem onClick={handleStockUpdate}>
            <InventoryIcon fontSize="small" sx={{ mr: 1 }} />
            Gérer le stock
          </MenuItem>
          <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
            <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
            Désactiver
          </MenuItem>
        </Menu>
      </motion.div>
    );
  }

  // Version complète
  return (
    <motion.div
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      whileTap={{ scale: 0.98 }}
    >
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'visible',
          '&:hover': {
            boxShadow: (theme) => theme.shadows[8],
          },
        }}
      >
        {/* Header avec actions */}
        <CardHeader
          avatar={
            <Avatar
              sx={{
                bgcolor: (theme) => theme.palette[getStockStatusColor(product.status)].main,
              }}
            >
              {getStockStatusIcon(product.status)}
            </Avatar>
          }
          action={
            <>
              <IconButton
                aria-label="favorite"
                onClick={() => setIsFavorite(!isFavorite)}
                size="small"
              >
                {isFavorite ? (
                  <StarIcon sx={{ color: 'warning.main' }} />
                ) : (
                  <StarBorderIcon />
                )}
              </IconButton>
              <IconButton
                aria-label="settings"
                onClick={handleMenuClick}
                size="small"
              >
                <MoreVertIcon />
              </IconButton>
            </>
          }
          title={
            <Typography variant="h6" component="h3" noWrap>
              {product.name}
            </Typography>
          }
          subheader={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
              <Chip
                label={product.category}
                size="small"
                icon={<CategoryIcon />}
                variant="outlined"
              />
              {product.brand && (
                <Chip
                  label={product.brand}
                  size="small"
                  variant="outlined"
                />
              )}
            </Box>
          }
        />

        {/* Image principale */}
        <Box sx={{ position: 'relative', mx: 2, borderRadius: 2, overflow: 'hidden' }}>
          <CardMedia
            component="div"
            sx={{
              pt: '56.25%', // 16:9
              position: 'relative',
              bgcolor: 'grey.100',
              backgroundImage: product.images && product.images.length > 0 
                ? `url(/uploads/products/${product.images[0]})`
                : 'none',
              backgroundSize: 'cover',
              backgroundPosition: 'center',
            }}
          >
            {(!product.images || product.images.length === 0) && (
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <InventoryIcon sx={{ fontSize: 64, color: 'grey.400' }} />
              </Box>
            )}
            <Box sx={{ position: 'absolute', top: 16, left: 16 }}>
              <Badge
                badgeContent={product.images?.length || 0}
                color="primary"
                showZero
              >
                <Chip
                  icon={getStockStatusIcon(product.status)}
                  label={product.status}
                  size="small"
                  color={getStockStatusColor(product.status)}
                  sx={{ fontWeight: 'bold', backdropFilter: 'blur(4px)' }}
                />
              </Badge>
            </Box>
          </CardMedia>
        </Box>

        <CardContent sx={{ flexGrow: 1 }}>
          {/* Description */}
          {product.description && (
            <Typography variant="body2" color="text.secondary" paragraph>
              {product.description.length > 100
                ? `${product.description.substring(0, 100)}...`
                : product.description}
            </Typography>
          )}

          {/* Informations produit */}
          <Box sx={{ mb: 2 }}>
            <Stack direction="row" spacing={2} sx={{ mb: 1 }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  SKU
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {product.sku || 'N/A'}
                </Typography>
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Code-barres
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {product.barcode || 'N/A'}
                </Typography>
              </Box>
            </Stack>
          </Box>

          {/* Prix et marge */}
          <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Box>
                <Typography variant="caption" color="text.secondary" display="block">
                  Prix de vente
                </Typography>
                <Typography variant="h5" color="primary.main" fontWeight="bold">
                  {formatCurrency(product.selling_price)}
                </Typography>
              </Box>
              <Box sx={{ textAlign: 'right' }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Prix d'achat
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  {formatCurrency(product.purchase_price)}
                </Typography>
              </Box>
            </Stack>
            <Box sx={{ textAlign: 'center' }}>
              <Chip
                icon={<LocalOfferIcon />}
                label={`Marge: ${priceMargin.marginPercentage.toFixed(1)}% (${formatCurrency(priceMargin.margin)})`}
                color="success"
                variant="outlined"
                sx={{ fontWeight: 'medium' }}
              />
            </Box>
          </Box>

          {/* Stock */}
          <Box sx={{ mb: 2 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle2">
                Stock actuel
              </Typography>
              <Typography variant="h6" color={getStockStatusColor(product.status)}>
                {product.stock} unités
              </Typography>
            </Stack>
            <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Seuil d'alerte: {product.alert_threshold}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {Math.round((product.stock / product.alert_threshold) * 100)}% du seuil
              </Typography>
            </Stack>
            <LinearProgress
              variant="determinate"
              value={getStockPercentage()}
              color={getStockStatusColor(product.status)}
              sx={{ height: 6, borderRadius: 3 }}
            />
          </Box>

          {/* Informations supplémentaires */}
          <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
            {product.expiration_date && (
              <Box sx={{ flex: 1 }}>
                <Typography variant="caption" color="text.secondary" display="block">
                  Expiration
                </Typography>
                <Typography variant="body2">
                  {formatDate(product.expiration_date)}
                </Typography>
              </Box>
            )}
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="text.secondary" display="block">
                Dernière mise à jour
              </Typography>
              <Typography variant="body2">
                {formatDate(product.updated_at, 'relative')}
              </Typography>
            </Box>
          </Stack>
        </CardContent>

        <Divider />

        <CardActions sx={{ p: 2, justifyContent: 'space-between' }}>
          <Button
            variant="outlined"
            size="small"
            onClick={handleViewDetails}
          >
            Détails
          </Button>
          <Stack direction="row" spacing={1}>
            <Button
              variant="contained"
              size="small"
              startIcon={<ShoppingCartIcon />}
              onClick={() => {
                // Ajouter au panier
              }}
            >
              Vendre
            </Button>
            <Button
              variant="outlined"
              size="small"
              startIcon={<InventoryIcon />}
              onClick={handleStockUpdate}
            >
              Stock
            </Button>
          </Stack>
        </CardActions>
      </Card>

      {/* Menu contextuel */}
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEdit}>
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          Modifier le produit
        </MenuItem>
        <MenuItem onClick={handleStockUpdate}>
          <InventoryIcon fontSize="small" sx={{ mr: 1 }} />
          Gérer le stock
        </MenuItem>
        <MenuItem onClick={() => navigate(`/products/${product.id}/movements`)}>
          <InventoryIcon fontSize="small" sx={{ mr: 1 }} />
          Historique des mouvements
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Désactiver le produit
        </MenuItem>
      </Menu>
    </motion.div>
  );
};

export default ProductCard;