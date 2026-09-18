import { Slider } from "@mui/material";
import { ListItemSlider } from "./styles";

const MultiSlider = ({min, max, onChange, tickMarks}) => {
    return (
        <ListItemSlider 
            getAriaLabel={() => "Custom marks"} 
            marks={tickMarks} 
            value={[min, max]}
            onChange={onChange}
        />
    )
}

export default MultiSlider;