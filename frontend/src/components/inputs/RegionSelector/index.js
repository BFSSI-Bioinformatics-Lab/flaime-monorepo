import React from 'react';
import SelectInput from '../SelectInput';
import { Typography } from '@mui/material';

const RegionSelector = ({ value, onSelect }) => {
    // const { regions, loading } = useRegions();
    const regions = ["ottawa", "QC", "BC", "ON", "montreal", "vancouver"];
    const loading = false;

    const regionsWithDefault = [
        { label: 'Use all regions', value: '-1' },
        ...regions.map(region => ({ label: region, value: region }))
    ];

    const handleSelectionChange = (newValue) => {
        if (onSelect) {
            onSelect(newValue);
        }
    };

    return (
        <div style={{ maxWidth: '320px', minWidth: '280px' }}>
            <Typography variant="h5" style={{ padding: '10px' }}>Select a Region</Typography>
            {loading ? <p>Loading...</p> : (
                <SelectInput
                    options={regionsWithDefault}
                    value={value || '-1'}
                    onChange={handleSelectionChange}    
                    label="Select a Region"
                    InputProps={{ style: { minWidth: '280px', overflow: 'hidden' } }}
                />
            )}
        </div>
    );
};

export default RegionSelector;