import { TextField } from "@mui/material";
import { styled } from "@mui/system";

export const SearchBarTextField = styled(TextField)(({theme}) => ({
    justifyContent: "center",
    color: theme.palette.primary.dark,
    backgroundColor: theme.palette.grey[100],
    borderRadius: "24px",
    "& input": {
      fontSize: theme.typography.fontSize * 1.8,
      textAlign: "center",
      "::placeholder": {
        color: theme.palette.primary.dark,
        opacity: 0.8
      },
      "::-ms-input-placeholder": {
        color: theme.palette.primary.dark,
        opacity: 0.8
      },
      ":-ms-input-placeholder": {
        color: theme.palette.primary.dark,
        opacity: 0.8
      }
    },
    "& fieldset": {
      border: "none"
    },
    ".MuiSvgIcon-root path": {
      color: theme.palette.primary.dark
    }
  }));