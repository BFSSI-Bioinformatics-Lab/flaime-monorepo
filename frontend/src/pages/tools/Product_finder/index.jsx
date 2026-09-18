import React, { useState, useEffect, useCallback, useRef } from 'react';
import dayjs from 'dayjs';
import { Button, FormControl, FormControlLabel, Radio, RadioGroup, Typography, Divider } from '@mui/material';
import PageContainer from '../../../components/page/PageContainer';
import TextFileInput from '../../../components/inputs/TextFileInput';
import StoreSelector from '../../../components/inputs/StoreSelector';
import SourceSelector from '../../../components/inputs/SourceSelector';
import RegionSelector from '../../../components/inputs/RegionSelector';
import SingleDatePicker from '../../../components/inputs/SingleDatePicker';
import { useSearchFilters, buildProductFinderBody, SORT_FIELD_MAP } from '../util';
import { ResetButton } from '../../../components/buttons/ResetButton';
import { DownloadResultButton } from '../../../components/buttons/DownloadResultButton';
import ColumnSelection  from '../../../components/table/ColumnSelection';
import ToolTable  from '../../../components/table/ToolTable';
import SearchResultSummary from '../../../components/misc/SearchResultSummary';
import useProductSearch from '../../../hooks/useProductSearch';
import usePagination from '../../../hooks/usePagination';
import useColumnSelection from '../../../hooks/useColumnSelection';


const INITIAL_COLUMNS_VISIBILITY = {
  id: true,
  name: true,
  price: true,
  source: true,
  store: true,
  date: true,
  region: true,
  categories: true,
};

