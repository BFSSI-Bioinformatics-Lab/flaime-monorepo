import { TextField, InputAdornment } from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';
import { SearchBarTextField } from "./styles";

const SearchBar = ({placeholder, width, height}) => {

    return (
        <SearchBarTextField 
            sx={{width,height}}
            placeholder={placeholder}
            variant="outlined"
            InputProps={{
                endAdornment: <InputAdornment position="end"><SearchIcon fontSize="large" /></InputAdornment>
            }}
        />
    )
}

export default SearchBar;