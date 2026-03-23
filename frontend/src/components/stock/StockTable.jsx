import React, { useState } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  IconButton,
  Tooltip,
  Chip,
  Box,
  TextField,
  InputAdornment,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  LinearProgress,
  Typography,
  Avatar,
  Badge,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Inventory as InventoryIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  ArrowDropDown as ArrowDropDownIcon,
  ArrowDropUp as ArrowDropUpIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { formatCurrency, formatDate } from '../../utils/formatters';
import { PRODUCT_CATEGORIES } from '../../constants/config';

const StockTable = ({ products, loading, onEdit, filters, onFilterChange }) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [order, setOrder] = useState('desc');
  const [orderBy, setOrderBy] = useState('current_stock');

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const getStockStatus = (stock, threshold) => {
    if (stock <= 0) {
      return { label: 'Rupture', color: 'error', icon: <ErrorIcon />, severity: 0 };
    } else if (stock <= threshold) {
      const percentage = (stock / threshold) * 100;
      if (percentage <= 20) {
        return { label: 'Critique', color: 'error', icon: <ErrorIcon />, severity: 1 };
      } else {
        return { label: 'Faible', color: 'warning', icon: <WarningIcon />, severity: 2 };
      }
    } else if (stock <= threshold * 2) {
      return { label: 'Normal', color: 'success', icon: <CheckCircleIcon />, severity: 3 };
    } else {
      return { label: 'Excédent', color: 'info', icon: <TrendingUpIcon />, severity: 4 };
    }
  };

  const stableSort = (array, comparator) => {
    const stabilizedThis = array.map((el, index) => [el, index]);
    stabilizedThis.sort((a, b) => {
      const order = comparator(a[0], b[0]);
      if (order !== 0) return order;
      return a[1] - b[1];
    });
    return stabilizedThis.map((el) => el[0]);
  };

  const getComparator = (order, orderBy) => {
    return order === 'desc'
      ? (a, b) => descendingComparator(a, b, orderBy)
      : (a, b) => -descendingComparator(a, b, orderBy);
  };

  const descendingComparator = (a, b, orderBy) => {
    if (b[orderBy] < a[orderBy]) {
      return -1;
    }
    if (b[orderBy] > a[orderBy]) {
      return 1;
    }
    return 0;
  };

  // Filtrer et trier les produits
  const filteredProducts = products?.filter(product => {
    if (filters.category && product.category !== filters.category) return false;
    if (filters.status) {
      const status = getStockStatus(product.current_stock || 0, product.alert_threshold);
      if (status.label.toLowerCase() !== filters.status.toLowerCase()) return false;
    }
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      return (
        product.name.toLowerCase().includes(searchLower) ||
        product.sku?.toLowerCase().includes(searchLower) ||
        product.barcode?.toLowerCase().includes(searchLower) ||
        product.category.toLowerCase().includes(searchLower)
      );
    }
    return true;
  }) || [];

  const sortedProducts = stableSort(filteredProducts, getComparator(order, orderBy));
  const paginatedProducts = sortedProducts.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const columns = [
    { 
      id: 'name', 
      label: 'Produit',
      sortable: true,
      width: 250,
    },
    { 
      id: 'category', 
      label: 'Catégorie',
      sortable: true,
      width: 150,
    },
    { 
      id: 'current_stock', 
      label: 'Stock',
      sortable: true,
      width: 120,
      align: 'center',
    },
    { 
      id: 'status', 
      label: 'Statut',
      sortable: false,
      width: 130,
      align: 'center',
    },
    { 
      id: 'threshold', 
      label: 'Seuil',
      sortable: false,
      width: 100,
      align: 'center',
    },
    { 
      id: 'purchase_price', 
      label: 'Prix d\'achat',
      sortable: true,
      width: 130,
      align: 'right',
    },
    { 
      id: 'value', 
      label: 'Valeur',
      sortable: true,
      width: 130,
      align: 'right',
    },
    { 
      id: 'last_movement', 
      label: 'Dernier mouvement',
      sortable: false,
      width: 150,
    },
    { 
      id: 'actions', 
      label: 'Actions',
      sortable: false,
      width: 100,
      align: 'center',
    },
  ];

  if (loading) {
    return (
      <Paper sx={{ width: '100%', borderRadius: 3 }}>
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <LinearProgress sx={{ mb: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Chargement des produits...
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      {/* Barre de filtres */}
      <Paper sx={{ p: 2, mb: 3, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            placeholder="Rechercher un produit..."
            value={filters.search || ''}
            onChange={(e) => onFilterChange({ search: e.target.value })}
            sx={{ flex: 1, minWidth: 200 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />

          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Catégorie</InputLabel>
            <Select
              value={filters.category || ''}
              label="Catégorie"
              onChange={(e) => onFilterChange({ category: e.target.value })}
            >
              <MenuItem value="">Toutes</MenuItem>
              {PRODUCT_CATEGORIES.map((category) => (
                <MenuItem key={category} value={category}>
                  {category}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Statut</InputLabel>
            <Select
              value={filters.status || ''}
              label="Statut"
              onChange={(e) => onFilterChange({ status: e.target.value })}
            >
              <MenuItem value="">Tous</MenuItem>
              <MenuItem value="Rupture">Rupture</MenuItem>
              <MenuItem value="Critique">Critique</MenuItem>
              <MenuItem value="Faible">Faible</MenuItem>
              <MenuItem value="Normal">Normal</MenuItem>
              <MenuItem value="Excédent">Excédent</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Paper>

      {/* Tableau */}
      <Paper sx={{ width: '100%', borderRadius: 3, overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                {columns.map((column) => (
                  <TableCell
                    key={column.id}
                    align={column.align}
                    style={{ width: column.width }}
                    sx={{ 
                      fontWeight: 'bold',
                      bgcolor: 'primary.main',
                      color: 'white',
                      fontSize: '0.9rem',
                    }}
                  >
                    {column.sortable ? (
                      <TableSortLabel
                        active={orderBy === column.id}
                        direction={orderBy === column.id ? order : 'asc'}
                        onClick={() => handleRequestSort(column.id)}
                        IconComponent={orderBy === column.id ? 
                          (order === 'asc' ? ArrowDropUpIcon : ArrowDropDownIcon) : 
                          undefined
                        }
                        sx={{ color: 'white !important' }}
                      >
                        {column.label}
                      </TableSortLabel>
                    ) : (
                      column.label
                    )}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            
            <TableBody>
              {paginatedProducts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={columns.length} align="center" sx={{ py: 8 }}>
                    <InventoryIcon sx={{ fontSize: 60, color: 'grey.400', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      Aucun produit trouvé
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Essayez de modifier vos critères de recherche
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                paginatedProducts.map((product) => {
                  const stock = product.current_stock || 0;
                  const threshold = product.alert_threshold || 10;
                  const status = getStockStatus(stock, threshold);
                  const productValue = stock * (product.purchase_price || 0);

                  return (
                    <motion.tr key={product.id}>
                      <TableRow
                        hover
                        sx={{ 
                          '&:hover': { bgcolor: 'action.hover' },
                          transition: 'background-color 0.2s',
                        }}
                      >
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Avatar
                              src={product.images?.[0] ? `/uploads/products/${product.images[0]}` : undefined}
                              sx={{ 
                                width: 40, 
                                height: 40,
                                bgcolor: 'primary.light',
                              }}
                            >
                              <InventoryIcon />
                            </Avatar>
                            <Box>
                              <Typography variant="subtitle2" fontWeight="medium">
                                {product.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {product.sku || 'N/A'} • {product.barcode || 'N/A'}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        
                        <TableCell>
                          <Chip 
                            label={product.category} 
                            size="small" 
                            variant="outlined"
                            sx={{ fontWeight: 'medium' }}
                          />
                        </TableCell>
                        
                        <TableCell align="center">
                          <Badge 
                            badgeContent={stock} 
                            color={status.color}
                            sx={{ 
                              '& .MuiBadge-badge': { 
                                fontSize: '0.9rem',
                                fontWeight: 'bold',
                                minWidth: 30,
                                height: 24,
                              }
                            }}
                          >
                            <Box sx={{ width: 60 }}>
                              <LinearProgress 
                                variant="determinate" 
                                value={Math.min(100, (stock / threshold) * 100)} 
                                color={status.color}
                                sx={{ 
                                  height: 6, 
                                  borderRadius: 3,
                                  bgcolor: `${status.color}.light`
                                }}
                              />
                            </Box>
                          </Badge>
                        </TableCell>
                        
                        <TableCell align="center">
                          <Tooltip title={status.label}>
                            <Chip
                              icon={status.icon}
                              label={status.label}
                              size="small"
                              color={status.color}
                              sx={{ fontWeight: 'bold' }}
                            />
                          </Tooltip>
                        </TableCell>
                        
                        <TableCell align="center">
                          <Typography variant="body2" fontWeight="medium">
                            {threshold}
                          </Typography>
                        </TableCell>
                        
                        <TableCell align="right">
                          <Typography variant="body2" color="text.secondary">
                            {formatCurrency(product.purchase_price || 0)}
                          </Typography>
                        </TableCell>
                        
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="bold" color="primary.main">
                            {formatCurrency(productValue)}
                          </Typography>
                        </TableCell>
                        
                        <TableCell>
                          <Typography variant="caption" color="text.secondary">
                            {product.updated_at ? formatDate(product.updated_at, 'relative') : 'Jamais'}
                          </Typography>
                        </TableCell>
                        
                        <TableCell align="center">
                          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                            <Tooltip title="Voir les détails">
                              <IconButton 
                                size="small"
                                onClick={() => onEdit(product)}
                                color="primary"
                              >
                                <VisibilityIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            
                            <Tooltip title="Ajuster le stock">
                              <IconButton 
                                size="small"
                                onClick={() => onEdit(product)}
                                color="info"
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    </motion.tr>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        {/* Pagination */}
        <TablePagination
          rowsPerPageOptions={[10, 25, 50]}
          component="div"
          count={filteredProducts.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Lignes par page:"
          labelDisplayedRows={({ from, to, count }) => `${from}-${to} sur ${count}`}
          sx={{
            borderTop: '1px solid',
            borderColor: 'divider',
          }}
        />
      </Paper>

      {/* Résumé */}
      {filteredProducts.length > 0 && (
        <Paper sx={{ p: 2, mt: 2, borderRadius: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              {filteredProducts.length} produits • 
              Valeur totale: {formatCurrency(
                filteredProducts.reduce((sum, product) => 
                  sum + ((product.current_stock || 0) * (product.purchase_price || 0)), 0
                )
              )}
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Chip 
                icon={<WarningIcon />}
                label={`${filteredProducts.filter(p => (p.current_stock || 0) <= (p.alert_threshold || 10)).length} en alerte`}
                color="warning"
                size="small"
                variant="outlined"
              />
              <Chip 
                icon={<ErrorIcon />}
                label={`${filteredProducts.filter(p => (p.current_stock || 0) === 0).length} ruptures`}
                color="error"
                size="small"
                variant="outlined"
              />
            </Box>
          </Box>
        </Paper>
      )}
    </motion.div>
  );
};

export default StockTable;