// frontend\src\components\common\ConfirmationModal.jsx
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton,
  Alert,
} from '@mui/material';
import { Close, Warning, CheckCircle, Error } from '@mui/icons-material';

const ConfirmationModal = ({
  open,
  onClose,
  onConfirm,
  title = 'Confirmation',
  message = 'Êtes-vous sûr de vouloir effectuer cette action ?',
  confirmText = 'Confirmer',
  cancelText = 'Annuler',
  severity = 'warning',
  loading = false,
  maxWidth = 'sm',
  children,
}) => {
  const getIcon = () => {
    switch (severity) {
      case 'error':
        return <Error color="error" />;
      case 'success':
        return <CheckCircle color="success" />;
      case 'info':
        return <Error color="info" />;
      default:
        return <Warning color="warning" />;
    }
  };

  const getColor = () => {
    switch (severity) {
      case 'error':
        return 'error';
      case 'success':
        return 'success';
      case 'info':
        return 'info';
      default:
        return 'warning';
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={maxWidth}
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
        },
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getIcon()}
            <Typography variant="h6" fontWeight="bold">
              {title}
            </Typography>
          </Box>
          <IconButton
            onClick={onClose}
            size="small"
            disabled={loading}
          >
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Alert
          severity={severity}
          variant="outlined"
          sx={{ mb: 2, borderRadius: 2 }}
        >
          {message}
        </Alert>

        {children && (
          <Box sx={{ mt: 2 }}>
            {children}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button
          onClick={onClose}
          disabled={loading}
          variant="outlined"
          sx={{ minWidth: 100 }}
        >
          {cancelText}
        </Button>
        <Button
          onClick={onConfirm}
          disabled={loading}
          variant="contained"
          color={getColor()}
          sx={{ minWidth: 100 }}
        >
          {loading ? 'Chargement...' : confirmText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmationModal;