import React, { useState, useEffect, useCallback, useRef } from 'react';
import dayjs from 'dayjs';
import { TextField, Button, Alert, Typography, Divider, Grid, Select, MenuItem, FormControl, InputLabel, ToggleButton, ToggleButtonGroup} from '@mui/material';
import PageContainer from '../../../components/page/PageContainer';
import SingleDatePicker from '../../../components/inputs/SingleDatePicker';
import CategorySelector from '../../../components/inputs/CategorySelector';
import NutritionFilter from '../../../components/inputs/NutritionFilter';
import { useSearchFilters, buildAdvancedSearchBody, SORT_FIELD_MAP } from '../util';
import ColumnSelection  from '../../../components/table/ColumnSelection';
import ToolTable  from '../../../components/table/ToolTable';
import SearchResultSummary from '../../../components/misc/SearchResultSummary';
import { ResetButton } from '../../../components/buttons/ResetButton';
import { DownloadResultButton } from '../../../components/buttons/DownloadResultButton';
import useSearchOptions from '../../../hooks/useSearchOptions';
import useProductSearch from '../../../hooks/useProductSearch';
import usePagination from '../../../hooks/usePagination';
import useColumnSelection from '../../../hooks/useColumnSelection';

const COLUMN_ORDER = [
    'id',
    'external_id',
    'name',
    'price',
    'source',
    'store',
    'date',
    'region',
    'categories',
    'storage_condition',
    'primary_package_material',
    'allergens_warnings'
];

const INITIAL_COLUMNS_VISIBILITY = {
    id: true,
    external_id: true,
    name: true,
    price: true,
    source: true,
    store: true,
    date: true,
    region: true,
    categories: true,
    storage_condition: true,
    primary_package_material: true,
    allergens_warnings: true,
};

// Flatten the nested allergen array into a single "; "-joined string so the
// `allergens_warnings` table column can render it directly.
const processAllergenRows = (rows) => rows.map(row => {
    const validTexts = Array.isArray(row.allergens_warnings)
        ? row.allergens_warnings
            .flatMap(w => [w.contains_en, w.may_contain_en])
            .filter(Boolean)
        : [];

    return { ...row, allergens_warnings: [...new Set(validTexts)].join("; ") };
});

