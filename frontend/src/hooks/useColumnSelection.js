import { useState } from 'react';

const useColumnSelection = (initialVisibility, columnOrder = null) => {
    const [columnsVisibility] = useState(initialVisibility);
    const [selectedColumns, setSelectedColumns] = useState(Object.keys(initialVisibility));

    const handleColumnSelection = (event) => {
        const value = event.target.value;
        if (columnOrder) {
            setSelectedColumns(columnOrder.filter(col => value.includes(col)));
        } else {
            setSelectedColumns(value);
        }
    };

    return { columnsVisibility, selectedColumns, setSelectedColumns, handleColumnSelection };
};

export default useColumnSelection;
