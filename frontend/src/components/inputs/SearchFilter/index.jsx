import { Autocomplete, TextField, Typography, Grid } from "@mui/material";

const SearchFilter = ({categories, onInputChange, free = true}) => {

    return (
        <>
            <Grid container spacing={3}>
                {categories.map((category, i) => (
                    <Grid key={`${category.title}${i}`} item xs={category.multiple ? 7 : 6} md={category.multiple ? 4 : 3}>
                        <div>
                            <Typography variant="h5">{category.title}</Typography>
                            <Autocomplete 
                                freeSolo={free}
                                id={`${category.title}${i}`}
                                options={category.options ?? []}
                                size={"small"}
                                multiple={category.multiple}
                                onChange={category.multiple ? (e, val) => onInputChange(category.title, e, val) : () => {}}
                                onInputChange={category.multiple ? () => {} : (e, val) => onInputChange(category.title, e, val)}
                                renderInput={(params => <TextField {...params} />)}
                                loading={category.loading}
                            />
                        </div>
                    </Grid>
                ))}
            </Grid>
        </>
    )
}

export default SearchFilter;