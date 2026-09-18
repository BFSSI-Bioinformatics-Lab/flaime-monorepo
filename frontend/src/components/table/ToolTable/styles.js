import { TableCell } from "@mui/material";
import { styled } from "@mui/system";


export const StyledTableCell = styled(TableCell)({
    fontWeight: 'bold',
    textTransform: 'none',
    '&:first-letter': {
      textTransform: 'uppercase',
    },
    textAlign: 'center',
    letterSpacing: '1px',
  });