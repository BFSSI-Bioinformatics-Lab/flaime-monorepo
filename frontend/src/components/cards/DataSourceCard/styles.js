import {  Card } from "@mui/material";
import { styled } from "@mui/system";


export const DataCard = styled(Card)(({ theme }) => ({
    backgroundColor: theme.palette.landing.main,
    boxShadow: "none",
    paddingBottom: "0px",
    width: "880px",
}))