import React, { useState, useEffect } from 'react';
import {
  Paper,
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Button,
  Chip,
  Stack,
  Grid,
  IconButton,
  Collapse,
  Typography,
} from '@mui/material';
import { Search, Clear, FilterList, ExpandMore, ExpandLess } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { PRODUCT_CATEGORIES, PRODUCT_BRANDS } from '../../constants/config';
import { inventoryService } from '../../services/inventory';

const ProductFilter = ({ onFilterChange, compact = false }) => {
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    brand: '',
    supplier_id: '',
    min_price: '',
    max_price: '',
    low_stock: false,
    out_of_stock: false,
    include_inactive: false,
  });

  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [suppliers, setSuppliers] = useState([]);
  const [priceRange, setPriceRange] = useState([0, 100000]);

  useEffect(() => {
    // Charger la liste des fournisseurs pour le filtre
    inventoryService.getSuppliers({ active_only: true, limit: 100 })
      .then(data => setSuppliers(data))
      .catch(console.error);
  }, []);

  const handleChange = (field, value) => {
    const newFilters = { ...filters, [field]: value };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const handlePriceChange = (event, newValue) => {
    setPriceRange(newValue);
  };

  const handlePriceCommitted = (event, newValue) => {
    handleChange('min_price', newValue[0]);
    handleChange('max_price', newValue[1]);
  };

  const resetFilters = () => {
    const empty = {
      search: '',
      category: '',
      brand: '',
      supplier_id: '',
      min_price: '',
      max_price: '',
      low_stock: false,
      out_of_stock: false,
      include_inactive: false,
    };
    setFilters(empty);
    setPriceRange([0, 100000]);
    onFilterChange?.(empty);
  };

  const activeCount = Object.values(filters).filter(v => v && v !== '' && v !== false).length;

  const formatPrice = (val) => `${val.toLocaleString()} F`;

  return (
    <Paper
      elevation={0}
      sx={{
        p: compact ? 2 : 3,
        mb: 3,
        borderRadius: 3,
        bgcolor: 'background.paper',
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Grid container spacing={2} alignItems="center">
        {/* Barre de recherche */}
        <Grid item xs={12} md={compact ? 12 : 6}>
          <TextField
            fullWidth
            size="small"
            placeholder="Rechercher un produit (nom, SKU, code-barres)"
            value={filters.search}
            onChange={(e) => handleChange('search', e.target.value)}
            InputProps={{
              startAdornment: <Search color="action" sx={{ mr: 1 }} />,
              endAdornment: filters.search && (
                <IconButton size="small" onClick={() => handleChange('search', '')}>
                  <Clear fontSize="small" />
                </IconButton>
              ),
            }}
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3 } }}
          />
        </Grid>

        {compact ? (
          <Grid item xs={12} md={6}>
            <Stack direction="row" spacing={1}>
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Catégorie</InputLabel>
                <Select
                  value={filters.category}
                  label="Catégorie"
                  onChange={(e) => handleChange('category', e.target.value)}
                >
                  <MenuItem value="">Toutes</MenuItem>
                  {PRODUCT_CATEGORIES.map(cat => (
                    <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => setAdvancedOpen(!advancedOpen)}
                endIcon={advancedOpen ? <ExpandLess /> : <ExpandMore />}
              >
                Filtres {activeCount > 0 && `(${activeCount})`}
              </Button>
              {activeCount > 0 && (
                <Button variant="text" color="secondary" onClick={resetFilters} startIcon={<Clear />}>
                  Réinitialiser
                </Button>
              )}
            </Stack>
          </Grid>
        ) : (
          <>
            <Grid item xs={12} md={6}>
              <Stack direction="row" spacing={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Catégorie</InputLabel>
                  <Select
                    value={filters.category}
                    label="Catégorie"
                    onChange={(e) => handleChange('category', e.target.value)}
                  >
                    <MenuItem value="">Toutes</MenuItem>
                    {PRODUCT_CATEGORIES.map(cat => (
                      <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <FormControl fullWidth size="small">
                  <InputLabel>Marque</InputLabel>
                  <Select
                    value={filters.brand}
                    label="Marque"
                    onChange={(e) => handleChange('brand', e.target.value)}
                  >
                    <MenuItem value="">Toutes</MenuItem>
                    {PRODUCT_BRANDS.map(b => (
                      <MenuItem key={b} value={b}>{b}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Stack>
            </Grid>
          </>
        )}
      </Grid>

      {/* Filtres avancés */}
      <Collapse in={advancedOpen}>
        <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Typography gutterBottom variant="subtitle2">Fournisseur</Typography>
              <FormControl fullWidth size="small">
                <Select
                  value={filters.supplier_id}
                  onChange={(e) => handleChange('supplier_id', e.target.value)}
                  displayEmpty
                >
                  <MenuItem value="">Tous les fournisseurs</MenuItem>
                  {suppliers.map(s => (
                    <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={4}>
              <Typography gutterBottom variant="subtitle2">Gamme de prix</Typography>
              <Box sx={{ px: 1 }}>
                <Slider
                  value={priceRange}
                  onChange={handlePriceChange}
                  onChangeCommitted={handlePriceCommitted}
                  valueLabelDisplay="auto"
                  valueLabelFormat={formatPrice}
                  min={0}
                  max={100000}
                  step={1000}
                />
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="caption">{formatPrice(priceRange[0])}</Typography>
                  <Typography variant="caption">{formatPrice(priceRange[1])}</Typography>
                </Stack>
              </Box>
            </Grid>

            <Grid item xs={12} md={4}>
              <Typography gutterBottom variant="subtitle2">Statut du stock</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                <Chip
                  label="Stock faible"
                  color={filters.low_stock ? 'warning' : 'default'}
                  onClick={() => handleChange('low_stock', !filters.low_stock)}
                  variant={filters.low_stock ? 'filled' : 'outlined'}
                />
                <Chip
                  label="Rupture"
                  color={filters.out_of_stock ? 'error' : 'default'}
                  onClick={() => handleChange('out_of_stock', !filters.out_of_stock)}
                  variant={filters.out_of_stock ? 'filled' : 'outlined'}
                />
                <Chip
                  label="Inactifs"
                  color={filters.include_inactive ? 'secondary' : 'default'}
                  onClick={() => handleChange('include_inactive', !filters.include_inactive)}
                  variant={filters.include_inactive ? 'filled' : 'outlined'}
                />
              </Stack>
            </Grid>
          </Grid>
        </Box>
      </Collapse>

      {/* Filtres actifs (compact) */}
      <AnimatePresence>
        {activeCount > 0 && compact && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
              <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
                Filtres actifs:
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {filters.search && (
                  <Chip
                    label={`Recherche: ${filters.search}`}
                    size="small"
                    onDelete={() => handleChange('search', '')}
                  />
                )}
                {filters.category && (
                  <Chip
                    label={filters.category}
                    size="small"
                    onDelete={() => handleChange('category', '')}
                  />
                )}
                {filters.brand && (
                  <Chip
                    label={filters.brand}
                    size="small"
                    onDelete={() => handleChange('brand', '')}
                  />
                )}
                {filters.supplier_id && (
                  <Chip
                    label={`Fournisseur: ${suppliers.find(s => s.id === filters.supplier_id)?.name || ''}`}
                    size="small"
                    onDelete={() => handleChange('supplier_id', '')}
                  />
                )}
                {(filters.min_price > 0 || filters.max_price < 100000) && (
                  <Chip
                    label={`Prix: ${formatPrice(filters.min_price || 0)} - ${formatPrice(filters.max_price || 100000)}`}
                    size="small"
                    onDelete={() => {
                      handleChange('min_price', '');
                      handleChange('max_price', '');
                      setPriceRange([0, 100000]);
                    }}
                  />
                )}
                {filters.low_stock && (
                  <Chip label="Stock faible" size="small" onDelete={() => handleChange('low_stock', false)} />
                )}
                {filters.out_of_stock && (
                  <Chip label="Rupture" size="small" onDelete={() => handleChange('out_of_stock', false)} />
                )}
              </Stack>
            </Box>
          </motion.div>
        )}
      </AnimatePresence>
    </Paper>
  );
};

export default ProductFilter;