const ProductFinder = () => {

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const initialFilters = {
    TextEntries: { value: [] },
    Source: { value: null },
    Store: { value: null },
    Region: { value: null },
    StartDate: { value: null },
    EndDate: { value: null }
  };

  const [inputMode, setInputMode] = useState('Name');
  const [searchInputs, handleInputChange] = useSearchFilters(initialFilters);
  const [inputError, setInputError] = useState(false);

  const { results: searchResults, isLoading: searchResultsIsLoading, totalProducts, setResults: setSearchResults, setTotalProducts, executeSearch } = useProductSearch();
  const { columnsVisibility, selectedColumns, setSelectedColumns, handleColumnSelection } = useColumnSelection(INITIAL_COLUMNS_VISIBILITY);

  const [sortState, setSortState] = useState({ field: null, order: 'asc' });
  const sortRef = useRef({ field: null, order: 'asc' });

  const buildQueryObject = useCallback(() => {
    return buildProductFinderBody(searchInputs, inputMode);
  }, [searchInputs, inputMode]);

  const search = useCallback(async (page, rowsPerPage) => {
    const cleanTextEntries = [...new Set(
      searchInputs.TextEntries.value.map(line => line.trim()).filter(line => line !== "")
    )];

    if (cleanTextEntries.length === 0) {
      setInputError(true);
      return;
    }
    if (cleanTextEntries.length > 1000) return;

    setInputError(false);
    const { field, order } = sortRef.current;
    const sort = field ? { field: SORT_FIELD_MAP[field], order } : null;
    await executeSearch(buildQueryObject(), page, rowsPerPage, null, sort);
  }, [buildQueryObject, executeSearch, searchInputs.TextEntries.value]);

  const { page, setPage, rowsPerPage, setRowsPerPage, handlePageChange, handleRowsPerPageChange } = usePagination(search);

  const handleReset = () => {
    handleInputChange('TextEntries', { value: [] });
    handleInputChange('Source', { value: null });
    handleInputChange('Store', { value: null });
    handleInputChange('Region', { value: null });
    handleInputChange('StartDate', { value: '1900-01-01' });
    handleInputChange('EndDate', { value: dayjs().format('YYYY-MM-DD') });
    setSearchResults([]);
    setTotalProducts(0);
    setInputMode('Name');
    setPage(0);
    setRowsPerPage(25);
    const resetSort = { field: null, order: 'asc' };
    sortRef.current = resetSort;
    setSortState(resetSort);
  };

  const handleSortChange = (column) => {
    const newOrder = sortState.field === column && sortState.order === 'asc' ? 'desc' : 'asc';
    const newSort = { field: column, order: newOrder };
    sortRef.current = newSort;
    setSortState(newSort);
    setPage(0);
    search(0, rowsPerPage);
  };

  const handleInputModeChange = (event) => {
    setInputMode(event.target.value);
  };

  const handleTextChange = (text) => {
    if (inputError) setInputError(false);
    handleInputChange('TextEntries', { value: text.split("\n") });
  };

  const handleSourceChange = (selectedSource) => {
    handleInputChange('Source', { value: selectedSource === '-1' ? null : selectedSource });
  };

  const handleRegionChange = (selectedRegion) => {
    handleInputChange('Region', { value: selectedRegion === '-1' ? null : selectedRegion });
  };

  const handleStoreChange = (selectedStore) => {
    handleInputChange('Store', { value: selectedStore === '-1' ? null : selectedStore });
  };

  const handleStartDateChange = (date) => {
    handleInputChange('StartDate', { value: date });
  };
  const handleEndDateChange = (date) => {
    handleInputChange('EndDate', { value: date });
  };

  const currentQueryBody = buildQueryObject();

return (
  <PageContainer>
    <div>
      <Typography variant="h4" style={{ padding: '10px' }}>Product Finder</Typography>
      <Typography variant="body1" style={{ padding: '10px', width: '80vw', margin: '0 auto' }}>
        Here you can enter a list of product names or FLAIME IDs to search for. <br/> You can also further filter by source, region, and store.
      </Typography>
      <Divider style={{ width: '60vw', margin: '15px auto 15px auto' }}/>
      <FormControl style={{ margin: '0 25%' }}>
        <RadioGroup row value={inputMode} onChange={handleInputModeChange} name="inputMode">
          <FormControlLabel value="Name" control={<Radio />} label="Product Names" />
          <FormControlLabel value="ID" control={<Radio />} label="FLAIME ID" />
          <FormControlLabel value="UPC" control={<Radio />} label="UPC" />
          <FormControlLabel value="Nielsen_UPC" control={<Radio />} label="Nielsen UPC" />
        </RadioGroup>
      </FormControl>
      <Divider style={{ width: '60vw', margin: '15px auto 5px auto' }}/>

      <div style={{ width: '75vw', margin: '10px auto'}}>
        <Typography variant="h5">Enter product names (or IDs) or upload a file</Typography>
        {(() => {
            const validItemCount = searchInputs.TextEntries.value.filter(line => line.trim() !== "").length;

            return (
              <>
                <TextFileInput
                  text={searchInputs.TextEntries.value.join("\n")}
                  onTextChange={handleTextChange}
                  error={validItemCount > 1000}
                />

                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', marginTop: '5px' }}>
                    {validItemCount > 1000 && (
                        <Typography variant="caption" color="error" style={{ fontWeight: 'bold', fontSize: '14px' }}>
                            Maximum 1000 entries allowed. Please reduce your input.
                        </Typography>
                    )}

                    <Typography
                        variant="caption"
                        style={{
                            color: validItemCount > 1000 ? '#d32f2f' : 'gray',
                            fontWeight: validItemCount > 1000 ? 'bold' : 'normal'
                        }}
                    >
                        Current count: {validItemCount} / 1000
                    </Typography>
                </div>
              </>
            );
        })()}
      </div>
      <Divider style={{ width: '60vw', margin: '15px auto 5px auto' }}/>
      <div style={{ display: 'flex', justifyContent: 'space-around', paddingBottom: '25px' }}>
        <SourceSelector
          value={searchInputs.Source.value}
          onSelect={handleSourceChange}
          showTitle={true}
          label="Select a source"
        />
        <RegionSelector
          value={searchInputs.Region.value}
          onSelect={handleRegionChange}
        />
        <StoreSelector
          value={searchInputs.Store.value}
          onSelect={handleStoreChange}
        />
      </div>
      <Typography variant="h5">Select a date range</Typography>
      <div style={{ display: 'flex', justifyContent: 'space-around', margin: '15px 0', width: '45vw' }}>
        <SingleDatePicker
            label="Start Date"
            initialDate="1900-01-01"
            onChange={handleStartDateChange}
        />
        <SingleDatePicker
            label="End Date"
            initialDate={dayjs().format('YYYY-MM-DD')}
            onChange={handleEndDateChange}
        />
      </div>
      {inputError && (
        <Typography
          color="error"
          variant="body2"
          style={{ marginTop: '20px', fontWeight: 'bold' }}
        >
          Please enter at least one product name or ID.
        </Typography>
      )}
      <div style={{ marginTop: '10px', display: 'flex', gap: '10px'}}>
        <Button variant="contained" onClick={() => { setPage(0); search(0, rowsPerPage); }}>
          Search
        </Button>
        <ResetButton variant="contained" onClick={handleReset}>Reset Search</ResetButton>
        <DownloadResultButton
          queryBody={currentQueryBody}
          totalProducts={totalProducts}
          fileNamePrefix="product_finder"
        />
      </div>
      <SearchResultSummary totalProducts={totalProducts} />
      <>
        <ColumnSelection
          selectedColumns={selectedColumns}
          setSelectedColumns={setSelectedColumns}
          columnsVisibility={columnsVisibility}
          handleColumnSelection={handleColumnSelection}
        />
        {searchResultsIsLoading ? (
          <p>Loading...</p>
        ) : (
          <>
            <ToolTable
              columns={selectedColumns}
              data={searchResults}
              totalCount={totalProducts}
              page={page}
              rowsPerPage={rowsPerPage}
              onPageChange={handlePageChange}
              onRowsPerPageChange={handleRowsPerPageChange}
              sortField={sortState.field}
              sortOrder={sortState.order}
              onSortChange={handleSortChange}
            />
          </>
        )}
      </>
      </div>
    </PageContainer>
  );
};

export default ProductFinder;
