import { FormGroup, Typography, FormControl, FormControlLabel, Checkbox, Box, Tooltip, IconButton } from '@mui/material'
import { HelpTooltipIcon } from "../../globalStyles";


function CheckBoxGroup({title, items = {}, row = true, labelPlacement = "end", sx={}, helpTxt="", onChecked=null} = {}) {
    return (
        <Box sx={sx}>
            <FormControl component="fieldset">
                <Box sx={{display: "flex"}}>
                    { title !== undefined ? (<Typography variant="h5">{title}</Typography>) : null}
                    { helpTxt !== "" ? (
                    <Tooltip title={helpTxt} arrow>
                        <IconButton>
                        <HelpTooltipIcon />
                        </IconButton>
                    </Tooltip>) : null}
                </Box>
                <FormGroup row={Boolean(row)}>
                    {items.map((item, ind) => {
                        return <FormControlLabel
                                    value={item.value}
                                    control={<Checkbox onChange={onChecked !== null ? () => onChecked(item, ind) : null}/>}
                                    label={item.name}
                                    labelPlacement={labelPlacement}
                                ></FormControlLabel>})}
                </FormGroup>
            </FormControl>
        </Box>
    );
}

export default CheckBoxGroup;