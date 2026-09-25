import React from 'react';
import SelectInput from '../SelectInput';
import { Typography } from '@mui/material';
import useSearchOptions from '../../../hooks/useSearchOptions';

const RegionSelector = ({ value, onSelect }) => {
    // Locations from the API: { value: code (e.g. 'ON'), label: name (e.g. 'Ontario') }
    const { regionOptions, loading } = useSearchOptions();

    const regionsWithDefault = [
        { label: 'Use all regions', value: '-1' },
        ...regionOptions
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