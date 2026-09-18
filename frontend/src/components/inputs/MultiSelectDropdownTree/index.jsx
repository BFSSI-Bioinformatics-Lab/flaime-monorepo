import DropdownTreeSelect from "react-dropdown-tree-select";
import 'react-dropdown-tree-select/dist/styles.css'
import { Typography, Box, Tooltip, IconButton } from '@mui/material'
import { HelpTooltipIcon } from "../../globalStyles";


// Retrieves the indices for selected a certain node in the provided tree, given the id
//  from the 'react-dropdown-tree-select' library
export function getDropDownTreeIndices(selectedNodeId) {
    let idParts = selectedNodeId.split("-");
    idParts.splice(0, 1);
    return idParts.map((str) => Number(str));
}

export function MultiSelectDropdownTree({title, items = [], onChange = null, sx={}, helpTxt="", texts={}} = {}) {
    items = (items && items.length) ? [{label: "Select All", value: items, children: items, expanded: true, allSelected: true}] : [];
    return (
        <Box sx={sx}>
            <Box sx={{display: "flex"}}>
                { title !== undefined ? (<Typography variant="h5">{title}</Typography>) : null}
                { helpTxt !== "" ? (
                <Tooltip title={helpTxt} arrow>
                    <IconButton>
                    <HelpTooltipIcon />
                    </IconButton>
                </Tooltip>) : null}
            </Box>
            <DropdownTreeSelect data={items} onChange={onChange} className="mdl-demo" texts={texts} />
        </Box>
    );
}