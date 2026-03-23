// frontend\src\components\dashboard\SalesChart.jsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  Grid,
  Chip,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  Download,
  CalendarToday,
  AttachMoney,
  ShoppingCart,
  TrendingDown,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import api from '../../services/api';
import { formatCurrency, formatDate, formatPercentage } from '../../utils/formatters';
import { dashboardService } from '../../services/dashboard';

// Custom tooltip for charts
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <Card sx={{ p: 2, boxShadow: 3, bgcolor: 'background.paper' }}>
        <Typography variant="subtitle2" gutterBottom>
          {label}
        </Typography>
        {payload.map((entry, index) => (
          <Typography 
            key={index} 
            variant="body2" 
            sx={{ color: entry.color, display: 'flex', alignItems: 'center', gap: 1 }}
          >
            <Box 
              sx={{ 
                width: 12, 
                height: 12, 
                borderRadius: '2px', 
                bgcolor: entry.color,
                display: 'inline-block',
                mr: 1 
              }} 
            />
            {entry.name}: {formatCurrency(entry.value)}
          </Typography>
        ))}
      </Card>
    );
  }
  return null;
};

const SalesChart = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [period, setPeriod] = useState('month');
  const [days, setDays] = useState(30);
  const [chartTab, setChartTab] = useState(0);
  const [salesData, setSalesData] = useState({
    trends: [],
    topProducts: [],
    performance: {}
  });

  // Fetch sales data
  const fetchSalesData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch trends data
      const trendsResponse = await dashboardService.getSalesTrend(days, period === 'month' ? 'day' : period);
      const trendsData = trendsResponse.data || [];

      // Fetch top products
      const productsResponse = await dashboardService.getTopProducts(10, days, 'revenue');
      const productsData = productsResponse.products || [];

      // Fetch performance metrics
      const metricsResponse = await dashboardService.getPerformanceMetrics(period);
      const metricsData = metricsResponse || {};

      setSalesData({
        trends: trendsData,
        topProducts: productsData,
        performance: metricsData
      });
    } catch (err) {
      console.error('Error fetching sales data:', err);
      setError('Erreur lors du chargement des données des ventes');
    } finally {
      setLoading(false);
    }
  }, [days, period]);

  useEffect(() => {
    fetchSalesData();
  }, [fetchSalesData]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setChartTab(newValue);
  };

  // Prepare chart data
  const getTrendChartData = () => {
    return salesData.trends.map(item => ({
      name: item.period,
      revenue: item.amount || 0,
      profit: item.profit || 0,
      sales: item.sales_count || 0,
      avgTicket: item.avg_ticket || 0,
      netAmount: item.net_amount || 0
    }));
  };

  const getCategoryData = () => {
    const categories = salesData.topProducts.reduce((acc, product) => {
      const category = product.category || 'Autre';
      if (!acc[category]) {
        acc[category] = { name: category, revenue: 0, profit: 0, count: 0 };
      }
      acc[category].revenue += product.total_revenue || 0;
      acc[category].profit += product.total_profit || 0;
      acc[category].count += product.total_sold || 0;
      return acc;
    }, {});

    return Object.values(categories)
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, 6);
  };

  const getTopProductsData = () => {
    return salesData.topProducts.slice(0, 8).map(product => ({
      name: product.name.length > 20 ? product.name.substring(0, 20) + '...' : product.name,
      revenue: product.total_revenue || 0,
      profit: product.total_profit || 0,
      quantity: product.total_sold || 0,
      margin: product.margin_percentage || 0
    }));
  };

  // Handle export
  const handleExport = () => {
    const dataStr = JSON.stringify(salesData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    const exportFileDefaultName = `ventes_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Chart colors
  const chartColors = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.success.main,
    theme.palette.warning.main,
    theme.palette.error.main,
    theme.palette.info.main,
  ];

  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Box sx={{ width: '100%', textAlign: 'center' }}>
            <LinearProgress sx={{ mb: 2 }} />
            <Typography variant="body2" color="text.secondary">
              Chargement des données...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Box sx={{ textAlign: 'center' }}>
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
            <IconButton onClick={fetchSalesData} color="primary">
              Réessayer
            </IconButton>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <TrendingUp color="primary" />
            <Typography variant="h6">Analyse des Ventes</Typography>
          </Box>
        }
        subheader="Tendances et performance des ventes"
        action={
          <Box display="flex" alignItems="center" gap={1}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Période</InputLabel>
              <Select
                value={period}
                label="Période"
                onChange={(e) => setPeriod(e.target.value)}
              >
                <MenuItem value="day">Journalier</MenuItem>
                <MenuItem value="week">Hebdomadaire</MenuItem>
                <MenuItem value="month">Mensuel</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 100 }}>
              <InputLabel>Jours</InputLabel>
              <Select
                value={days}
                label="Jours"
                onChange={(e) => setDays(e.target.value)}
              >
                <MenuItem value={7}>7 jours</MenuItem>
                <MenuItem value={30}>30 jours</MenuItem>
                <MenuItem value={90}>90 jours</MenuItem>
              </Select>
            </FormControl>
            <Tooltip title="Exporter les données">
              <IconButton onClick={handleExport} size="small">
                <Download />
              </IconButton>
            </Tooltip>
          </Box>
        }
      />
      <CardContent>
        {/* Tabs for different chart types */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={chartTab} onChange={handleTabChange} centered>
            <Tab icon={<TrendingUp />} label="Tendances" />
            <Tab icon={<BarChartIcon />} label="Top Produits" />
            <Tab icon={<PieChartIcon />} label="Catégories" />
          </Tabs>
        </Box>

        {/* Trends Chart */}
        {chartTab === 0 && (
          <Box sx={{ height: 350 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={getTrendChartData()}>
                <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                <XAxis 
                  dataKey="name" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => {
                    if (period === 'day') return value.split('-').slice(2).join('/');
                    if (period === 'week') return `S${value.split('-W')[1]}`;
                    return value;
                  }}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => formatCurrency(value)}
                />
                <RechartsTooltip content={<CustomTooltip />} />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke={chartColors[0]}
                  fill={chartColors[0]}
                  fillOpacity={0.1}
                  strokeWidth={2}
                  name="Chiffre d'affaires"
                />
                <Area
                  type="monotone"
                  dataKey="profit"
                  stroke={chartColors[2]}
                  fill={chartColors[2]}
                  fillOpacity={0.1}
                  strokeWidth={2}
                  name="Profit"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Box>
        )}

        {/* Top Products Chart */}
        {chartTab === 1 && (
          <Box sx={{ height: 350 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={getTopProductsData()}>
                <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                <XAxis 
                  dataKey="name" 
                  angle={-45}
                  textAnchor="end"
                  height={70}
                  tick={{ fontSize: 11 }}
                />
                <YAxis 
                  tickFormatter={(value) => formatCurrency(value)}
                  tick={{ fontSize: 12 }}
                />
                <RechartsTooltip content={<CustomTooltip />} />
                <Legend />
                <Bar
                  dataKey="revenue"
                  fill={chartColors[0]}
                  name="Revenu"
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="profit"
                  fill={chartColors[2]}
                  name="Profit"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </Box>
        )}

        {/* Categories Chart */}
        {chartTab === 2 && (
          <Box sx={{ height: 350 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={getCategoryData()}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${formatPercentage(entry.revenue / salesData.topProducts.reduce((sum, p) => sum + (p.total_revenue || 0), 0) * 100, 0)}`}
                  outerRadius={100}
                  innerRadius={40}
                  paddingAngle={2}
                  dataKey="revenue"
                >
                  {getCategoryData().map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={chartColors[index % chartColors.length]} 
                    />
                  ))}
                </Pie>
                <RechartsTooltip 
                  formatter={(value) => [formatCurrency(value), 'Revenu']}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Box>
        )}

        {/* Performance Metrics */}
        {salesData.performance.sales_metrics && (
          <Box sx={{ mt: 4, pt: 3, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="medium">
              Métriques de Performance
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Panier Moyen
                  </Typography>
                  <Typography variant="h5" color="primary.main" fontWeight="bold">
                    {formatCurrency(salesData.performance.sales_metrics?.avg_ticket || 0)}
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Marge
                  </Typography>
                  <Typography variant="h5" color="success.main" fontWeight="bold">
                    {formatPercentage(salesData.performance.sales_metrics?.profit_margin || 0)}
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Conversion
                  </Typography>
                  <Typography variant="h5" color="info.main" fontWeight="bold">
                    {formatPercentage(salesData.performance.performance_metrics?.conversion_rate || 0)}
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Clients Actifs
                  </Typography>
                  <Typography variant="h5" color="warning.main" fontWeight="bold">
                    {salesData.performance.client_metrics?.active_clients || 0}
                  </Typography>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default SalesChart;