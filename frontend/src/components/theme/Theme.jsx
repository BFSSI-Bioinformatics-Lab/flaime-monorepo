import { createTheme } from "@mui/material";

const getColorConfig = (version) => {
    if (version === 'PROD') {
        return {
            main: "rgb(115, 44, 2)",
            dark: "rgb(115, 44, 2)"
        };
    } else {
        return {
            main: "rgb(10, 44, 115)",
            dark: "rgb(10, 44, 115)"
        };
    }
}

const colorConfig = getColorConfig(process.env.REACT_APP_VERSION);

const Theme = createTheme({
    palette: {
        primary: {
            ...colorConfig,
            light: "#D9B166",
            transparent: {
                light: "#D9B16633"
            },
        },
        landing: {
            main: "#F1F1F1"
        },
        action: {
            main: "#BF6B04",
        },
    },
    typography: {
        fontFamily: [
            "K2D"
        ]
    },
    page: {
        content: {
            max: 1300
        }
    }
});

export default Theme;
