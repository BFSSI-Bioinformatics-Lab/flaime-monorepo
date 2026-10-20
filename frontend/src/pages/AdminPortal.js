// AdminPortal.js
import React from 'react';

const AdminPortal = () => {
  // Redirect to Django admin
  // `??`, not `||`: production sets REACT_APP_API_URL to "" (same origin), and
  // Django serves the admin under the same PUBLIC_URL prefix as the app.
  const API_BASE_URL = process.env.REACT_APP_API_URL ?? 'http://localhost:8000';
  const URL_PREFIX = process.env.PUBLIC_URL ?? '';
  React.useEffect(() => {
    window.location.href = `${API_BASE_URL}${URL_PREFIX}/admin/`;
  }, []);
  
  return <div>Redirecting to admin panel...</div>;
};

export default AdminPortal;
