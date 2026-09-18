import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Paper,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { GetAllSources } from '../../../api/services/SourceService';
import { GetAllCategorySchemes } from '../../../api/services/CategoryService';
import { GetVerificationStats, GetAllUsers } from '../../../api/services/CategoryVerificationService';


const CategoryVerificationSetup = () => {
  const navigate = useNavigate();
  const [schemes, setSchemes] = useState([]);
  const [sources, setSources] = useState([]);
  const [verificationStats, setVerificationStats] = useState({});
  const [users, setUsers] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const predefinedCombinations = [
      { sourceId: 183, schemeId: 9, name: "Snacks - RA", extraCategoryIds: [349, 366, 397] },
      { sourceId: 181, schemeId: 10, name: "Baked Goods - Sodium", extraCategoryIds: [] },
      { sourceId: 186, schemeId: 9, name: "Meat and Alternatives - RA", extraCategoryIds: [] },
      { sourceId: 187, schemeId: 9, name: "Fish and Seafood - RA", extraCategoryIds: [] },
  ];

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (users.length > 0) {
      const initialSelectedUsers = {};
      predefinedCombinations.forEach(combo => {
        const comboKey = `${combo.sourceId}-${combo.schemeId}`;
        initialSelectedUsers[comboKey] = '';
      });
      setSelectedUsers(initialSelectedUsers);
    }
  }, [users]);

  const fetchData = async () => {
    try {
      const [schemesResult, sourcesResult, usersResult] = await Promise.all([
        GetAllCategorySchemes(),
        GetAllSources(),
        GetAllUsers()
      ]);

      if (schemesResult.error) {
        throw new Error('Failed to fetch schemes: ' + schemesResult.message);
      }
      if (sourcesResult.error) {
        throw new Error('Failed to fetch sources: ' + sourcesResult.message);
      }
      if (usersResult.error) {
        console.warn('Failed to fetch users:', usersResult.message);
      } else {
        setUsers(usersResult.users || []);
      }

      setSchemes(schemesResult.categories);
      setSources(sourcesResult.sources);
      
      await fetchVerificationStats();
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const fetchVerificationStats = async () => {
    const stats = {};
    for (const combo of predefinedCombinations) {
      try {
        const result = await GetVerificationStats(combo.schemeId, combo.sourceId);
        if (result.error) {
          console.warn(`Failed to fetch stats for ${combo.sourceId}-${combo.schemeId}:`, result.message);
          stats[`${combo.sourceId}-${combo.schemeId}`] = { total: 0, verified: 0, pending: 0 };
        } else {
          stats[`${combo.sourceId}-${combo.schemeId}`] = result.stats;
        }
      } catch (err) {
        console.error(`Error fetching stats for ${combo.sourceId}-${combo.schemeId}:`, err);
        stats[`${combo.sourceId}-${combo.schemeId}`] = { total: 0, verified: 0, pending: 0 };
      }
    }
    setVerificationStats(stats);
  };

  const getSchemeById = (id) => schemes.find(scheme => scheme.id === id);
  const getSourceById = (id) => sources.find(source => source.id === id);

  const handleLaunchVerification = (sourceId, schemeId) => {
      const combo = predefinedCombinations.find(c => c.sourceId === sourceId && c.schemeId === schemeId);
      const extraParam = combo?.extraCategoryIds?.length ? `&extra_categories=${combo.extraCategoryIds.join(',')}` : '';
      navigate(`/tools/verify-categories?scheme=${schemeId}&source=${sourceId}${extraParam}`);
  };

  const handleLaunchProblematic = (sourceId, schemeId) => {
      const combo = predefinedCombinations.find(c => c.sourceId === sourceId && c.schemeId === schemeId);
      const extraParam = combo?.extraCategoryIds?.length ? `&extra_categories=${combo.extraCategoryIds.join(',')}` : '';
      navigate(`/tools/verify-categories?scheme=${schemeId}&source=${sourceId}&view=problematic${extraParam}`);
  };

  const handleLaunchUserVerifications = (sourceId, schemeId) => {
      const comboKey = `${sourceId}-${schemeId}`;
      const userId = selectedUsers[comboKey];
      if (userId) {
        const combo = predefinedCombinations.find(c => c.sourceId === sourceId && c.schemeId === schemeId);
        const extraParam = combo?.extraCategoryIds?.length ? `&extra_categories=${combo.extraCategoryIds.join(',')}` : '';
        navigate(`/tools/verify-categories?scheme=${schemeId}&source=${sourceId}&view=user-verifications&user=${userId}${extraParam}`);
      }
  };
  
  const handleUserSelection = (comboKey, event) => {
    const userId = event.target.value;
    setSelectedUsers(prev => ({
      ...prev,
      [comboKey]: userId
    }));
  };

  const getProgressPercentage = (stats) => {
    if (!stats || stats.total === 0) return 0;
    return Math.round((stats.verified / stats.total) * 100);
  };

  const getStatusColor = (percentage) => {
    if (percentage >= 80) return 'success';
    if (percentage >= 50) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <div className="p-8 flex justify-center">
        <CircularProgress />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <Alert severity="error">{error}</Alert>
      </div>
    );
  }

  return (
    <div className="p-8">
      <Typography variant="h4" className="mb-2">
        Category Verification
      </Typography>
      <Typography variant="body1" color="text.secondary" className="mb-6">
        Review and verify product categorizations for quality assurance
      </Typography>

      <Grid container spacing={3}>
        {predefinedCombinations.map((combo) => {
          const scheme = getSchemeById(combo.schemeId);
          const source = getSourceById(combo.sourceId);
          const stats = verificationStats[`${combo.sourceId}-${combo.schemeId}`] || { total: 0, verified: 0, pending: 0 };
          const progressPercentage = getProgressPercentage(stats);
          const comboKey = `${combo.sourceId}-${combo.schemeId}`;
          
          return (
            <Grid item xs={12} md={6} lg={4} key={`${combo.sourceId}-${combo.schemeId}`}>
              <Card variant="outlined" className="h-full">
                <CardContent>
                  <Box className="flex justify-between items-start mb-3">
                    <Typography variant="h6" component="h3">
                      {source?.name || `Source ${combo.sourceId}`}
                    </Typography>
                    <Chip 
                      label={scheme?.name || `Scheme ${combo.schemeId}`} 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                    />
                  </Box>
                  
                  <Divider className="mb-3" />
                  
                  <Box className="space-y-3">
                    <Box className="flex justify-between text-sm">
                      <span>Progress</span>
                      <span>{progressPercentage}%</span>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={progressPercentage} 
                      color={getStatusColor(progressPercentage)}
                      className="mb-2"
                    />
                    
                    <Grid container spacing={2} className="text-sm">
                      <Grid item xs={4}>
                        <Box className="text-center">
                          <Typography variant="h6" color="primary">
                            {stats.total}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Total
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={4}>
                        <Box className="text-center">
                          <Typography variant="h6" color="success.main">
                            {stats.verified}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Verified
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={4}>
                        <Box className="text-center">
                          <Typography variant="h6" color="warning.main">
                            {stats.pending}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Pending
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </Box>
                </CardContent>
                
                <CardActions className="flex-col space-y-2">
                  <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    onClick={() => handleLaunchVerification(combo.sourceId, combo.schemeId)}
                    disabled={stats.pending === 0}
                  >
                    {stats.pending === 0 ? 'Complete' : 'Continue Verification'}
                  </Button>
                  
                  <Button
                    variant="outlined"
                    color="warning"
                    fullWidth
                    size="small"
                    onClick={() => handleLaunchProblematic(combo.sourceId, combo.schemeId)}
                  >
                    Review Problematic
                  </Button>
                  
                  <Box className="w-full space-y-2">
                    <FormControl fullWidth size="small">
                      <InputLabel id={`user-select-${comboKey}`}>Select User</InputLabel>
                      <Select
                        labelId={`user-select-${comboKey}`}
                        value={selectedUsers[comboKey] || ''}
                        onChange={(e) => handleUserSelection(comboKey, e)}
                        label="Select User"
                        displayEmpty
                      >
                        <MenuItem value="">
                          <em>Choose a user...</em>
                        </MenuItem>
                        {users.map((user) => (
                          <MenuItem key={user.id} value={user.id}>
                            {user.username || user.email || `User ${user.id}`}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                    
                    <Button
                      variant="outlined"
                      color="info"
                      fullWidth
                      size="small"
                      onClick={() => handleLaunchUserVerifications(combo.sourceId, combo.schemeId)}
                      disabled={!selectedUsers[comboKey]}
                    >
                      View User Verifications
                    </Button>
                  </Box>
                </CardActions>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      <Paper className="p-6 mt-6">
        <Typography variant="h6" className="mb-3">
          Verification Process
        </Typography>
        <Typography variant="body2" className="mb-2">
          • Products are shown in a consistent order by prediction confidence
        </Typography>
        <Typography variant="body2" className="mb-2">
          • Navigate through pages to review and verify products at your own pace
        </Typography>
        <Typography variant="body2" className="mb-2">
          • Review the predicted category and confirm or correct as needed
        </Typography>
        <Typography variant="body2">
          • Your verifications help improve categorization accuracy across the system
        </Typography>
      </Paper>
    </div>
  );
};

export default CategoryVerificationSetup;