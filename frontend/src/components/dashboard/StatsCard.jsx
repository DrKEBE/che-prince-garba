// frontend\src\components\dashboard\StatsCard.jsx
import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  useTheme,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const StatsCard = ({
  title,
  value,
  icon,
  color = 'primary',
  trend = 0,
  subtitle,
  progress,
  onClick,
}) => {
  const getTrendColor = (trend) => {
    if (trend > 0) return 'success';
    if (trend < 0) return 'error';
    return 'info';
  };

  const getTrendIcon = (trend) => {
    if (trend > 0) return <TrendingUp sx={{ fontSize: 16 }} />;
    if (trend < 0) return <TrendingDown sx={{ fontSize: 16 }} />;
    return <TrendingFlat sx={{ fontSize: 16 }} />;
  };

  const trendColor = getTrendColor(trend);
  const TrendIcon = getTrendIcon(trend);
  const theme = useTheme();
  
  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        onClick={onClick}
        sx={{
          cursor: onClick ? 'pointer' : 'default',
          height: '100%',
          position: 'relative',
          overflow: 'hidden',
          '&:hover': {
            '& .hover-gradient': {
              opacity: 1,
            },
          },
        }}
      >
        {/* Background gradient effect */}
        <Box
          className="hover-gradient"
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '100%',
            background: `linear-gradient(135deg, ${theme.palette[color].main} 0%, transparent 100%)`,            opacity: 0.1,
            transition: 'opacity 0.3s ease',
          }}
        />

        <CardContent sx={{ position: 'relative', zIndex: 1 }}>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              mb: 2,
            }}
          >
            <Box>
              <Typography
                variant="subtitle2"
                color="text.secondary"
                gutterBottom
              >
                {title}
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {value}
              </Typography>
            </Box>
            
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                backgroundColor: `${color}.light`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: `${color}.main`,
              }}
            >
              {icon}
            </Box>
          </Box>

          {subtitle && (
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ display: 'block', mb: 1 }}
            >
              {subtitle}
            </Typography>
          )}

          {(trend !== 0 || progress !== undefined) && (
            <Box sx={{ mt: 2 }}>
              {trend !== 0 && (
                <Chip
                  icon={TrendIcon}
                  label={`${Math.abs(trend).toFixed(1)}%`}
                  size="small"
                  color={trendColor}
                  variant="outlined"
                  sx={{ mr: 1 }}
                />
              )}

              {progress !== undefined && (
                <Box sx={{ mt: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min(Math.max(progress || 0, 0), 100)}
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      backgroundColor: `${color}.light`,
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: `${color}.main`,
                        borderRadius: 3,
                      },
                    }}
                  />
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ mt: 0.5, display: 'block' }}
                  >
                    {(progress || 0).toFixed(1)}% complété
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default StatsCard;