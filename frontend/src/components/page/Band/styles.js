import { Box } from "@mui/material";
import { styled } from '@mui/material/styles';
    
export const BannerBox = styled(Box)(() => ({
    display: 'flex',
    alignItems: 'center',
    justifyContent: "center",
    flexGrow: 1,
    width: "100%",
    height: 134,
    backgroundColor: "#D9965B",
    '& > :not(style)': {
        m: 0,
        width: '100%',
        backgroundColor: "#D9965B",
    }
}));