import { TextField } from "@mui/material";
import { styled } from "@mui/system";

export const RangeTextField = styled(TextField)(({theme}) => ({
    ".MuiInputBase-input.Mui-disabled": {
        color: theme.palette.primary.dark,
        "-webkit-text-fill-color": theme.palette.primary.dark
    }
}));