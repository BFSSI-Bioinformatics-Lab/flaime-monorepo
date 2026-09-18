import { FaQuestionCircle } from "react-icons/fa";
import { styled } from "@mui/system";


export const HelpTooltipIcon = styled(FaQuestionCircle)(({theme}) => ({
    color: theme.palette.primary.dark,
    width: "16px",
    height: "16px",

    "&:hover": {
        color: theme.palette.primary.light
    }
}));