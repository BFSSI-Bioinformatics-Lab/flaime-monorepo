import React from 'react';
import SelectInput from '../SelectInput'; 

const StorageSelector = ({ value, onChange, options, loading }) => {
    const optionsWithDefault = [
        { label: 'Use all storage conditions', value: '-1' },
        ...options
    ];

    return (
        <div style={{ maxWidth: '320px', minWidth: '280px' }}>
            {loading ? <p>Loading...</p> : (
                <SelectInput
                    label="Storage Condition"
                    options={optionsWithDefault}
                    value={value || '-1'}
                    onChange={onChange}
                    InputProps={{ style: { minWidth: '280px', overflow: 'hidden' } }}
                />
            )}
        </div>
    );
};

export default StorageSelector;