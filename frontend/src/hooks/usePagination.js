import { useState, useRef, useEffect, useCallback } from 'react';

const usePagination = (onSearch, initialRowsPerPage = 25) => {
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(initialRowsPerPage);

    // Always keep a current reference to onSearch to avoid stale closures
    const onSearchRef = useRef(onSearch);
    useEffect(() => {
        onSearchRef.current = onSearch;
    });

    const handlePageChange = useCallback((_, newPage) => {
        setPage(newPage);
        onSearchRef.current(newPage, rowsPerPage);
    }, [rowsPerPage]);

    const handleRowsPerPageChange = useCallback((event) => {
        const newRowsPerPage = parseInt(event.target.value, 10);
        setRowsPerPage(newRowsPerPage);
        setPage(0);
        onSearchRef.current(0, newRowsPerPage);
    }, []);

    return { page, setPage, rowsPerPage, setRowsPerPage, handlePageChange, handleRowsPerPageChange };
};

export default usePagination;