const AdvancedSearch = () => {
    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    const initialFilters = {
        Names: '',
        IDs: '',
        ExternalIDs: '',
        UPCs: '',
        NielsenUPCs: '',
        Storage: '',
        Packaging: '',
        Allergens: '',
        Ingredients: '',
        IngredientsMatch: 'all',
        Categories: { value: [] },
        Source: { value: null },
        Store: { value: null },
        Region: { value: null },
        StartDate: { value: null },
        EndDate: { value: null },
        Nutrition: { nutrient: '', minAmount: '', maxAmount: '' },
    };

    const { storageOptions, packagingOptions, sourceOptions, storeOptions, regionOptions } = useSearchOptions();
    const [searchInputs, handleInputChange] = useSearchFilters(initialFilters);
    const [errorMessage, setErrorMessage] = useState('');
    const [resetKey, setResetKey] = useState(0);

    const { results: searchResults, isLoading, totalProducts, setResults: setSearchResults, setTotalProducts, executeSearch } = useProductSearch();
    const { columnsVisibility, selectedColumns, setSelectedColumns, handleColumnSelection } = useColumnSelection(INITIAL_COLUMNS_VISIBILITY, COLUMN_ORDER);

    const [sortState, setSortState] = useState({ field: null, order: 'asc' });
    const sortRef = useRef({ field: null, order: 'asc' });

    const buildQueryObject = useCallback(() => {
        return buildAdvancedSearchBody(searchInputs);
    }, [searchInputs]);

    const search = useCallback((page, rowsPerPage) => {
        const { field, order } = sortRef.current;
        const sort = field ? { field: SORT_FIELD_MAP[field], order } : null;
        executeSearch(buildQueryObject(), page, rowsPerPage, processAllergenRows, sort);
    }, [buildQueryObject, executeSearch]);

    const { page, setPage, rowsPerPage, setRowsPerPage, handlePageChange, handleRowsPerPageChange } = usePagination(search);

    const handleReset = () => {
        Object.keys(initialFilters).forEach(key => {
            handleInputChange(key, initialFilters[key]);
        });

        setSearchResults([]);
        setTotalProducts(0);
        setErrorMessage('');
        setPage(0);
        setRowsPerPage(25);
        setResetKey(prev => prev + 1);
        setSelectedColumns(Object.keys(columnsVisibility));
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

    const handleTextFieldChange = (field) => (event) => {
        handleInputChange(field, event.target.value);
        if (errorMessage) setErrorMessage('');
    };

    const handleSelectChange = (field) => (event) => {
        handleInputChange(field, event.target.value);
    };

    const handleSelectorChange = (field) => (value) => {
        handleInputChange(field, { value: value === '-1' ? null : value });
    };

    const handleCategoryChange = (field) => (value) => {
        handleInputChange(field, { value });
    };

    const handleNutritionChange = (nutrition) => {
        handleInputChange('Nutrition', nutrition);
    };

    const currentQueryBody = buildQueryObject();

    return (
        <PageContainer>
            <div>
                {errorMessage && <Alert severity="error">{errorMessage}</Alert>}
                <Typography variant="h4" style={{ padding: '10px' }}>Advanced Search</Typography>
                <Typography variant="body1" style={{ padding: '10px', width: '80vw', margin: '0 auto' }}>
                Enter search terms in any or all of the fields. Note that some fields are only relevant for certain datasets; e.g. Region is only relevant for Web Scrape data, and Store is not recorded for Nielsen data.
                </Typography>
                <Divider style={{ width: '60vw', margin: '15px auto 5px auto' }}/>
                <Typography variant="h5" style={{ padding: '10px' }}>Product Info</Typography>

                <div style={{ display: 'flex', justifyContent: 'space-around', paddingBottom: '15px' }}>
                    <div style={{ maxWidth: '320px', minWidth: '280px' }}>
                        <TextField
                            label="Product Name"
                            value={searchInputs.Names}
                            onChange={handleTextFieldChange('Names')}
                            variant="outlined"
                            InputProps={{ style: { minWidth: '280px', overflow: 'hidden' } }}
                        />
                    </div>
                    <div>
                        <TextField
                            label="Product ID"
                            value={searchInputs.IDs}
                            onChange={handleTextFieldChange('IDs')}
                            variant="outlined"
                        />
                    </div>
                    <div>
                        <TextField
                            label="External ID"
                            value={searchInputs.ExternalIDs}
                            onChange={handleTextFieldChange('ExternalIDs')}
                            variant="outlined"
                        />
                    </div>
                    <div>
                        <TextField
                            label="UPC"
                            value={searchInputs.UPCs}
                            onChange={handleTextFieldChange('UPCs')}
                            variant="outlined"
                        />
                    </div>
                    <div>
                        <TextField
                            label="Nielsen UPC"
                            value={searchInputs.NielsenUPCs}
                            onChange={handleTextFieldChange('NielsenUPCs')}
                            variant="outlined"
                        />
                    </div>
                </div>

                <Divider style={{ width: '60vw', margin: '10px auto' }}/>

               <Typography variant="h5" style={{ padding: '10px' }}>Attributes & Location</Typography>
               <div style={{ display: 'flex', justifyContent: 'space-around', paddingBottom: '25px', marginTop: '20px' }}>
                    <div style={{ width: '30%', minWidth: '280px', maxWidth: '320px' }}>
                        <FormControl variant="outlined" fullWidth>
                            <InputLabel>Select a source</InputLabel>
                            <Select
                                value={searchInputs.Source.value || '-1'}
                                onChange={(e) => handleSelectorChange('Source')(e.target.value)}
                                label="Select a source"
                            >
                                <MenuItem value="-1">Use all sources</MenuItem>
                                {sourceOptions.map((option) => (
                                    <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </div>

                    <div style={{ width: '30%', minWidth: '280px', maxWidth: '320px' }}>
                        <FormControl variant="outlined" fullWidth>
                            <InputLabel>Select a Region</InputLabel>
                            <Select
                                value={searchInputs.Region.value || '-1'}
                                onChange={(e) => handleSelectorChange('Region')(e.target.value)}
                                label="Select a Region"
                            >
                                <MenuItem value="-1">Use all regions</MenuItem>
                                {regionOptions.map((option) => (
                                    <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </div>

                    <div style={{ width: '30%', minWidth: '280px', maxWidth: '320px' }}>
                         <FormControl variant="outlined" fullWidth>
                            <InputLabel>Select a Store</InputLabel>
                            <Select
                                value={searchInputs.Store.value || '-1'}
                                onChange={(e) => handleSelectorChange('Store')(e.target.value)}
                                label="Select a Store"
                            >
                                <MenuItem value="-1">Use all stores</MenuItem>
                                {storeOptions.map((option) => (
                                    <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </div>
               </div>
               {/* <Divider style={{ width: '60vw', margin: '10px auto' }}/>

               <Typography variant="h5" style={{ padding: '10px' }}>Physical Properties</Typography> */}

               <div style={{ display: 'flex', justifyContent: 'space-around', paddingBottom: '25px' }}>
                    <div style={{ width: '45%', minWidth: '280px' }}>
                        <FormControl variant="outlined" fullWidth>
                            <InputLabel>Storage Condition</InputLabel>
                            <Select
                                value={searchInputs.Storage || '-1'}
                                onChange={handleSelectChange('Storage')}
                                label="Storage Condition"
                            >
                                <MenuItem value="-1">Use all storage conditions</MenuItem>
                                {storageOptions.map((option) => (
                                    <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </div>

                    <div style={{ width: '45%', minWidth: '280px' }}>
                        <FormControl variant="outlined" fullWidth>
                            <InputLabel>Packaging Material</InputLabel>
                            <Select
                                value={searchInputs.Packaging || '-1'}
                                onChange={handleSelectChange('Packaging')}
                                label="Packaging Material"
                            >
                                <MenuItem value="-1">Use all packaging materials</MenuItem>
                                {packagingOptions.map((option) => (
                                    <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </div>
               </div>

               <div style={{ display: 'flex', justifyContent: 'space-around', paddingBottom: '25px' }}>
                    <div style={{ width: '45%', minWidth: '280px' }}>
                        <TextField
                            label="Allergens (Text Search)"
                            placeholder="e.g. Peanuts, Soy"
                            value={searchInputs.Allergens}
                            onChange={handleTextFieldChange('Allergens')}
                            variant="outlined"
                            fullWidth
                            helperText="Searches 'Contains' and 'May Contain'"
                        />
                    </div>

                    <div style={{ width: '45%', minWidth: '280px' }}>
                        <TextField
                            label="Ingredients (Text Search)"
                            placeholder="e.g. Sugar, Wheat Flour"
                            value={searchInputs.Ingredients}
                            onChange={handleTextFieldChange('Ingredients')}
                            variant="outlined"
                            fullWidth
                            helperText={
                                searchInputs.IngredientsMatch === 'any'
                                    ? "Matches products with any of the listed ingredients (English & French)"
                                    : "Matches products with all of the listed ingredients (English & French)"
                            }
                        />
                        <ToggleButtonGroup
                            value={searchInputs.IngredientsMatch}
                            exclusive
                            size="small"
                            onChange={(e, value) => { if (value) handleInputChange('IngredientsMatch', value); }}
                            aria-label="Ingredient match mode"
                            style={{ marginTop: '8px' }}
                        >
                            <ToggleButton value="all" aria-label="Match all ingredients">Match all</ToggleButton>
                            <ToggleButton value="any" aria-label="Match any ingredient">Match any</ToggleButton>
                        </ToggleButtonGroup>
                    </div>
               </div>

                <Grid container spacing={1} direction="row" justifyContent="space-between" >
                    <Grid item xs={12} md={6}>
                        <CategorySelector key={resetKey} onChange={handleCategoryChange('Categories')} />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Typography variant="h5" style={{ padding: '10px 20px 20px 20px' }}>Select a date range</Typography>
                        <div style={{ display: 'flex', justifyContent: 'space-around', padding: '15px 20px' }}>
                            <SingleDatePicker
                                key={`start-${resetKey}`}
                                label="Start Date"
                                initialDate="1900-01-01"
                                onChange={(date) => handleInputChange('StartDate', { value: date })}
                            />
                            <SingleDatePicker
                                key={`end-${resetKey}`}
                                label="End Date"
                                initialDate={dayjs().format('YYYY-MM-DD')}
                                onChange={(date) => handleInputChange('EndDate', { value: date })}
                            />
                        </div>
                        <Divider style={{ width: '300px', margin: '10px auto' }}/>
                        <div>
                            <NutritionFilter
                                value={searchInputs.Nutrition}
                                onChange={handleNutritionChange}
                            />
                        </div>
                    </Grid>
                </Grid>

                <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
                    <Button variant="contained" onClick={() => { setPage(0); search(0, rowsPerPage); }} disabled={isLoading}>
                        Search
                    </Button>
                    <ResetButton variant="contained" onClick={handleReset}>Reset Search</ResetButton>
                    <DownloadResultButton
                        queryBody={currentQueryBody}
                        totalProducts={totalProducts}
                        fileNamePrefix="advanced_search"
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
                    {isLoading ? (
                        <p>Loading...</p>
                    ) : (
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
                    )}
                </>
            </div>
        </PageContainer>
    );
};

export default AdvancedSearch;
