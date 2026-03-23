import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  LinearProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Stack,
  Button,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Refresh,
  Warning,
  Error,
  CheckCircle,
  Info,
  Download,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';
import { productService } from '../../services/products';
import stockService from '../../services/stock';
import { formatCurrency } from '../../utils/formatters';

const StockLevelChart = ({ timeRange = 'month', height = 400 }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartType, setChartType] = useState('bar');
  const [data, setData] = useState({
    products: [],
    categories: [],
    alerts: [],
    turnover: [],
  });
  const [selectedCategory, setSelectedCategory] = useState('all');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Charger les produits
      const products = await productService.getProducts({
        include_inactive: false,
      });
      
      // Analyser les données par catégorie
      const categories = {};
      const alerts = {
        out_of_stock: 0,
        critical: 0,
        low_stock: 0,
        normal: 0,
        high: 0,
      };
      
      products.forEach(product => {
        // Par catégorie
        const category = product.category || 'Non catégorisé';
        if (!categories[category]) {
          categories[category] = {
            name: category,
            total_products: 0,
            total_stock: 0,
            total_value: 0,
            low_stock_count: 0,
          };
        }
        
        categories[category].total_products++;
        categories[category].total_stock += product.current_stock || 0;
        categories[category].total_value += (product.current_stock || 0) * (product.purchase_price || 0);
        
        const status = stockService.calculateStockStatus(product);
        if (status.status === 'OUT_OF_STOCK') alerts.out_of_stock++;
        else if (status.status === 'CRITICAL') alerts.critical++;
        else if (status.status === 'LOW') alerts.low_stock++;
        else if (status.status === 'NORMAL') alerts.normal++;
        else if (status.status === 'HIGH') alerts.high++;
        
        if (product.current_stock <= (product.alert_threshold || 10)) {
          categories[category].low_stock_count++;
        }
      });
      
      // Données pour le graphique par catégorie
      const categoryData = Object.values(categories)
        .sort((a, b) => b.total_value - a.total_value)
        .slice(0, 10);
      
      // Données pour le graphique d'alertes
      const alertData = [
        { name: 'Rupture', value: alerts.out_of_stock, color: '#EF4444' },
        { name: 'Critique', value: alerts.critical, color: '#F59E0B' },
        { name: 'Faible', value: alerts.low_stock, color: '#3B82F6' },
        { name: 'Normal', value: alerts.normal, color: '#10B981' },
        { name: 'Élevé', value: alerts.high, color: '#8B5CF6' },
      ];
      
      // Données pour le graphique de rotation
      const turnoverData = [
        { month: 'Jan', rotation: 45, ideal: 30 },
        { month: 'Fév', rotation: 42, ideal: 30 },
        { month: 'Mar', rotation: 38, ideal: 30 },
        { month: 'Avr', rotation: 51, ideal: 30 },
        { month: 'Mai', rotation: 47, ideal: 30 },
        { month: 'Jun', rotation: 39, ideal: 30 },
      ];
      
      setData({
        products,
        categories: categoryData,
        alerts: alertData,
        turnover: turnoverData,
      });
    } catch (err) {
      console.error('Error loading stock data:', err);
      setError('Impossible de charger les données de stock');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [timeRange]);

  const getStockValueColor = (value, maxValue) => {
    const percentage = (value / maxValue) * 100;
    if (percentage > 70) return '#10B981';
    if (percentage > 40) return '#3B82F6';
    if (percentage > 20) return '#F59E0B';
    return '#EF4444';
  };

  if (loading) {
    return (
      <Card sx={{ height }}>
        <CardContent sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
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
      <Card sx={{ height }}>
        <CardContent sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Alert severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        {/* En-tête */}
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Box>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TrendingUp />
              Analyse des niveaux de stock
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Visualisation des stocks par catégorie et statut
            </Typography>
          </Box>
          
          <Stack direction="row" spacing={1}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Type de graphique</InputLabel>
              <Select
                value={chartType}
                label="Type de graphique"
                onChange={(e) => setChartType(e.target.value)}
              >
                <MenuItem value="bar">Barres</MenuItem>
                <MenuItem value="pie">Camembert</MenuItem>
                <MenuItem value="line">Lignes</MenuItem>
              </Select>
            </FormControl>
            
            <Tooltip title="Rafraîchir">
              <IconButton size="small" onClick={loadData}>
                <Refresh />
              </IconButton>
            </Tooltip>
          </Stack>
        </Stack>

        {/* Statistiques rapides */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary" display="block">
                Produits en stock
              </Typography>
              <Typography variant="h5" fontWeight="bold">
                {data.products.length}
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary" display="block">
                Valeur totale
              </Typography>
              <Typography variant="h5" fontWeight="bold" color="success.main">
                {formatCurrency(
                  data.products.reduce((sum, p) => 
                    sum + (p.current_stock || 0) * (p.purchase_price || 0), 0
                  )
                )}
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary" display="block">
                Stock moyen
              </Typography>
              <Typography variant="h5" fontWeight="bold">
                {Math.round(
                  data.products.reduce((sum, p) => sum + (p.current_stock || 0), 0) / data.products.length
                ) || 0}
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary" display="block">
                Taux d'alerte
              </Typography>
              <Typography variant="h5" fontWeight="bold" color="warning.main">
                {Math.round(
                  (data.alerts.reduce((sum, a) => 
                    a.name === 'Rupture' || a.name === 'Critique' || a.name === 'Faible' ? sum + a.value : sum, 0
                  ) / data.products.length) * 100
                ) || 0}%
              </Typography>
            </Card>
          </Grid>
        </Grid>

        {/* Graphique principal */}
        <Box sx={{ height: 300, mb: 3 }}>
          {chartType === 'bar' && (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.categories}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <RechartsTooltip 
                  formatter={(value) => [formatCurrency(value), 'Valeur']}
                />
                <Legend />
                <Bar 
                  dataKey="total_value" 
                  name="Valeur du stock" 
                  fill="#8A2BE2"
                  radius={[4, 4, 0, 0]}
                />
                <Bar 
                  dataKey="total_stock" 
                  name="Quantité totale" 
                  fill="#FF4081"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
          
          {chartType === 'pie' && (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.alerts}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.alerts.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
          
          {chartType === 'line' && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.turnover}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis label={{ value: 'Jours', angle: -90, position: 'insideLeft' }} />
                <RechartsTooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="rotation"
                  name="Rotation réelle"
                  stroke="#8A2BE2"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
                <Line
                  type="monotone"
                  dataKey="ideal"
                  name="Rotation idéale"
                  stroke="#10B981"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </Box>

        {/* Légende des statuts */}
        <Box sx={{ mt: 3, pt: 3, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Légende des statuts
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap">
            <Chip
              icon={<Error />}
              label="Rupture"
              size="small"
              color="error"
              variant="outlined"
            />
            <Chip
              icon={<Warning />}
              label="Critique"
              size="small"
              color="warning"
              variant="outlined"
            />
            <Chip
              icon={<Info />}
              label="Faible"
              size="small"
              color="info"
              variant="outlined"
            />
            <Chip
              icon={<CheckCircle />}
              label="Normal"
              size="small"
              color="success"
              variant="outlined"
            />
            <Chip
              icon={<TrendingUp />}
              label="Élevé"
              size="small"
              color="secondary"
              variant="outlined"
            />
          </Stack>
        </Box>

        {/* Recommandations */}
        {data.alerts.some(a => a.name === 'Rupture' || a.name === 'Critique') && (
          <Box sx={{ mt: 3, p: 2, bgcolor: 'warning.light', borderRadius: 2 }}>
            <Typography variant="subtitle2" fontWeight="medium" gutterBottom color="warning.dark">
              <Warning fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
              Recommandations
            </Typography>
            <Typography variant="body2" color="warning.dark">
              {data.alerts.find(a => a.name === 'Rupture')?.value || 0} produits sont en rupture et 
              {data.alerts.find(a => a.name === 'Critique')?.value || 0} sont en stock critique.
              Pensez à réapprovisionner ces produits rapidement.
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default StockLevelChart;