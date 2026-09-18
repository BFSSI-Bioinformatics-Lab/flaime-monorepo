import { Box, Container, Typography } from "@mui/material";

import { styled } from "@mui/system";
import quickSearch from "../../static/images/singin.jpg";



export const HomePageContainer = styled("div")(({theme}) => ({
    backgroundColor: theme.palette.landing.main
}))

export const PageTitleTypography = styled(Typography)(() => ({
    position: "absolute", 
    color: "rgb(115, 44, 2)",
    top: '25%',
    left: "25%",
    transform: "translateX(-60%)"
}));

export const PageDescriptionTypography = styled(Typography)(() => ({
    position: "absolute", 
    color: "#732C02",
    top: '45%',
    left: "45%",
    transform: "translateX(-58%)"
}));

export const SearchBarContainer = styled(Box)(() => ({
    height: "375px", 
    backgroundImage:`url(${quickSearch})`, 
    backgroundRepeat: "no-repeat", 
    backgroundSize: "cover", 
    backgroundPosition: "80% 50%", 
    display: "flex", 
    alignItems: "center", 
    justifyContent: "space-evenly"
}))

export const DataSourceContainer = styled(Box)(() => ({
    // height: "450px", 
    display: "flex",
    flexDirection: "column", 
    alignItems: "center", 
    // justifyContent: "space-between",
    // marginBottom: "35px",
    // marginTop: "15px"
}))

export const HeadingContainer = styled(Container)(() => ({
    padding: "25px"
}))

