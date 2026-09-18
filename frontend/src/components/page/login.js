import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../../api/services/authService';
import PageContainer from './PageContainer';
import { 
  Typography, 
  Box, 
  TextField, 
  Button, 
  Paper, 
  Alert,
  CircularProgress
} from '@mui/material';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const success = await login(username, password);
      if (success) {
        navigate('/'); // Redirect to home after login
      } else {
        setError('Login failed');
      }
    } catch (err) {
      setError('Invalid credentials');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageContainer>
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: 'calc(100vh - 64px)' 
        }}
      >
        <Paper 
          elevation={3} 
          sx={{ 
            padding: 4, 
            width: '100%', 
            maxWidth: 400,
            backgroundColor: 'rgba(255, 255, 255, 0.95)'
          }}
        >
          <Typography variant="h5" component="h1" align="center" gutterBottom>
            Login
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <form onSubmit={handleSubmit}>
            <TextField
              label="Username"
              variant="outlined"
              fullWidth
              margin="normal"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <TextField
              label="Password"
              type="password"
              variant="outlined"
              fullWidth
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Button
              type="submit"
              variant="contained"
              fullWidth
              sx={{ 
                mt: 3, 
                mb: 2,
                bgcolor: '#732C02',
                '&:hover': {
                  bgcolor: '#D9965B',
                }
              }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Login'}
            </Button>
          </form>
        </Paper>
      </Box>
    </PageContainer>
  );
};

export default Login;