// SelectInput.jsx
import React from 'react';
import { Select, MenuItem } from '@mui/material';
import { CustomFormControl, CustomInputLabel } from './styles';

const SelectInput = ({ options, value, onChange, label }) => {
  return (
    <CustomFormControl variant="outlined">
      <CustomInputLabel id={`${label}-label`}>{label}</CustomInputLabel>
      <Select
        labelId={`${label}-label`}
        value={value}
        onChange={(event, child) => onChange(child.props.value)}
        label={label}
      >
      {options.map(option => (
          <MenuItem key={option.value} value={option.value}>
              {option.label}
          </MenuItem>
      ))}
      </Select>
    </CustomFormControl>
  );
};

export default SelectInput;
