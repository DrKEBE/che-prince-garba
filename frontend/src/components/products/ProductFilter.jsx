// frontend\src\components\products\ProductFilter.jsx
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
  Typography,
  IconButton,
  Collapse,
  Divider,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterListIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Category as CategoryIcon,
  BrandingWatermark as BrandIcon,
  AttachMoney as MoneyIcon,
  Inventory as InventoryIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { PRODUCT_CATEGORIES, PRODUCT_BRANDS } from '../../constants/config';

const ProductFilter = ({
  onFilterChange,
  initialFilters = {},
  categories = PRODUCT_CATEGORIES,
  brands = PRODUCT_BRANDS,
  compact = false,
}) => {
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    brand: '',
    minPrice: 0,
    maxPrice: 100000,
    stockStatus: '',
    ...initialFilters,
  });

  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [priceRange, setPriceRange] = useState([0, 100000]);

  // Mettre à jour les filtres
  const updateFilter = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    if (onFilterChange) {
      onFilterChange(newFilters);
    }
  };

  // Réinitialiser les filtres
  const resetFilters = () => {
    const defaultFilters = {
      search: '',
      category: '',
      brand: '',
      minPrice: 0,
      maxPrice: 100000,
      stockStatus: '',
    };
    setFilters(defaultFilters);
    setPriceRange([0, 100000]);
    if (onFilterChange) {
      onFilterChange(defaultFilters);
    }
  };

  // Appliquer la gamme de prix
  const handlePriceChange = (event, newValue) => {
    setPriceRange(newValue);
  };

  const handlePriceChangeCommitted = (event, newValue) => {
    updateFilter('minPrice', newValue[0]);
    updateFilter('maxPrice', newValue[1]);
  };

  // Filtres actifs
  const activeFilters = Object.entries(filters).filter(
    ([key, value]) => 
      value && 
      key !== 'minPrice' && 
      key !== 'maxPrice' &&
      !(key === 'search' && value === '')
  ).length;

  const formatPrice = (value) => {
    return `${value.toLocaleString('fr-CI')} F`;
  };

  if (compact) {
    return (
      <Paper
        sx={{
          p: 2,
          mb: 3,
          borderRadius: 3,
          bgcolor: 'background.paper',
          boxShadow: (theme) => theme.shadows[2],
        }}
      >
        <Grid container spacing={2} alignItems="center">
          {/* Barre de recherche */}
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              size="small"
              placeholder="Rechercher un produit..."
              value={filters.search}
              onChange={(e) => updateFilter('search', e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />,
                endAdornment: filters.search && (
                  <IconButton
                    size="small"
                    onClick={() => updateFilter('search', '')}
                    edge="end"
                  >
                    <ClearIcon fontSize="small" />
                  </IconButton>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                },
              }}
            />
          </Grid>

          {/* Filtres rapides */}
          <Grid item xs={12} md={8}>
            <Stack direction="row" spacing={2} alignItems="center">
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Catégorie</InputLabel>
                <Select
                  value={filters.category}
                  label="Catégorie"
                  onChange={(e) => updateFilter('category', e.target.value)}
                  startAdornment={<CategoryIcon sx={{ mr: 1, color: 'text.secondary' }} />}
                >
                  <MenuItem value="">
                    <em>Toutes les catégories</em>
                  </MenuItem>
                  {categories.map((cat) => (
                    <MenuItem key={cat} value={cat}>
                      {cat}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Marque</InputLabel>
                <Select
                  value={filters.brand}
                  label="Marque"
                  onChange={(e) => updateFilter('brand', e.target.value)}
                  startAdornment={<BrandIcon sx={{ mr: 1, color: 'text.secondary' }} />}
                >
                  <MenuItem value="">
                    <em>Toutes les marques</em>
                  </MenuItem>
                  {brands.map((brand) => (
                    <MenuItem key={brand} value={brand}>
                      {brand}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Button
                variant="outlined"
                startIcon={<FilterListIcon />}
                onClick={() => setAdvancedOpen(!advancedOpen)}
                endIcon={advancedOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                sx={{ whiteSpace: 'nowrap' }}
              >
                Plus de filtres
                {activeFilters > 0 && (
                  <Chip
                    label={activeFilters}
                    size="small"
                    color="primary"
                    sx={{ ml: 1 }}
                  />
                )}
              </Button>

              {(activeFilters > 0 || filters.search) && (
                <Button
                  variant="outlined"
                  color="secondary"
                  onClick={resetFilters}
                  startIcon={<ClearIcon />}
                >
                  Réinitialiser
                </Button>
              )}
            </Stack>
          </Grid>
        </Grid>

        {/* Filtres avancés */}
        <Collapse in={advancedOpen}>
          <Box sx={{ mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography gutterBottom variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <MoneyIcon fontSize="small" />
                  Gamme de prix
                </Typography>
                <Box sx={{ px: 2 }}>
                  <Slider
                    value={priceRange}
                    onChange={handlePriceChange}
                    onChangeCommitted={handlePriceChangeCommitted}
                    valueLabelDisplay="auto"
                    valueLabelFormat={formatPrice}
                    min={0}
                    max={100000}
                    step={1000}
                    marks={[
                      { value: 0, label: '0 F' },
                      { value: 50000, label: '50k F' },
                      { value: 100000, label: '100k F' },
                    ]}
                    sx={{ mt: 3 }}
                  />
                </Box>
                <Stack direction="row" justifyContent="space-between" sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Min: {formatPrice(priceRange[0])}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Max: {formatPrice(priceRange[1])}
                  </Typography>
                </Stack>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography gutterBottom variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <InventoryIcon fontSize="small" />
                  Statut du stock
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {[
                    { value: '', label: 'Tous' },
                    { value: 'EN_STOCK', label: 'En stock', color: 'success' },
                    { value: 'ALERTE', label: 'Stock faible', color: 'warning' },
                    { value: 'RUPTURE', label: 'Rupture', color: 'error' },
                  ].map((status) => (
                    <Chip
                      key={status.value}
                      label={status.label}
                      color={filters.stockStatus === status.value ? status.color : 'default'}
                      variant={filters.stockStatus === status.value ? 'filled' : 'outlined'}
                      onClick={() => updateFilter('stockStatus', status.value)}
                      clickable
                    />
                  ))}
                </Stack>
              </Grid>
            </Grid>
          </Box>
        </Collapse>

        {/* Filtres actifs */}
        <AnimatePresence>
          {activeFilters > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
                  Filtres actifs:
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {filters.search && (
                    <Chip
                      label={`Recherche: "${filters.search}"`}
                      size="small"
                      onDelete={() => updateFilter('search', '')}
                    />
                  )}
                  {filters.category && (
                    <Chip
                      label={`Catégorie: ${filters.category}`}
                      size="small"
                      onDelete={() => updateFilter('category', '')}
                    />
                  )}
                  {filters.brand && (
                    <Chip
                      label={`Marque: ${filters.brand}`}
                      size="small"
                      onDelete={() => updateFilter('brand', '')}
                    />
                  )}
                  {filters.stockStatus && (
                    <Chip
                      label={`Stock: ${filters.stockStatus === 'EN_STOCK' ? 'En stock' : filters.stockStatus === 'ALERTE' ? 'Faible' : 'Rupture'}`}
                      size="small"
                      onDelete={() => updateFilter('stockStatus', '')}
                    />
                  )}
                  {(filters.minPrice > 0 || filters.maxPrice < 100000) && (
                    <Chip
                      label={`Prix: ${formatPrice(filters.minPrice)} - ${formatPrice(filters.maxPrice)}`}
                      size="small"
                      onDelete={() => {
                        updateFilter('minPrice', 0);
                        updateFilter('maxPrice', 100000);
                        setPriceRange([0, 100000]);
                      }}
                    />
                  )}
                </Stack>
              </Box>
            </motion.div>
          )}
        </AnimatePresence>
      </Paper>
    );
  }

  // Version étendue (pour page dédiée)
  return (
    <Paper
      sx={{
        p: 3,
        mb: 4,
        borderRadius: 3,
        bgcolor: 'background.paper',
        boxShadow: (theme) => theme.shadows[3],
      }}
    >
      <Stack spacing={3}>
        {/* En-tête */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterListIcon />
            Filtres avancés
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {activeFilters > 0 && (
              <Button
                variant="outlined"
                color="secondary"
                onClick={resetFilters}
                startIcon={<ClearIcon />}
              >
                Tout effacer
              </Button>
            )}
            <Button
              variant="outlined"
              onClick={() => setAdvancedOpen(!advancedOpen)}
              endIcon={advancedOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            >
              {advancedOpen ? 'Moins de filtres' : 'Plus de filtres'}
            </Button>
          </Box>
        </Box>

        {/* Filtres principaux */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Rechercher un produit"
              value={filters.search}
              onChange={(e) => updateFilter('search', e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />,
              }}
              helperText="Recherche par nom, description, SKU ou code-barres"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Stack direction="row" spacing={2}>
              <FormControl fullWidth>
                <InputLabel>Catégorie</InputLabel>
                <Select
                  value={filters.category}
                  label="Catégorie"
                  onChange={(e) => updateFilter('category', e.target.value)}
                >
                  <MenuItem value="">
                    <em>Toutes les catégories</em>
                  </MenuItem>
                  {categories.map((cat) => (
                    <MenuItem key={cat} value={cat}>
                      {cat}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Marque</InputLabel>
                <Select
                  value={filters.brand}
                  label="Marque"
                  onChange={(e) => updateFilter('brand', e.target.value)}
                >
                  <MenuItem value="">
                    <em>Toutes les marques</em>
                  </MenuItem>
                  {brands.map((brand) => (
                    <MenuItem key={brand} value={brand}>
                      {brand}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Stack>
          </Grid>
        </Grid>

        <Divider />

        {/* Filtres avancés */}
        <Collapse in={advancedOpen}>
          <Stack spacing={3}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography gutterBottom variant="subtitle1">
                  Gamme de prix
                </Typography>
                <Box sx={{ px: 2 }}>
                  <Slider
                    value={priceRange}
                    onChange={handlePriceChange}
                    onChangeCommitted={handlePriceChangeCommitted}
                    valueLabelDisplay="auto"
                    valueLabelFormat={formatPrice}
                    min={0}
                    max={100000}
                    step={1000}
                    marks={[
                      { value: 0, label: '0 F' },
                      { value: 25000, label: '25k F' },
                      { value: 50000, label: '50k F' },
                      { value: 75000, label: '75k F' },
                      { value: 100000, label: '100k F' },
                    ]}
                    sx={{ mt: 3 }}
                  />
                </Box>
                <Stack direction="row" justifyContent="space-between" sx={{ mt: 2 }}>
                  <Typography variant="body2" fontWeight="medium">
                    {formatPrice(priceRange[0])}
                  </Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {formatPrice(priceRange[1])}
                  </Typography>
                </Stack>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography gutterBottom variant="subtitle1">
                  Statut du stock
                </Typography>
                <Stack direction="row" spacing={2} flexWrap="wrap">
                  {[
                    { value: '', label: 'Tous les produits', color: 'primary' },
                    { value: 'EN_STOCK', label: 'En stock', color: 'success' },
                    { value: 'ALERTE', label: 'Stock faible', color: 'warning' },
                    { value: 'RUPTURE', label: 'Rupture de stock', color: 'error' },
                  ].map((status) => (
                    <Button
                      key={status.value}
                      variant={filters.stockStatus === status.value ? 'contained' : 'outlined'}
                      color={status.color}
                      onClick={() => updateFilter('stockStatus', status.value)}
                      startIcon={<InventoryIcon />}
                      sx={{ mb: 1 }}
                    >
                      {status.label}
                    </Button>
                  ))}
                </Stack>
              </Grid>
            </Grid>

            {/* Options supplémentaires */}
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography gutterBottom variant="subtitle1">
                  Options supplémentaires
                </Typography>
                <Stack spacing={2}>
                  <Button
                    variant={filters.lowStock ? 'contained' : 'outlined'}
                    color="warning"
                    onClick={() => updateFilter('lowStock', !filters.lowStock)}
                    fullWidth
                  >
                    Afficher uniquement les produits avec stock faible
                  </Button>
                  <Button
                    variant={filters.includeInactive ? 'contained' : 'outlined'}
                    color="secondary"
                    onClick={() => updateFilter('includeInactive', !filters.includeInactive)}
                    fullWidth
                  >
                    Inclure les produits désactivés
                  </Button>
                </Stack>
              </Grid>
            </Grid>
          </Stack>
        </Collapse>

        {/* Résumé des filtres */}
        <AnimatePresence>
          {activeFilters > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  bgcolor: 'primary.contrastText',
                  borderColor: 'primary.main',
                }}
              >
                <Stack direction="row" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="subtitle2" color="primary.main" gutterBottom>
                      {activeFilters} filtre{activeFilters > 1 ? 's' : ''} actif{activeFilters > 1 ? 's' : ''}
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      {filters.search && (
                        <Chip
                          label={`"${filters.search}"`}
                          size="small"
                          onDelete={() => updateFilter('search', '')}
                          color="primary"
                        />
                      )}
                      {filters.category && (
                        <Chip
                          label={filters.category}
                          size="small"
                          onDelete={() => updateFilter('category', '')}
                          color="primary"
                        />
                      )}
                      {filters.brand && (
                        <Chip
                          label={filters.brand}
                          size="small"
                          onDelete={() => updateFilter('brand', '')}
                          color="primary"
                        />
                      )}
                      {filters.stockStatus && (
                        <Chip
                          label={`Stock: ${filters.stockStatus}`}
                          size="small"
                          onDelete={() => updateFilter('stockStatus', '')}
                          color="primary"
                        />
                      )}
                      {(filters.minPrice > 0 || filters.maxPrice < 100000) && (
                        <Chip
                          label={`Prix: ${formatPrice(filters.minPrice)}-${formatPrice(filters.maxPrice)}`}
                          size="small"
                          onDelete={() => {
                            updateFilter('minPrice', 0);
                            updateFilter('maxPrice', 100000);
                            setPriceRange([0, 100000]);
                          }}
                          color="primary"
                        />
                      )}
                    </Stack>
                  </Box>
                  <Button
                    size="small"
                    onClick={resetFilters}
                    startIcon={<ClearIcon />}
                  >
                    Tout effacer
                  </Button>
                </Stack>
              </Paper>
            </motion.div>
          )}
        </AnimatePresence>
      </Stack>
    </Paper>
  );
};

export default ProductFilter;