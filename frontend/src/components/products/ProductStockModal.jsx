// frontend/src/components/products/ProductStockModal.jsx
import React from 'react';
import { Dialog, DialogTitle, DialogContent, IconButton, Box, Typography } from '@mui/material';
import { Close as CloseIcon, Inventory as InventoryIcon } from '@mui/icons-material';
import StockMovement from './StockMovement';
import { motion } from 'framer-motion';

const ProductStockModal = ({ open, onClose, product }) => {
  if (!product) return null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 4,
          overflow: 'hidden',
          background: 'linear-gradient(145deg, #ffffff 0%, #f9f9ff 100%)',
        },
      }}
      TransitionComponent={motion.div}
      transitionDuration={400}
    >
      <DialogTitle sx={{ 
        background: 'linear-gradient(135deg, #8A2BE2 0%, #FF4081 100%)',
        color: 'white',
        py: 2 
      }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h5" fontWeight="bold" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <InventoryIcon />
            Gestion du stock - {product.name}
          </Typography>
          <IconButton onClick={onClose} sx={{ color: 'white' }}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent dividers sx={{ p: 3, bgcolor: 'background.default' }}>
        <StockMovement
          productId={product.id}
          productName={product.name}
          productPurchasePrice={product.purchase_price}
          onMovementCreated={onClose}
        />
      </DialogContent>
    </Dialog>
  );
};

export default ProductStockModal;