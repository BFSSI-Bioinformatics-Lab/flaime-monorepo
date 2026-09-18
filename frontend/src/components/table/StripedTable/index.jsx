import { StripedDataGrid } from "./styles"

const StripedTable = ({
    getRowHeight,
    rows,
    rowCount,
    loading,
    rowsPerPageOptions=[25,50,100],
    pagination = true,
    page = 0,   //page currently visable
    pageSize= 25,   //# of rows visible in page
    paginationMode="server",
    onPageChange = () => {},
    onPageSizeChange= () => {},
    columns,
    columnVisibilityModel,
    controlledColumns
}) => {

    return (
        <StripedDataGrid                
            autoHeight
            getRowHeight={getRowHeight ?? (() => "auto")}
            rows={rows}
            rowCount={rowCount}
            loading={loading}
            rowsPerPageOptions={rowsPerPageOptions}
            pagination={pagination}
            page={page}   //page currently visable
            pageSize={pageSize}   //# of rows visible in page
            paginationMode={paginationMode}
            onPageChange={onPageChange}
            onPageSizeChange={onPageSizeChange}
            columns={columns}
            getRowClassName={(params) => 
                params.indexRelativeToCurrentPage % 2 === 0 ? "even" : "odd"
            }   
            disableSelectionOnClick 
            disableColumnFilter={controlledColumns}
            disableColumnSelector={controlledColumns}
            columnVisibilityModel={columnVisibilityModel}            
        />
    )
}

export default StripedTable;