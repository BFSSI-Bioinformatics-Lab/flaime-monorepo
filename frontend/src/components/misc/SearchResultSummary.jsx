// src/components/SearchResultSummary.jsx
import React from 'react';
import { Divider, Typography } from '@mui/material';

const SearchResultSummary = ({ totalProducts }) => {
  if (totalProducts === 0) return null;

  let summaryText;
  if (totalProducts === 1) {
    summaryText = "Your search resulted in 1 product.";
  } else if (totalProducts < 10000) {
    summaryText = `Your search resulted in ${totalProducts} products.`;
  } else {
    summaryText = "Your search resulted in over 10,000 products. Only the first 10,000 are shown.";
  }

  return (
    <Divider style={{ marginTop: '20px', color: '#424242', marginBottom: '15px' }}>
      <Typography variant="body2">{summaryText}</Typography>
    </Divider>
  );
};

export default SearchResultSummary;