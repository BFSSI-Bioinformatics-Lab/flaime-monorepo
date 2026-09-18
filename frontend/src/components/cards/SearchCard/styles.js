import {  Card } from "@mui/material";
import { styled } from "@mui/system";


export const SearchCards = styled(Card)(({ theme }) => ({
    backgroundColor: theme.palette.landing.main,
    // boxShadow: "none",
    width: "300px",
    height: "225px",
    // paddingBottom: "0px",
}))