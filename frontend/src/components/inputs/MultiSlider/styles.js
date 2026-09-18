import { Slider } from "@mui/material";
import { styled } from "@mui/system";

export const ListItemSlider = styled(Slider)(() => ({
    ".MuiSlider-thumb": {
        transition: "none"
    },
    ".MuiSlider-track": {
        transition: "none"
    },
    "span": {
        transition: "none"
    }
}));
