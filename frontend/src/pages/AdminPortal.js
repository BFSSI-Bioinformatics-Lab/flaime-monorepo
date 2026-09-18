// AdminPortal.js
import React from 'react';

const AdminPortal = () => {
  // Redirect to Django admin
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  React.useEffect(() => {
    window.location.href = `${API_BASE_URL}/admin/`;
  }, []);
  
  return <div>Redirecting to admin panel...</div>;
};

export default AdminPortal;
