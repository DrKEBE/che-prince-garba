import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Button,
  Typography,
  Box,
} from '@mui/material';
import { Close } from '@mui/icons-material';

const ModalForm = ({
  open,
  onClose,
  title,
  children,
  maxWidth = 'md',
  fullWidth = true,
  actions = true,
  cancelText = 'Annuler',
  confirmText = 'Enregistrer',
  onConfirm,
  loading = false,
}) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={maxWidth}
      fullWidth={fullWidth}
      PaperProps={{ sx: { borderRadius: 3 } }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">{title}</Typography>
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent dividers>{children}</DialogContent>
      {actions && (
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            {cancelText}
          </Button>
          <Button
            onClick={onConfirm}
            variant="contained"
            disabled={loading}
            color="primary"
          >
            {loading ? 'Chargement...' : confirmText}
          </Button>
        </DialogActions>
      )}
    </Dialog>
  );
};

export default ModalForm;