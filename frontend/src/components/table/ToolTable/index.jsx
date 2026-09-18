import React from 'react';
import { Table, TableHead, TableBody, TableRow, TableCell, TableContainer, Paper, TablePagination, TableSortLabel } from '@mui/material';
import { StyledTableCell } from './styles';
import { Link } from 'react-router-dom';

// Columns the API can sort on (POST /api/storeproducts/search/ `sort.field`).
const SORTABLE_COLUMNS = {
  id: 'id',
  external_id: 'external_id',
  name: 'site_name',
  price: 'price',
  source: 'source',
  store: 'store',
  date: 'date',
  region: 'region',
  storage_condition: 'storage_condition',
  primary_package_material: 'primary_package_material',
};

const ToolTable = ({ columns, data, totalCount, page, rowsPerPage, onPageChange, onRowsPerPageChange, sortField, sortOrder, onSortChange }) => {
  const renderCell = (column, item) => {
    switch (column) {
      case 'id':
        return <Link to={`/tools/product-browser/${item.id}`} target="_blank">{item.id}</Link>;
      case 'name':
        return item.site_name;
      case 'price':
        return item.price;
      case 'source':
        return item.source?.name ?? '';
      case 'store':
        return item.store?.name ?? '';
      case 'date':
        return item.scrape_batch?.datetime ?? '';
      case 'region':
        return item.scrape_batch?.region ?? '';
      case 'categories':
        return item.categories && item.categories.length > 0
          ? [...item.categories]
              .sort((a, b) => a.level - b.level)
              .map(cat => cat.name)
              .join(' > ')
          : 'No category';
      default:
        return item[column] ?? '';
    }
  };

  const headerMapping = {
    id: 'ID',
    external_id: 'External ID',
    name: 'Product Name',
    price: 'Price',
    source: 'Source',
    store: 'Store',
    date: 'Date',
    region: 'Region',
    categories: 'Categories',
    storage_condition: 'Storage Condition',
    primary_package_material: 'Packaging Material',
    allergens_warnings: 'Allergens',
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <StyledTableCell key={column}>
                {onSortChange && SORTABLE_COLUMNS[column] ? (
                  <TableSortLabel
                    active={sortField === column}
                    direction={sortField === column ? sortOrder : 'asc'}
                    onClick={() => onSortChange(column)}
                  >
                    {headerMapping[column] || column}
                  </TableSortLabel>
                ) : (
                  headerMapping[column] || column
                )}
              </StyledTableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((item, index) => (
            <TableRow key={item.id ?? index}>
              {columns.map((column) => (
                <TableCell key={column}>
                  {renderCell(column, item)}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <TablePagination
        component="div"
        count={totalCount}
        page={page}
        onPageChange={onPageChange}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={onRowsPerPageChange}
        rowsPerPageOptions={[10, 25, 50, 100]}
      />
    </TableContainer>
  );
};

export default ToolTable;
