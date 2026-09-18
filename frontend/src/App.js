// import Table from "./components/Table";
import { useEffect } from 'react';
import Home from "./pages/Home";
import Login from "./components/page/login";
import Header from "./components/page/Header";
import Footer from "./components/page/Footer";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from '@mui/material/styles';
import Theme from "./components/theme/Theme";
import ProductBrowser from "./pages/tools/Product_browser";
import ProductDetail from "./pages/tools/Product_detail";
import Download from "./pages/data/Download";
import Quality from "./pages/data/Quality";
import Visualizations from "./pages/data/Visualizations";
import About from "./pages/About";
import ProductFinder from "./pages/tools/Product_finder";
import AdvancedSearch from "./pages/tools/Advanced_search";
import CategoryVerification from "./pages/tools/Category_verification";
import PrivateRoute from './context/auth/PrivateRoute';
import AdminPortal from './pages/AdminPortal';
import CategoryVerificationSetup from './pages/tools/Category_verification_setup';
import CollectionStats from './pages/reports/Collection_stats';

function App() {
  useEffect(() => {
    document.title = process.env.REACT_APP_TITLE || 'Default App Title';
  }, []);

  return (
    <BrowserRouter basename={process.env.PUBLIC_URL}>
      <ThemeProvider theme={Theme}>
        <div className="App">
          <Header />
          <Routes>
            <Route path="/login" element={<Login />} />
            {/* All other routes wrapped in PrivateRoute. use eg requiredGroup="Staff" to restrict to certain groups */}
            <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
            <Route path="tools/product-browser" element={<PrivateRoute requiredGroup="HC"><ProductBrowser /></PrivateRoute>} />
            <Route path="tools/product-finder" element={<PrivateRoute><ProductFinder /></PrivateRoute>} />
            <Route path="tools/advanced-search" element={<PrivateRoute><AdvancedSearch /></PrivateRoute>} />
            <Route path="tools/verify-categories" element={<PrivateRoute requiredGroup="staff"><CategoryVerification /></PrivateRoute>} />
            <Route path="reports/collection-stats" element={<PrivateRoute><CollectionStats /></PrivateRoute>} />
            <Route path="tools/category-verification-setup" element={<PrivateRoute requiredGroup="Staff"><CategoryVerificationSetup /></PrivateRoute>} />
            <Route path="data/quality" element={<PrivateRoute><Quality /></PrivateRoute>} />
            <Route path="data/download" element={<PrivateRoute><Download /></PrivateRoute>} />
            <Route path="data/visualizations" element={<PrivateRoute><Visualizations /></PrivateRoute>} />
            <Route path="about" element={<PrivateRoute><About /></PrivateRoute>} />
            <Route path="tools/product-browser/:productId" element={<PrivateRoute><ProductDetail /></PrivateRoute>} />
            <Route path="admin" element={<PrivateRoute><AdminPortal /></PrivateRoute>} />
          </Routes>
          <Footer />
        </div>
      </ThemeProvider>
    </BrowserRouter>
  );
}
export default App;
