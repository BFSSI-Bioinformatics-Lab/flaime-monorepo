import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
    Typography, Divider, Button, Table, TableBody, TableCell,
    TableHead, TableRow, Paper, Grid, Card, CardContent,
    CircularProgress, Alert, TextField
} from '@mui/material';
import PageContainer from '../../../components/page/PageContainer';
import SourceSelector from '../../../components/inputs/SourceSelector';
import { GetCollectionStats, SearchStoreProducts } from '../../../api/services/StoreProductSearchService';

const CollectionStats = () => {
    const [sourceId, setSourceId] = useState(null);
    const [stats, setStats] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const [selectedIngredient, setSelectedIngredient] = useState(null);
    const [ingredientProducts, setIngredientProducts] = useState([]);
    const [ingredientProductsLoading, setIngredientProductsLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    const handleSourceChange = (value) => {
        setSourceId(value === '-1' ? null : value);
        setStats(null);
        setError('');
        setSelectedIngredient(null);
        setIngredientProducts([]);
    };

    const fetchIngredientProducts = useCallback(async (term) => {
        setSelectedIngredient(term);
        setIngredientProducts([]);
        setIngredientProductsLoading(true);

        const filters = { ingredients: { terms: [term], mode: 'any' } };
        if (sourceId) filters.source = sourceId;

        const { error: err, data } = await SearchStoreProducts({
            text: {},
            filters,
            page: 1,
            page_size: 50,
        });

        setIngredientProducts(!err && data ? data.results : []);
        setIngredientProductsLoading(false);
    }, [sourceId]);

    const handleIngredientClick = useCallback((term) => {
        if (selectedIngredient === term) {
            setSelectedIngredient(null);
            setIngredientProducts([]);
        } else {
            fetchIngredientProducts(term);
        }
    }, [selectedIngredient, fetchIngredientProducts]);

    const handleSearch = useCallback(() => {
        const term = searchTerm.trim();
        if (term) fetchIngredientProducts(term);
    }, [searchTerm, fetchIngredientProducts]);

    const handleLoadStats = useCallback(async () => {
        setIsLoading(true);
        setError('');
        setStats(null);

        const { error: err, data, message } = await GetCollectionStats(sourceId);

        if (!err && data) {
            setStats(data);
        } else {
            setError(message || 'Error loading statistics.');
        }

        setIsLoading(false);
    }, [sourceId]);

    useEffect(() => {
        handleLoadStats();
    }, [handleLoadStats]);

    const fmt = (val, decimals = 2) =>
        val != null && isFinite(val) ? val.toFixed(decimals) : '—';

    const total       = stats?.total ?? 0;
    const reviewed    = stats?.manually_reviewed ?? 0;
    const notReviewed = total - reviewed;
    const hasResults  = stats && !isLoading;

    return (
        <PageContainer>
            <Typography variant="h4" style={{ padding: '10px' }}>Collection Statistics</Typography>
            <Typography variant="body1" style={{ padding: '10px', width: '80vw', margin: '0 auto' }}>
                Select a collection (source) to view summary statistics for its products, or load statistics across every collection.
                Statistics are currently broken down by collection; breakdown by reference amount (RA) category will be added in a future update.
            </Typography>

            <Divider style={{ width: '60vw', margin: '15px auto' }} />

            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', padding: '10px', justifyContent: 'center' }}>
                <SourceSelector
                    value={sourceId}
                    onSelect={handleSourceChange}
                    showTitle={false}
                    label="Select a collection"
                />
                <Button variant="contained" onClick={handleLoadStats} disabled={isLoading}>
                    Load Statistics
                </Button>
            </div>

            {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

            {isLoading && (
                <div style={{ textAlign: 'center', padding: '40px' }}>
                    <CircularProgress />
                </div>
            )}

            {hasResults && (
                <>
                    {/* ── Basic Stats & QC ─────────────────────────────────── */}
                    <Typography variant="h5" style={{ padding: '20px 10px 10px' }}>
                        Basic Stats &amp; QC
                    </Typography>

                    <Grid container spacing={3} style={{ padding: '0 10px 20px' }}>
                        <Grid item xs={12} sm={4}>
                            <Card variant="outlined">
                                <CardContent>
                                    <Typography variant="subtitle1" color="text.secondary">
                                        Total Products
                                    </Typography>
                                    <Typography variant="h3">{total.toLocaleString()}</Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <Card variant="outlined">
                                <CardContent>
                                    <Typography variant="subtitle1" color="text.secondary">
                                        Manually Reviewed
                                    </Typography>
                                    <Typography variant="h3">{reviewed.toLocaleString()}</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {stats.reviewed_percentage}% of total
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <Card variant="outlined">
                                <CardContent>
                                    <Typography variant="subtitle1" color="text.secondary">
                                        Not Yet Reviewed
                                    </Typography>
                                    <Typography variant="h3">{notReviewed.toLocaleString()}</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {(100 - stats.reviewed_percentage).toFixed(2)}% of total
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>

                    <Divider style={{ margin: '10px 0 20px' }} />

                    {/* ── Nutrients of Concern ─────────────────────────────── */}
                    <Typography variant="h5" style={{ padding: '10px' }}>
                        Nutrients of Concern
                    </Typography>
                    <Typography variant="body2" color="text.secondary" style={{ padding: '0 10px 10px' }}>
                        Amounts per serving as recorded on the product label.
                        "Products with Data" reflects how many products have a recorded value for that nutrient.
                    </Typography>

                    <Paper variant="outlined" style={{ margin: '10px', overflowX: 'auto' }}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell><b>Nutrient</b></TableCell>
                                    <TableCell align="right"><b>Products with Data</b></TableCell>
                                    <TableCell align="right"><b>Mean</b></TableCell>
                                    <TableCell align="right"><b>Median</b></TableCell>
                                    <TableCell align="right"><b>Min</b></TableCell>
                                    <TableCell align="right"><b>Max</b></TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {(stats.nutrients || []).map(({ label, unit, count, mean, median, min, max }) => (
                                    <TableRow key={label}>
                                        <TableCell>{label}</TableCell>
                                        <TableCell align="right">{count ? count.toLocaleString() : '—'}</TableCell>
                                        <TableCell align="right">{count ? `${fmt(mean)} ${unit}` : '—'}</TableCell>
                                        <TableCell align="right">{count ? `${fmt(median)} ${unit}` : '—'}</TableCell>
                                        <TableCell align="right">{count ? `${fmt(min)} ${unit}` : '—'}</TableCell>
                                        <TableCell align="right">{count ? `${fmt(max)} ${unit}` : '—'}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </Paper>

                    <Divider style={{ margin: '20px 0' }} />

                    {/* ── Front-of-Pack ────────────────────────────────────── */}
                    <Typography variant="h5" style={{ padding: '10px' }}>
                        Front-of-Pack (FOP) Symbol
                    </Typography>

                    <Grid container spacing={3} style={{ padding: '0 10px 20px' }}>
                        <Grid item xs={12} sm={4}>
                            <Card variant="outlined">
                                <CardContent>
                                    <Typography variant="subtitle1" color="text.secondary">
                                        Products with FOP Symbol
                                    </Typography>
                                    <Typography variant="h3">{stats.with_fop.toLocaleString()}</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {stats.fop_percentage}% of total
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <Card variant="outlined">
                                <CardContent>
                                    <Typography variant="subtitle1" color="text.secondary">
                                        Products without FOP Symbol
                                    </Typography>
                                    <Typography variant="h3">{(total - stats.with_fop).toLocaleString()}</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {(100 - stats.fop_percentage).toFixed(2)}% of total
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>

                    <Divider style={{ margin: '20px 0' }} />

                    {/* ── Ingredient Prevalence ─────────────────────────────── */}
                    <Typography variant="h5" style={{ padding: '10px' }}>
                        Ingredient Prevalence &amp; Additives
                    </Typography>
                    <Typography variant="body2" color="text.secondary" style={{ padding: '0 10px 10px' }}>
                        Additives with research associating them with negative health outcomes.
                        Counts reflect products whose English ingredient list contains the additive name.
                    </Typography>
                    <Paper variant="outlined" style={{ margin: '10px', overflowX: 'auto' }}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell><b>Additive</b></TableCell>
                                    <TableCell align="right"><b>Products Containing</b></TableCell>
                                    <TableCell align="right"><b>% of Total</b></TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {(stats.additives || []).map(({ label, term, count, percentage }) => {
                                    const isSelected = selectedIngredient === term;
                                    return (
                                        <TableRow
                                            key={term}
                                            hover
                                            selected={isSelected}
                                            onClick={() => handleIngredientClick(term)}
                                            style={{ cursor: 'pointer' }}
                                        >
                                            <TableCell>{label}</TableCell>
                                            <TableCell align="right">{count != null ? count.toLocaleString() : '—'}</TableCell>
                                            <TableCell align="right">{percentage != null ? `${percentage}%` : '—'}</TableCell>
                                        </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </Paper>

                    <div style={{ display: 'flex', gap: '10px', padding: '10px 10px 0', alignItems: 'center' }}>
                        <TextField
                            size="small"
                            label="Search any ingredient"
                            value={searchTerm}
                            onChange={e => setSearchTerm(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleSearch()}
                            style={{ width: '300px' }}
                        />
                        <Button variant="outlined" onClick={handleSearch} disabled={!searchTerm.trim()}>
                            Search
                        </Button>
                    </div>

                    {selectedIngredient && (
                        <>
                            <Typography variant="h6" style={{ padding: '10px 10px 4px' }}>
                                Products containing "{selectedIngredient}"
                                {!ingredientProductsLoading && ` (showing up to 50)`}
                            </Typography>
                            {ingredientProductsLoading ? (
                                <div style={{ textAlign: 'center', padding: '20px' }}>
                                    <CircularProgress size={24} />
                                </div>
                            ) : (
                                <Paper variant="outlined" style={{ margin: '10px', overflowX: 'auto' }}>
                                    <Table size="small">
                                        <TableHead>
                                            <TableRow>
                                                <TableCell><b>Product</b></TableCell>
                                                <TableCell><b>Store</b></TableCell>
                                                <TableCell><b>Collection</b></TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {ingredientProducts.length === 0 ? (
                                                <TableRow>
                                                    <TableCell colSpan={3} align="center">No products found.</TableCell>
                                                </TableRow>
                                            ) : ingredientProducts.map(p => (
                                                <TableRow key={p.id} hover>
                                                    <TableCell>
                                                        <Link to={`/tools/product-browser/${p.id}`} target="_blank">
                                                            {p.site_name}
                                                        </Link>
                                                    </TableCell>
                                                    <TableCell>{p.store?.name ?? '—'}</TableCell>
                                                    <TableCell>{p.source?.name ?? '—'}</TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </Paper>
                            )}
                        </>
                    )}
                </>
            )}
        </PageContainer>
    );
};

export default CollectionStats;
