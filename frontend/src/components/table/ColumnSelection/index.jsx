import React from 'react';
import { Select, MenuItem, Checkbox, ListItemText } from '@mui/material';

const ColumnSelection = ({ selectedColumns, columnsVisibility, setSelectedColumns, handleColumnSelection }) => {
  return (
    <div style={{ marginTop: '20px' }}>
      <Select
        multiple
        value={selectedColumns}
        onChange={handleColumnSelection}
        renderValue={() => 'Select Visible Table Columns'}
      >
        {Object.keys(columnsVisibility).map((column) => (
          <MenuItem key={column} value={column}>
            <Checkbox checked={selectedColumns.indexOf(column) > -1} />
            <ListItemText primary={column} />
          </MenuItem>
        ))}
      </Select>
    </div>
  );
};

export default ColumnSelection;