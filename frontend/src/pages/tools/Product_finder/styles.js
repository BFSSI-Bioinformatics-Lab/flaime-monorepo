import { Box, Button, Grid, AccordionSummary, TableCell } from "@mui/material";
import { styled } from "@mui/system";


export const AdvancedSearchSection = styled(Box)(({theme}) => ({
    paddingTop: theme.spacing(3),
    paddingBottom: theme.spacing(3)
}));

export const AddNutrientButton = styled(Button)(() => ({
    fontSize: 16,
    marginBottom: 5
}));

export const SearchButton = styled(Button)(() => ({
    fontSize: 16
}));

export const NutrientFiltersGrid = styled(Grid)(() => ({
    paddingBottom: 2
}));

export const FilterStyles = {
    marginBottom: '30px'
}

export const CategorySearchStyle = {
    marginTop: '30px',
    marginBottom: '50px'
}

export const StyledTableCell = styled(TableCell)({
    fontWeight: 'bold',
    textTransform: 'none',
    '&:first-letter': {
      textTransform: 'uppercase',
    },
    textAlign: 'center',
    letterSpacing: '1px',
  });