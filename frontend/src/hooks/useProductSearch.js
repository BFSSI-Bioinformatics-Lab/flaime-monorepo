import { useState, useCallback } from 'react';
import { SearchStoreProducts } from '../api/services/StoreProductSearchService';

/**
 * Runs POST /api/storeproducts/search/ and exposes the paginated result.
 *
 * Replaces the former useElasticsearch hook: same return shape
 * ({ results, isLoading, totalProducts, setResults, setTotalProducts, executeSearch })
 * so the calling pages barely change.
 *
 * executeSearch(body, page, rowsPerPage, processResults?, sort?)
 *   - body: { text, filters } from the util.js builders, or null to no-op
 *   - page: zero-based (MUI TablePagination); converted to the API's 1-based `page`
 *   - processResults: optional (rows) => rows transform applied before setState
 *   - sort: { field, order } | null
 */
const useProductSearch = () => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [totalProducts, setTotalProducts] = useState(0);

  const executeSearch = useCallback(async (body, page, rowsPerPage, processResults = null, sort = null) => {
    if (!body) return;

    setIsLoading(true);

    const payload = {
      ...body,
      page: page + 1,
      page_size: rowsPerPage,
      ...(sort ? { sort } : {}),
    };

    const { error, data, message } = await SearchStoreProducts(payload);

    if (!error && data) {
      const rows = processResults ? processResults(data.results) : data.results;
      setResults(rows);
      setTotalProducts(data.count);
    } else {
      console.error('Product search failed:', message);
      setResults([]);
      setTotalProducts(0);
    }

    setIsLoading(false);
  }, []);

  return { results, isLoading, totalProducts, setResults, setTotalProducts, executeSearch };
};

export default useProductSearch;
