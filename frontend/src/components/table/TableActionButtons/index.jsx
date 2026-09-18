import { useState, useRef } from 'react';
import { ButtonGroup, Button, MenuList, ClickAwayListener } from '@mui/material';
import {
    ColumnVisiblityButton,
    ColumnMenuPopper,
    ColumnMenuPaper,
    VisibleColumnMenuItem,
    HiddenColumnMenuItem
} from "./styles";

const TableActionButtons = ({columns, onColumnClick}) => {

    const [columnsMenuAnchorEl, setColumnsMenuAnchorEl] = useState(null);
    const columnsMenuRef = useRef();
    const handleMenuClose = () => setColumnsMenuAnchorEl(null);
    const columnsMenuOpen = Boolean(columnsMenuAnchorEl);
    const onColumnsMenuButtonClick = () => setColumnsMenuAnchorEl(columnsMenuRef.current)
    return (
        <ButtonGroup>
            <ColumnVisiblityButton ref={columnsMenuRef} 
                variant="contained" 
                size="large" 
                onClick={onColumnsMenuButtonClick}
            >
                Column Visibility
            </ColumnVisiblityButton>
            <ColumnMenuPopper anchorEl={columnsMenuAnchorEl} open={columnsMenuOpen} onClose={handleMenuClose}>
                <ClickAwayListener onClickAway={handleMenuClose}>
                    <ColumnMenuPaper>
                        <MenuList>
                            { columns && 
                                columns.map((column, i) => 
                                    column.visible ?
                                    <VisibleColumnMenuItem onClick={() => onColumnClick(i)}>
                                        {column.headerName}
                                    </VisibleColumnMenuItem>
                                    :
                                    <HiddenColumnMenuItem onClick={() => onColumnClick(i)}>
                                        {column.headerName}
                                    </HiddenColumnMenuItem>
                                )
                            }
                        </MenuList>
                    </ColumnMenuPaper>
                </ClickAwayListener>
            </ColumnMenuPopper>
            <Button variant="contained" size="large">Excel</Button>
            <Button variant="contained" size="large">CSV</Button>
            <Button variant="contained" size="large">PDF</Button>
        </ButtonGroup>
    )
}

export default TableActionButtons;