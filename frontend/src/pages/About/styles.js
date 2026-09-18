import { Box, Typography} from "@mui/material";

import { styled } from "@mui/system";

export const AboutPageContainer = styled("div")(({theme}) => ({
    backgroundColor: theme.palette.landing.main
}))

export const PageTitleTypography = styled(Typography)(() => ({
    margin: "0 auto",
    padding: "20px",
    color: "rgb(115, 44, 2)",
    textAlign: "center",
}));

export const SectionTitleTypography = styled(Typography)(({theme}) => ({
    marginLeft: "5%",
    padding: "20px",
    color: theme.palette.primary.dark,
}));

export const InfoContainer = styled(Box)(() => ({
    padding: "0 10%", 
    alignItems: "right", 
}))