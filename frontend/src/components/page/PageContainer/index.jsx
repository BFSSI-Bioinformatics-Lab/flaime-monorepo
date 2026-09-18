import { Container, useTheme } from "@mui/material";

/* Wraps page to keep page within a same max width */

const PageContainer = ({children}) => {
    const theme = useTheme();
    return <Container sx={{maxWidth: theme.page.content.max}} maxWidth={false}>{children}</Container>
}

export default PageContainer;