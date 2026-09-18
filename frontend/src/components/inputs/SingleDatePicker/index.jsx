import React from 'react';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { TextField } from '@mui/material';
import dayjs from 'dayjs';

function SingleDatePicker({ label, initialDate, onChange }) {
    const [selectedDate, setSelectedDate] = React.useState(dayjs(initialDate));

    const handleDateChange = (newValue) => {
        setSelectedDate(newValue);
        onChange(newValue);
    };

    return (
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DatePicker
                label={label}
                value={selectedDate}
                onChange={handleDateChange}
                renderInput={(params) => <TextField {...params} />}
            />
        </LocalizationProvider>
    );
}

export default SingleDatePicker;
