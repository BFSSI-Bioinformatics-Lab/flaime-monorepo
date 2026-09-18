import React, { useState, useEffect, useCallback } from 'react';
import {
  TableContainer, Table, TableHead, TableRow, TableCell, TableBody,
  Pagination, TextField, Paper, Typography, Card, CardContent, Divider, TableSortLabel
} from '@mui/material';
import { Link } from 'react-router-dom';
import SourceSelector from '../../../components/inputs/SourceSelector';
import { ResetButton } from '../../../components/buttons/ResetButton';
import { DownloadResultButton } from '../../../components/buttons/DownloadResultButton';
import { buildProductBrowserBody } from '../util';
import { SearchStoreProducts, GetStoreCounts } from '../../../api/services/StoreProductSearchService';

// ProductTable column key -> API sort field (POST /api/storeproducts/search/).
const SORT_FIELD_MAP = {
  id: 'id',
  external_id: 'external_id',
  store: 'store',
  source: 'source',
  name: 'site_name',
};

const ROWS_PER_PAGE = 15;

const ProductBrowser = () => {
  const [products, setProducts] = useState([]);
  const [page, setPage] = useState(1);
  const [totalProducts, setTotalProducts] = useState(0);
  const [searchTerms, setSearchTerms] = useState({
    id: '',
    external_id: '',
    sourceName: '',
    siteName: '',
  });
  const [storeCounts, setStoreCounts] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [sortState, setSortState] = useState({ field: null, order: 'asc' });

  const buildBody = useCallback(() => {
    const body = buildProductBrowserBody(searchTerms);
    if (sortState.field) {
      body.sort = { field: SORT_FIELD_MAP[sortState.field], order: sortState.order };
    }
    return body;
  }, [searchTerms, sortState]);

  const fetchProducts = useCallback(async () => {
    const body = buildBody();

    const [searchRes, countsRes] = await Promise.all([
      SearchStoreProducts({ ...body, page, page_size: ROWS_PER_PAGE }),
      GetStoreCounts(body),
    ]);

    if (!searchRes.error && searchRes.data) {
      setProducts(searchRes.data.results);
      setTotalProducts(searchRes.data.count);
    } else {
      console.error('Product browser search failed:', searchRes.message);
      setProducts([]);
      setTotalProducts(0);
    }

    setStoreCounts(!countsRes.error && Array.isArray(countsRes.data) ? countsRes.data : []);
  }, [buildBody, page]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const handleSearchChange = useCallback((field) => (event) => {
    setSearchTerms(prev => ({ ...prev, [field]: event.target.value }));
    setPage(1);
    setIsSearching(true);
  }, []);

  const handleSourceNameSearch = useCallback((selectedSource) => {
    setSearchTerms(prev => ({ ...prev, sourceName: selectedSource === '-1' ? '' : selectedSource }));
    setPage(1);
    setIsSearching(true);
  }, []);

  const handleSortChange = useCallback((field) => {
    setSortState(prev => {
      const newOrder = prev.field === field && prev.order === 'asc' ? 'desc' : 'asc';
      return { field, order: newOrder };
    });
    setPage(1);
  }, []);

  const handleReset = useCallback(() => {
    setSearchTerms({ id: '', external_id: '', sourceName: '', siteName: '' });
    setPage(1);
    setIsSearching(false);
    setSortState({ field: null, order: 'asc' });
  }, []);

  const currentQueryBody = buildProductBrowserBody(searchTerms);

  return (
    <div style={{ width: '80vw', margin: '0 auto' }}>
      <Typography variant="h4" style={{ padding: '10px' }}>Product Browser</Typography>
      <Typography variant="body1" style={{ padding: '10px', width: '80vw', margin: '0 auto' }}>
        Search for products by ID, external ID (e.g. FLIP product ID), data source or product name. Use the form below to search for products. Note that you can also search by more than one search term at once.
        <ul>
          <li>Product name search supports partial matching (e.g. "cone" will also match "cones", and "School" will match "SchoolSafe").</li>
        </ul>
      </Typography>
      <Divider variant="middle" />

      <SearchForm
        searchTerms={searchTerms}
        handleSearchChange={handleSearchChange}
        handleSourceNameSearch={handleSourceNameSearch}
        handleReset={handleReset}
        queryBody={currentQueryBody}
        totalProducts={totalProducts}
      />

      <StoreCards storeCounts={storeCounts} />

      {isSearching && (
        <SearchResults totalProducts={totalProducts} />
      )}

      <ProductTable products={products} sortField={sortState.field} sortOrder={sortState.order} onSortChange={handleSortChange} />

      <Pagination
        count={Math.ceil(totalProducts / ROWS_PER_PAGE)}
        page={page}
        onChange={(_, newPage) => setPage(newPage)}
        siblingCount={1}
      />
    </div>
  );
};

const SearchForm = React.memo(({ searchTerms, handleSearchChange, handleSourceNameSearch, handleReset, queryBody, totalProducts}) => (
  <div>
    <div style={{ display: 'flex', justifyContent: 'space-evenly', margin: '20px 20px', alignItems: 'center' }}>
      <SearchField label="Search ID" value={searchTerms.id} onChange={handleSearchChange('id')} />
      <SearchField label="External ID" value={searchTerms.external_id} onChange={handleSearchChange('external_id')} />
      <SourceSelector
        value={searchTerms.sourceName}
        onSelect={handleSourceNameSearch}
        showTitle={false}
        label="Search by Data Source"
      />
    </div>
    <div style={{ display: 'flex', justifyContent: 'space-evenly', margin: '10px 20px' }}>
      <SearchField label="Search by Product Name" value={searchTerms.siteName} onChange={handleSearchChange('siteName')} style={{ maxWidth: '480px' }} />
      <div style={{ display: 'flex', gap: '10px' }}>
        <ResetButton variant="contained" onClick={handleReset}>Reset Search</ResetButton>
        <DownloadResultButton queryBody={queryBody} totalProducts={totalProducts} fileNamePrefix="product_browser" />
      </div>
    </div>
  </div>
));

const SearchField = React.memo(({ label, value, onChange, style = {} }) => (
  <Paper component="form" className="search-form" style={{ flex: 1, marginRight: '5px', maxWidth: '300px', boxShadow: 'none', ...style }} onSubmit={(e) => e.preventDefault()}>
    <TextField
      label={label}
      variant="outlined"
      value={value}
      onChange={onChange}
      fullWidth
    />
  </Paper>
));

const StoreCards = React.memo(({ storeCounts }) => (
  <div>
    <Divider style={{ marginTop: '20px', color: '#424242', marginBottom: '15px' }}>
      Products per store:
    </Divider>
    <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-evenly', maxWidth: '880px', margin: '0 auto' }}>
      {storeCounts.map((row) => (
        <Card key={row.store ?? 'unknown'} style={{ flex: '1 0 calc(25% - 10px)', maxWidth: '180px', boxSizing: 'border-box', textAlign: 'center', marginBottom: '10px' }}>
          <CardContent>
            <Typography variant="h6" component="h2" style={{ fontSize: '14px' }}>
              {row.store ?? '—'}
            </Typography>
            <Typography color="textSecondary">
              {row.count.toLocaleString()}
            </Typography>
          </CardContent>
        </Card>
      ))}
    </div>
  </div>
));

const SearchResults = React.memo(({ totalProducts }) => (
  <div>
    <Divider style={{ marginTop: '20px', color: '#424242', marginBottom: '15px' }}>
      Based on your search, there is a total of {totalProducts.toLocaleString()} products.
    </Divider>
  </div>
));

const BROWSER_COLUMNS = [
  { header: 'Assigned Flaime ID', field: 'id' },
  { header: 'External ID', field: 'external_id' },
  { header: 'Store Name', field: 'store' },
  { header: 'Data Source', field: 'source' },
  { header: 'Product Name', field: 'name' },
  { header: 'Category Name', field: null },
];

const ProductTable = React.memo(({ products, sortField, sortOrder, onSortChange }) => (
  <TableContainer style={{ width: '80vw', margin: '0 auto' }}>
    <Table>
      <TableHead>
        <TableRow>
          {BROWSER_COLUMNS.map(({ header, field }) => (
            <TableCell key={header} style={{ fontWeight: 'bold', textAlign: 'center', letterSpacing: '1px' }}>
              {field && onSortChange ? (
                <TableSortLabel
                  active={sortField === field}
                  direction={sortField === field ? sortOrder : 'asc'}
                  onClick={() => onSortChange(field)}
                >
                  {header}
                </TableSortLabel>
              ) : header}
            </TableCell>
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {products.map((product, index) => (
          <TableRow key={product.id} style={{ background: index % 2 === 0 ? '#f2f2f2' : 'white' }}>
            <TableCell style={{ width: '80px', textAlign: 'center' }}>
              <Link to={`/tools/product-browser/${product.id}`} target="_blank">{product.id}</Link>
            </TableCell>
            <TableCell style={{ textAlign: 'center' }}>{product.external_id}</TableCell>
            <TableCell style={{ textAlign: 'center' }}>{product.store?.name ?? '—'}</TableCell>
            <TableCell style={{ width: '140px', textAlign: 'center' }}>{product.source?.name ?? '—'}</TableCell>
            <TableCell style={{ width: '375px' }}>{product.site_name}</TableCell>
            <TableCell style={{ textAlign: 'left' }}>
              {product.categories && product.categories.length > 0
                ? [...product.categories]
                    .sort((a, b) => a.level - b.level)
                    .map(cat => cat.name)
                    .join(' > ')
                : 'No category'}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </TableContainer>
));
export default ProductBrowser;
