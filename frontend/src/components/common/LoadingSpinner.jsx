// frontend\src\components\common\LoadingSpinner.jsx
import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { motion } from 'framer-motion';

const LoadingSpinner = ({ message = 'Chargement...', size = 40 }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 200,
        gap: 2,
      }}
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      >
        <CircularProgress
          size={size}
          sx={{
            color: 'primary.main',
          }}
        />
      </motion.div>
      {message && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 1 }}
        >
          {message}
        </Typography>
      )}
    </Box>
  );
};

export const InlineLoader = () => (
  <Box
    sx={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 1,
    }}
  >
    <CircularProgress size={16} />
    <Typography variant="caption" color="text.secondary">
      Chargement...
    </Typography>
  </Box>
);

export default LoadingSpinner;