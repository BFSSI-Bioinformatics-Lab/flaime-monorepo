import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  GetCategoriesToVerify, 
  SubmitCategoryVerification,
  UpdateCategoryVerification,
  GetProblematicVerifications, 
  GetUserVerifications,
  GetAllUsers 
} from '../../../api/services/CategoryVerificationService';
import { GetAllCategories } from '../../../api/services/CategoryService';
import {
  Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper, Select, MenuItem, Checkbox, Button,
  Alert, Snackbar, CircularProgress, Typography,
  Box, TextField, Pagination
} from '@mui/material';


const flattenCategories = (categories) => {
    return categories.reduce((flat, cat) => {
      flat.push(cat);
      if (cat.children?.length) {
        flat.push(...flattenCategories(cat.children));
      }
      return flat;
    }, []);
};

const CategoryVerification = () => {
  const [products, setProducts] = useState([]);
  const [allCategories, setAllCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [verificationData, setVerificationData] = useState({});
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize] = useState(50);

  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');

  const [searchParams] = useSearchParams();
  const scheme = searchParams.get('scheme');
  const source = searchParams.get('source');
  const view = searchParams.get('view') || 'verify';
  const preselectedUserId = searchParams.get('user');
  const extraCategoryIds = (searchParams.get('extra_categories') || '')
    .split(',').filter(Boolean).map(Number);

  const isVerificationView = () => view === 'verify';
  const isProblematicView = () => view === 'problematic';

  const getPageTitle = () => {
    const titles = {
      'problematic': 'Review Problematic Verifications',
      'user-verifications': 'User Verification History',
      'default': 'Category Verification'
    };
    return titles[view] || titles.default;
  };

  const getPageDesc = () => {
    if (totalCount === 0) return 'No products to display';
    const start = (currentPage - 1) * pageSize + 1;
    const end = Math.min(currentPage * pageSize, totalCount);
    return `Showing ${start}-${end} of ${totalCount} products`;
  };

  const getApiCall = () => {
    if (view === 'problematic') {
      return GetProblematicVerifications(parseInt(scheme), parseInt(source), currentPage, pageSize);
    }
    if (view === 'user-verifications') {
      const userId = preselectedUserId || selectedUser;
      return GetUserVerifications(
        parseInt(scheme), parseInt(source),
        userId ? parseInt(userId) : null,
        currentPage, pageSize
      );
    }
    return GetCategoriesToVerify(parseInt(scheme), parseInt(source), currentPage, pageSize);
  };

  const initializeVerificationData = (products, view) => {
    return products.reduce((acc, product) => {
      if (!acc[product.id]) {
        let category, problematicFlag, notes, verificationId;
        if (view === 'user-verifications' || view === 'problematic') {
          category = product.category_id;
          problematicFlag = product.problematic_flag || false;
          notes = product.notes || '';
          verificationId = product.id;
        } else {
          const topPrediction = product.predictions.reduce((prev, current) =>
            prev.confidence > current.confidence ? prev : current
          );
          category = topPrediction.category_id;
          problematicFlag = false;
          notes = '';
          verificationId = null;
        }
        acc[product.id] = {
          product_id: product.product_id,
          category,
          problematic_flag: problematicFlag,
          notes,
          verification_id: verificationId,
          complete: false
        };
      }
      return acc;
    }, {});
  };

  useEffect(() => {
      const fetchCategories = async () => {
        try {
          const { categories } = await GetAllCategories();
          setAllCategories(categories || []);
        } catch (err) {
          console.error('Error fetching categories:', err);
        }
      };
      fetchCategories();
  }, []);

  const fetchUsers = async () => {
    try {
      const { error, users, message } = await GetAllUsers();
      if (error) console.error('Failed to fetch users:', message);
      else setUsers(users || []);
    } catch (err) {
      console.error('Error fetching users:', err);
    }
  };

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const result = await getApiCall();
      if (result.error) throw new Error(result.message);
      
      setProducts(result.products);
      setTotalCount(result.count);
      setTotalPages(Math.ceil(result.count / pageSize));
      setVerificationData(prev => ({
        ...prev,
        ...initializeVerificationData(result.products, view)
      }));
      setLoading(false);
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Failed to fetch products: ' + err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    if (scheme && source) {
      fetchProducts();
      if (view === 'user-verifications') {
        fetchUsers();
        if (preselectedUserId) setSelectedUser(preselectedUserId);
      }
    } else {
      setError('Missing required parameters: scheme and source');
      setLoading(false);
    }
  }, [scheme, source, view, selectedUser, preselectedUserId, currentPage]);

  const handlePageChange = (event, value) => {
    setCurrentPage(value);
    requestAnimationFrame(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  };

  const handleCategoryChange = (productId, categoryId) => {
    setVerificationData(prev => ({
      ...prev,
      [productId]: { ...prev[productId], category: parseInt(categoryId) }
    }));
  };

  const handleProblematicToggle = (productId) => {
    setVerificationData(prev => ({
      ...prev,
      [productId]: { ...prev[productId], problematic_flag: !prev[productId].problematic_flag }
    }));
  };

  const handleCompleteToggle = (productId) => {
    setVerificationData(prev => ({
      ...prev,
      [productId]: { ...prev[productId], complete: !prev[productId].complete }
    }));
  };

  const handleNotesChange = (productId, notes) => {
    setVerificationData(prev => ({
      ...prev,
      [productId]: { ...prev[productId], notes }
    }));
  };

  const handleSubmit = async () => {
    const isUpdateView = view === 'problematic' || view === 'user-verifications';
    const completedItems = Object.entries(verificationData).filter(([_, data]) => data.complete);

    if (completedItems.length === 0) {
      setError('Please mark at least one item as complete before submitting');
      return false;
    }

    try {
      if (isUpdateView) {
        const results = await Promise.all(
          completedItems.map(([_, data]) =>
            UpdateCategoryVerification(data.verification_id, {
              category: data.category,
              problematic_flag: data.problematic_flag,
              ...(view === 'problematic' && { notes: data.notes })
            })
          )
        );
        if (!results.every(r => !r.error)) {
          setError('Some verifications failed to update');
          return false;
        }
        setSuccessMessage(`${completedItems.length} verification(s) successfully updated!`);
      } else {
        const results = await Promise.all(
          completedItems.map(([_, data]) =>
            SubmitCategoryVerification({
              product: data.product_id,
              category: data.category,
              problematic_flag: data.problematic_flag
            })
          )
        );
        if (!results.every(r => !r.error)) {
          setError('Some verifications failed to submit');
          return false;
        }
        setSuccessMessage(`${completedItems.length} categor${completedItems.length === 1 ? 'y' : 'ies'} successfully verified!`);
      }

      completedItems.forEach(([productId]) => {
        setVerificationData(prev => {
          const newData = { ...prev };
          delete newData[productId];
          return newData;
        });
      });

      setCurrentPage(1);
      setTimeout(() => {
        setSuccessMessage('');
        fetchProducts();
      }, 1500);
      return true;
    } catch (err) {
      setError('Failed to submit verifications');
      return false;
    }
  };

  const getCompletedCount = () => Object.values(verificationData).filter(d => d.complete).length;

  const getDropdownOptions = (product) => {
        const CONFIDENCE_THRESHOLD = 0.05;
        const predictionCategoryIds = new Set((product.predictions || []).map(p => p.category_id));
        const flatCategories = flattenCategories(allCategories);
        const extras = flatCategories
            .filter(c => extraCategoryIds.includes(c.id) && !predictionCategoryIds.has(c.id))
            .map(c => ({ category_id: c.id, category_name: c.name, category_code: c.code, confidence: null }));
        return [
            ...(product.predictions || []).sort((a, b) => {
                const aLow = a.confidence < CONFIDENCE_THRESHOLD;
                const bLow = b.confidence < CONFIDENCE_THRESHOLD;
                if (aLow && bLow) return (a.category_code || '').localeCompare(b.category_code || '', undefined, { numeric: true, sensitivity: 'base' });
                if (aLow) return 1;
                if (bLow) return -1;
                return b.confidence - a.confidence;
            }),
            ...extras
        ];
  };

  if (loading) {
    return <div className="flex justify-center p-8"><CircularProgress /></div>;
  }

  if (!scheme || !source) {
    return (
      <div className="p-8">
        <Typography variant="h4" className="mb-6">Category Verification</Typography>
        <Alert severity="error">
          Missing required parameters. Please access this page through the verification setup.
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-8 max-w-full overflow-x-auto">
      <Typography variant="h4" className="mb-4">{getPageTitle()}</Typography>

      <Box className="mb-6 flex justify-between items-center">
        <Typography variant="body1">{getPageDesc()}</Typography>
        {getCompletedCount() > 0 && (
          <Typography variant="body2" color="primary" sx={{ fontWeight: 'bold' }}>
            {getCompletedCount()} marked as complete
          </Typography>
        )}
      </Box>

      <Snackbar open={!!successMessage} autoHideDuration={3000} onClose={() => setSuccessMessage('')}>
        <Alert severity="success" onClose={() => setSuccessMessage('')}>{successMessage}</Alert>
      </Snackbar>

      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)}>
        <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>
      </Snackbar>

      {products.length === 0 ? (
        <Alert severity="info">No products to verify</Alert>
      ) : (
        <>
          <TableContainer component={Paper} sx={{ overflowX: 'auto' }}>
            <Table sx={{ minWidth: isProblematicView() ? 750 : 550 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Product name</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Flag</TableCell>
                  {isProblematicView() && <TableCell>Notes</TableCell>}
                  <TableCell>Complete?</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {products.map((product) => {
                  const options = getDropdownOptions(product);
                  return (
                    <TableRow key={product.id}>
                      <TableCell sx={{ minWidth: 200 }}>
                        <Link
                          to={`/tools/product-browser/${product.store_product_id || product.id}`}
                          target="_blank"
                          style={{ color: '#023466ff', textDecoration: 'none' }}
                          onMouseEnter={e => e.target.style.textDecoration = 'underline'}
                          onMouseLeave={e => e.target.style.textDecoration = 'none'}
                        >
                          {product.product_name}
                        </Link>
                      </TableCell>
                      <TableCell sx={{ minWidth: 250 }}>
                        <Select
                          value={verificationData[product.id]?.category || ''}
                          onChange={e => handleCategoryChange(product.id, e.target.value)}
                          fullWidth
                          size="small"
                        >
                          {options.map(opt => (
                            <MenuItem
                              key={`${opt.category_id}-${product.id}`}
                              value={opt.category_id}
                            >
                              {opt.category_code} - {opt.category_name}
                              {opt.confidence !== null && ` - ${(opt.confidence * 100).toFixed(1)}%`}
                            </MenuItem>
                          ))}
                        </Select>
                      </TableCell>
                      <TableCell>
                        <Checkbox
                          checked={verificationData[product.id]?.problematic_flag || false}
                          onChange={() => handleProblematicToggle(product.id)}
                        />
                      </TableCell>
                      {isProblematicView() && (
                        <TableCell sx={{ minWidth: 200 }}>
                          <TextField
                            value={verificationData[product.id]?.notes || ''}
                            onChange={e => handleNotesChange(product.id, e.target.value)}
                            fullWidth
                            size="small"
                            multiline
                            maxRows={3}
                            placeholder="Add notes..."
                          />
                        </TableCell>
                      )}
                      <TableCell>
                        <Checkbox
                          checked={verificationData[product.id]?.complete || false}
                          onChange={() => handleCompleteToggle(product.id)}
                          color="success"
                        />
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>

          {totalPages > 1 && (
            <Box className="mt-6 flex justify-center">
              <Pagination
                count={totalPages}
                page={currentPage}
                onChange={handlePageChange}
                color="primary"
                size="large"
                showFirstButton
                showLastButton
              />
            </Box>
          )}

          {view !== 'read-only' && (
            <Box className="mt-8">
              <Button
                variant="contained"
                color="primary"
                onClick={handleSubmit}
                disabled={getCompletedCount() === 0}
                size="large"
              >
                Submit {getCompletedCount() > 0 && `(${getCompletedCount()})`}
              </Button>
            </Box>
          )}
        </>
      )}
    </div>
  );
};

export default CategoryVerification;