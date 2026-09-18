// styles.js
import { styled } from '@mui/system';
import { FormControl, InputLabel } from '@mui/material';

export const CustomFormControl = styled(FormControl)(({ theme }) => ({
  margin: theme.spacing(1),
  minWidth: 120,
  width: '100%',
}));

export const CustomInputLabel = styled(InputLabel)(({ theme }) => ({
  // Specific styles go here
}));