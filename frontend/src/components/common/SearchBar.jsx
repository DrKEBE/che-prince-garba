// frontend\src\components\common\SearchBar.jsx
import React, { useState } from 'react';
import {
  TextField,
  InputAdornment,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Box,
} from '@mui/material';
import {
  Search,
  Clear,
  FilterList,
  Tune,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const SearchBar = ({ onSearch, placeholder = "Rechercher..." }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [filters, setFilters] = useState([]);

  const handleSearch = (value) => {
    setSearchTerm(value);
    if (onSearch) {
      onSearch(value);
    }
  };

  const handleClear = () => {
    setSearchTerm('');
    if (onSearch) {
      onSearch('');
    }
  };

  const handleFilterClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setAnchorEl(null);
  };

  const availableFilters = [
    { label: 'En rupture', value: 'out_of_stock' },
    { label: 'Stock faible', value: 'low_stock' },
    { label: 'Promotions', value: 'discount' },
    { label: 'Nouveautés', value: 'new' },
  ];

  const toggleFilter = (filter) => {
    if (filters.includes(filter.value)) {
      setFilters(filters.filter(f => f !== filter.value));
    } else {
      setFilters([...filters, filter.value]);
    }
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <motion.div
        initial={{ width: 0, opacity: 0 }}
        animate={{ width: '100%', opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <TextField
          fullWidth
          size="small"
          placeholder={placeholder}
          value={searchTerm}
          onChange={(e) => handleSearch(e.target.value)}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              backgroundColor: 'background.paper',
              transition: 'all 0.2s',
              '&:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.02)',
              },
              '&.Mui-focused': {
                backgroundColor: 'white',
                boxShadow: '0 0 0 3px rgba(138, 43, 226, 0.1)',
              },
            },
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search color="action" />
              </InputAdornment>
            ),
            endAdornment: searchTerm && (
              <InputAdornment position="end">
                <IconButton
                  size="small"
                  onClick={handleClear}
                  edge="end"
                >
                  <Clear fontSize="small" />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      </motion.div>

      <IconButton
        size="small"
        onClick={handleFilterClick}
        sx={{
          backgroundColor: filters.length > 0 ? 'primary.light' : 'transparent',
          color: filters.length > 0 ? 'white' : 'text.secondary',
          '&:hover': {
            backgroundColor: filters.length > 0 ? 'primary.main' : 'action.hover',
          },
        }}
      >
        {filters.length > 0 ? <Tune /> : <FilterList />}
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleFilterClose}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: 200,
            borderRadius: 2,
          },
        }}
      >
        {availableFilters.map((filter) => (
          <MenuItem
            key={filter.value}
            onClick={() => toggleFilter(filter)}
            selected={filters.includes(filter.value)}
          >
            {filter.label}
          </MenuItem>
        ))}
      </Menu>

      {filters.length > 0 && (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          {filters.map((filterValue) => {
            const filter = availableFilters.find(f => f.value === filterValue);
            return (
              <Chip
                key={filterValue}
                label={filter?.label}
                size="small"
                onDelete={() => toggleFilter(filter)}
                color="primary"
                variant="outlined"
              />
            );
          })}
        </Box>
      )}
    </Box>
  );
};

export default SearchBar;