import { Container, Typography } from "@mui/material";

import { FooterContainer } from './styles';

const Footer = () => {
    return  (
        <FooterContainer >
            <Typography variant="h4" color="primary" align="center">
                © FLAIME 2024
            </Typography>
        </FooterContainer>
    )
}

export default Footer;