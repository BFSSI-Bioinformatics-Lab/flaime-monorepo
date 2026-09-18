import React from 'react';
import { TextField, MenuItem, Typography } from '@mui/material';
import useNutrients from './useNutrients';

const NutritionFilter = ({ value, onChange }) => {
    const { nutrients, loading } = useNutrients();


    const handleNutrientChange = (event) => {
        onChange({ ...value, nutrient: event.target.value });
    };

    const handleAmountChange = (field) => (event) => {
        onChange({ ...value, [field]: event.target.value });
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', padding: '20px 15px', justifyContent: 'space-around', maxheight: '330px', overflow: 'auto', minHeight: '320px' }}>
            <Typography variant="h5" >Nutrient Filter</Typography>
            <p>Select a nutrient to filter by and a minimum and/or maximum value. Note that the unit will be as stored in the database (g/mg/ug/IU)</p>
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-around', padding: '0 15px', minHeight: '200px' }}>
                <TextField
                    select
                    label="Nutrient"
                    value={value.nutrient}
                    onChange={handleNutrientChange}
                    InputProps={{ style: { maxWidth: '280px', overflow: 'hidden' } }}
                >
                    {loading ? (
                        <MenuItem value="">Loading...</MenuItem>
                    ) : (
                        nutrients.map(option => (
                            <MenuItem key={option.value} value={option.value}>
                                {option.label}
                            </MenuItem>
                        ))
                    )}
                </TextField>
                <TextField
                    label="Minimum Amount (arbitrary units)"
                    type="number"
                    value={value.minAmount}
                    onChange={handleAmountChange('minAmount')}
                    InputProps={{ style: { maxWidth: '280px', overflow: 'hidden' } }}
                />
                <TextField
                    label="Maximum Amount (arbitrary units)"
                    type="number"
                    value={value.maxAmount}
                    onChange={handleAmountChange('maxAmount')}
                    InputProps={{ style: { maxWidth: '280px', overflow: 'hidden' } }}
                />
            </div>
        </div>
    );
};

export default NutritionFilter;
    