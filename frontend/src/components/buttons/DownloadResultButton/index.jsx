import React from 'react';
import { Button, Menu, MenuItem } from '@mui/material';
import { useProductExport } from '../../../hooks/useProductExport';

export const DownloadResultButton = ({ queryBody, totalProducts, fileNamePrefix = 'export' }) => {
  const {
    anchorEl,
    openDownloadMenu,
    handleDownloadClick,
    handleDownloadClose,
    handleDownloadSimple,
    handleDownloadFull,
    handleDownloadSupplemented
  } = useProductExport(queryBody, totalProducts);

  return (
    <>
      <Button 
        variant="contained" 
        color="secondary" 
        onClick={handleDownloadClick}
        disabled={!totalProducts || totalProducts === 0}
      >
        Download Results
      </Button>

      <Menu
        anchorEl={anchorEl}
        open={openDownloadMenu}
        onClose={handleDownloadClose}
      >
        <MenuItem onClick={() => handleDownloadSimple(fileNamePrefix)}>
          Simple CSV (Visible Columns)
        </MenuItem>
        <MenuItem onClick={() => handleDownloadFull(fileNamePrefix)}>
          Full CSV (All Data)
        </MenuItem>
        <MenuItem onClick={() => handleDownloadSupplemented(fileNamePrefix)}>
          Full CSV + Supplemented Food Flags
        </MenuItem>
      </Menu>
    </>
  );
};