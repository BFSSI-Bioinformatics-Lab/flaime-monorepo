import { Container } from "@mui/material";
import { styled } from "@mui/system";

export const FooterContainer = styled(Container)(({ theme }) => ({
    padding: "20px",
    backgroundColor: theme.palette.landing
}));