import React, { useEffect, useState } from 'react'
// import Product_detail from '../pages/tools/Product_detail';
import TableActionButtons from '../TableActionButtons';
import StripedTable from '../StripedTable';
import { 
    TableSearchBar,
    TableActionButtonsContainer 
} from './styles';

const MainTable = ({
    columns, 
    rows, 
    loading, 
    setLoading = () => {},
    getRowHeight, 
    onPageChange, 
    onSearchChange, 
    totalRows,
    pageSize, 
    downloadMenu = true, 
    searchBar = true
}) => {
    
    const [pageState, setPageState] = useState({
        isLoading:false,
        products: [],
        total: 0,
        page:1,
        pageSize: pageSize ?? 25,
        search:""
    })

    const [columnVisibilities, setColumnVisibilities] = useState([]);

    const toggleColumnVisibility = (index) => {
        setColumnVisibilities(columnVisibilities.toSpliced(index, 1, 
            {
                ...columnVisibilities[index],
                visible: !(columnVisibilities[index].visible)
            } 
        ));
    }

    useEffect( () =>{
        setPageState(old=>({...old, isLoading: true}))
        const action = pageState.search === "" ? 
            () => onPageChange(pageState.pageSize, pageState.page) : 
            () => onSearchChange(pageState.search, pageState.pageSize, pageState.page);
       
        action().then(
            (res) => {
                if (res != null) {
                    setPageState(old=>({...old, isLoading: false, total: res}));
                }
            }
        )
        .catch(() => setPageState(old=>({...old, isLoading: false, total: 0})));
        
    },[pageState.page, pageState.pageSize, pageState.search]);

    useEffect(() => {
        setPageState(old => ({...old, page: 1, total: totalRows ?? old.total}))
    }, [totalRows])

    useEffect(() => {
        setPageState(old => ({...old, pageSize: pageSize ?? old.pageSize}))
    }, [pageSize])

    useEffect(() => {
        setColumnVisibilities(columns.map((column) => ({ headerName: column.headerName, field: column.field, visible: true })));
    }, []);


    const requestSearch = (event) => {
        setPageState(old=>({
            ...old,
            search: event.target.value,
            page:1
        }));


    };

  return (
    <div >
            {
                downloadMenu && 
                <TableActionButtonsContainer>
                    <TableActionButtons columns={columnVisibilities} onColumnClick={toggleColumnVisibility}/>
                </TableActionButtonsContainer>
            }
            { 
                searchBar && 
                <TableSearchBar
                name="search"
                value={pageState.search}
                onChange={(searchVal) => requestSearch(searchVal)}
                variant="outlined"
                label="Search"
                // onCancelSearch={() => cancelSearch()}
                />
            }
            {/* Message that states the data is being loaded.. not great yet. */}
            {pageState.isLoading && (
                <div style={{ textAlign: 'center', padding: '10px' }}>
                    Data is being loaded...
                </div>
            )}
            <StripedTable
                rows={rows}
                rowCount={pageState.total}
                getRowHeight={getRowHeight}
                loading={pageState.isLoading || loading}
                rowsPerPageOptions={[25,50,100]}
                pagination
                page={pageState.page - 1}   //page currently visable
                pageSize={pageState.pageSize}   //# of rows visible in page
                onPageChange={(newPage) => setPageState(old =>({...old, page:newPage + 1}))}
                onPageSizeChange={(newPageSize) => setPageState(old=>({...old, pageSize: newPageSize}))}
                columns={columns}
                getRowClassName={(params) => 
                    params.indexRelativeToCurrentPage % 2 === 0 ? "even" : "odd"
                }   
                disableSelectionOnClick 
                controlledColumns={true}
                columnVisibilityModel={
                    columnVisibilities.reduce((obj, col) => (
                        { ...obj, [col.field]: col.visible }
                    ), {})
                }
                // components={{
                //     Toolbar: GridToolbar,
                // }}
            />
    </div>
  )
}

export default MainTable