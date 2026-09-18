import { useState } from 'react';
import { ExportStoreProducts } from '../api/services/StoreProductSearchService';

// Triggers a browser download for a Blob returned by the export endpoint.
const downloadBlob = (blob, filename) => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

// `columns` value -> filename suffix (keeps the historical file names).
const FILENAME_SUFFIX = {
  simple: 'simple',
  full: 'full',
  full_supplemented: 'supplemented',
};

/**
 * Drives the "Download Results" menu.
 *
 * The CSV is now built server-side by POST /api/storeproducts/export/ from the
 * same `{ text, filters }` body the results grid was searched with. The row cap
 * (EXPORT_MAX_ROWS) is enforced by the server, which returns 400 `{ detail }` —
 * surfaced here as an alert.
 */
export const useProductExport = (queryBody, totalProducts) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const openDownloadMenu = Boolean(anchorEl);

  const handleDownloadClick = (event) => setAnchorEl(event.currentTarget);
  const handleDownloadClose = () => setAnchorEl(null);

  const runExport = async (columns, filenamePrefix) => {
    handleDownloadClose();

    if (!totalProducts || totalProducts === 0) {
      alert('No data to download');
      return;
    }

    const { error, blob, message } = await ExportStoreProducts(queryBody, columns);
    if (error) {
      alert(message || 'Failed to fetch data for export.');
      return;
    }

    const suffix = FILENAME_SUFFIX[columns] || columns;
    downloadBlob(blob, `${filenamePrefix}_${suffix}_${new Date().toISOString().slice(0, 10)}.csv`);
  };

  return {
    anchorEl,
    openDownloadMenu,
    handleDownloadClick,
    handleDownloadClose,
    handleDownloadSimple: (prefix) => runExport('simple', prefix),
    handleDownloadFull: (prefix) => runExport('full', prefix),
    handleDownloadSupplemented: (prefix) => runExport('full_supplemented', prefix),
  };
};
