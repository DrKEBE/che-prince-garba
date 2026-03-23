import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import { MoreVert, Refresh } from '@mui/icons-material';

const ChartCard = ({
  title,
  children,
  action,
  loading = false,
  onRefresh,
  subtitle,
}) => {
  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader
        title={
          <Box>
            <Typography variant="h6" fontWeight="bold">
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
        }
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {onRefresh && (
              <IconButton
                size="small"
                onClick={onRefresh}
                disabled={loading}
                title="Actualiser"
              >
                <Refresh />
              </IconButton>
            )}
            {action}
          </Box>
        }
        sx={{ pb: 1 }}
      />
      <CardContent sx={{ pt: 0 }}>
        {loading ? (
          <Box
            sx={{
              height: 300,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography color="text.secondary">
              Chargement des données...
            </Typography>
          </Box>
        ) : (
          children
        )}
      </CardContent>
    </Card>
  );
};

export default ChartCard;