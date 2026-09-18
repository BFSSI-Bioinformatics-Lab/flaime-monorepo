import { Button, Popper, Paper, MenuItem } from "@mui/material";
import { styled } from "@mui/system";

export const ColumnVisiblityButton = styled(Button)(() => ({
    width: 200
}));

export const ColumnMenuPopper = styled(Popper)(() => ({
    zIndex: 1000
}))

export const ColumnMenuPaper = styled(Paper)(({theme}) => ({
    width: 200,
    backgroundColor: theme.palette.primary.dark
}))

export const VisibleColumnMenuItem = styled(MenuItem)(({theme}) => ({
    "&, &:hover": { 
        color: "white", 
        backgroundColor: theme.palette.primary.dark,
    }
}));

export const HiddenColumnMenuItem = styled(MenuItem)(({theme}) => ({
    "&, &:hover": { 
        color: theme.palette.primary.dark, 
        backgroundColor: "white",
    }
}));