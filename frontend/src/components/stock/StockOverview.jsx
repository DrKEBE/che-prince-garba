// frontend/src/components/stock/StockOverview.jsx
import React from 'react';
import { Grid, Card, CardHeader, Divider } from '@mui/material';
import StockMovementList from './StockMovementList';
import StockMovementForm from './StockMovementForm';

export default function StockOverview() {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={8}>
        <Card>
          <CardHeader title="Mouvements récents" />
          <Divider />
          <StockMovementList />
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card>
          <CardHeader title="Nouveau mouvement" />
          <Divider />
          <StockMovementForm />
        </Card>
      </Grid>
    </Grid>
  );
}