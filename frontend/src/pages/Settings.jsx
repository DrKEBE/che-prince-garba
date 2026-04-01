import React from 'react';
import { Container, Typography, Paper } from '@mui/material';

export default function Settings() {
  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>Paramètres</Typography>
        <Typography variant="body1">Paramètres de l'application...</Typography>
      </Paper>
    </Container>
  );
}