import { FormLabel } from "@mui/material"
import { RangeTextField } from "./styles"

const InputRangeField = ({label, value}) => {
    return (
        <div>
            <FormLabel color="primary">{label}</FormLabel>
             <RangeTextField disabled fullWidth variant="filled" color="primary.dark" size="small" value={value} />
        </div>
    )
}

export default InputRangeField;