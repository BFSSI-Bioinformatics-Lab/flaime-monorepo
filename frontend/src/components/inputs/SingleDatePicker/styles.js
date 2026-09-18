import { Box, Typography } from '@mui/material'
import { styled } from "@mui/system";
import { DatePicker } from '@mui/x-date-pickers';


export const DatePickerContainer = styled(Box)(({theme}) => ({
    marginTop: "15px",
}));

export const DateBetweenTextContainer = styled(Box)(({theme}) => ({
    display: "inline-flex"
}));

export const DateBetweenText = styled(Typography)(({theme}) => ({
    padding: "15px"
}));

export const DatePickerInput = styled(DatePicker)(({theme}) => ({
    "& label": {
        zIndex: 0
    }
}));