// authService.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL ?? 'http://localhost:8000';
// Same prefix Django is served under (FORCE_SCRIPT_NAME / DJANGO_URL_PREFIX),
// via CRA's build-time PUBLIC_URL so /api/ calls land under the proxy prefix.
const URL_PREFIX = process.env.PUBLIC_URL ?? '';

const axiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${URL_PREFIX}`,
  headers: {
    'Content-Type': 'application/json'
  },
});


// Add token to all requests
axiosInstance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Auth methods
const login = async (username, password) => {
  try {
    // 1. Request token
    const response = await axiosInstance.post('/api/token-auth/', { username, password });
    const { token } = response.data;

    if (token) {
      localStorage.setItem('token', token);

      // 2. Fetch user info and store it
      const userResponse = await axiosInstance.get('/api/user-info/');
      localStorage.setItem('user', JSON.stringify(userResponse.data));

      // 3. Notify app about auth change
      window.dispatchEvent(new Event('auth-change'));
      
      return true;
    }
    return false;
  } catch (error) {
    console.error("Login failed:", error.response ? error.response.data : error.message);
    throw error;
  }
};

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');

  window.dispatchEvent(new Event('auth-change'));
};

// API query function
const ApiQueryGet = async (url, controller, apiExt = "/api/") => {
  try {
    const res = await axiosInstance.get(`${apiExt}${url}`, {
      signal: controller ? controller.signal : null
    });
    return res.data;
  } catch (error) {
    console.error(`API error for ${url}:`, error);
    throw error;
  }
};

export { axiosInstance, ApiQueryGet, login, logout };