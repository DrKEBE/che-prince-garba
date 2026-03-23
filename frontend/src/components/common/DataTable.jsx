// frontend/src/components/common/DataTable.jsx
import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Paper,
  Skeleton,
  Box,
} from '@mui/material';

export default function DataTable({
  rows = [],
  columns = [],
  loading = false,
  defaultSortBy = '',
  defaultSortOrder = 'asc',
  onRowClick,
  pageSize = 10,
  rowsPerPageOptions = [5, 10, 25, 50],
}) {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(pageSize);
  const [orderBy, setOrderBy] = useState(defaultSortBy);
  const [order, setOrder] = useState(defaultSortOrder);

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const sortedRows = React.useMemo(() => {
    if (!orderBy) return rows;
    return rows.sort((a, b) => {
      const aVal = a[orderBy];
      const bVal = b[orderBy];
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return order === 'asc' ? aVal - bVal : bVal - aVal;
      }
      const aStr = String(aVal || '').toLowerCase();
      const bStr = String(bVal || '').toLowerCase();
      if (aStr < bStr) return order === 'asc' ? -1 : 1;
      if (aStr > bStr) return order === 'asc' ? 1 : -1;
      return 0;
    });
  }, [rows, orderBy, order]);

  const paginatedRows = sortedRows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  if (loading) {
    return (
      <TableContainer component={Paper} sx={{ borderRadius: 3, overflow: 'hidden' }}>
        <Table>
          <TableHead>
            <TableRow>
              {columns.map((col) => (
                <TableCell key={col.field}>
                  <Skeleton variant="text" width={80} />
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {[...Array(5)].map((_, i) => (
              <TableRow key={i}>
                {columns.map((col) => (
                  <TableCell key={col.field}>
                    <Skeleton variant="text" width="100%" />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  return (
    <Paper sx={{ borderRadius: 3, overflow: 'hidden', boxShadow: 3 }}>
      <TableContainer>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell
                  key={column.field}
                  sortDirection={orderBy === column.field ? order : false}
                  sx={{ fontWeight: 600, bgcolor: 'background.paper' }}
                >
                  {column.sortable ? (
                    <TableSortLabel
                      active={orderBy === column.field}
                      direction={orderBy === column.field ? order : 'asc'}
                      onClick={() => handleRequestSort(column.field)}
                    >
                      {column.headerName || column.field}
                    </TableSortLabel>
                  ) : (
                    column.headerName || column.field
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedRows.map((row, index) => (
              <TableRow
                key={row.id || index}
                hover
                onClick={() => onRowClick && onRowClick(row)}
                sx={{ cursor: onRowClick ? 'pointer' : 'default' }}
              >
                {columns.map((column) => (
                  <TableCell key={column.field}>
                    {column.renderCell ? column.renderCell({ row }) : row[column.field]}
                  </TableCell>
                ))}
              </TableRow>
            ))}
            {paginatedRows.length === 0 && (
              <TableRow>
                <TableCell colSpan={columns.length} align="center" sx={{ py: 6 }}>
                  Aucune donnée à afficher
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={rowsPerPageOptions}
        component="div"
        count={rows.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={(e, newPage) => setPage(newPage)}
        onRowsPerPageChange={(e) => {
          setRowsPerPage(parseInt(e.target.value, 10));
          setPage(0);
        }}
        labelRowsPerPage="Lignes par page"
        labelDisplayedRows={({ from, to, count }) => `${from}–${to} sur ${count}`}
      />
    </Paper>
  );
}