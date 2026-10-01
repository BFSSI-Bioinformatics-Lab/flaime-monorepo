import React from 'react';
import SelectInput from '../SelectInput';
import { Typography } from '@mui/material';
import useSearchOptions from '../../../hooks/useSearchOptions';

const SourceGroupSelector = ({ value, onSelect }) => {
    // Source groups from the API: { value: id, label: name (e.g. 'Total Diet Study') }.
    // The UI calls a source group a "source" and a source a "collection".
    const { sourceGroupOptions, loading } = useSearchOptions();

    const groupsWithDefault = [
        { label: 'Use all sources', value: '-1' },
        ...sourceGroupOptions
    ];

    const handleSelectionChange = (newValue) => {
        if (onSelect) {
            onSelect(newValue);
        }
    };

    return (
        <div style={{ maxWidth: '320px', minWidth: '280px' }}>
            <Typography variant="h5" style={{ padding: '10px' }}>Select a Source</Typography>
            {loading ? <p>Loading...</p> : (
                <SelectInput
                    options={groupsWithDefault}
                    value={value || '-1'}
                    onChange={handleSelectionChange}
                    label="Select a Source"
                    InputProps={{ style: { minWidth: '280px', overflow: 'hidden' } }}
                />
            )}
        </div>
    );
};

export default SourceGroupSelector;
