// PrivateRoute.js
import React from 'react';
import { Navigate } from 'react-router-dom';

const PrivateRoute = ({ children, requiredGroup }) => {
  const user = JSON.parse(localStorage.getItem('user'));
  const token = localStorage.getItem('token');

  if (!token || !user) {
    return <Navigate to="/login" />;
  }
  
  if (requiredGroup && !user.is_staff && !user.groups.includes(requiredGroup)) {
    return <Navigate to="/unauthorized" />;
  }
  
  return children;
};

export default PrivateRoute;