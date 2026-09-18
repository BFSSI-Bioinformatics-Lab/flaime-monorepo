import React from 'react';
import { TextField, Button } from '@mui/material';
import { styled } from '@mui/material/styles';

const Input = styled('input')({
  display: 'none',
});

const TextFileInput = ({ text, onTextChange }) => {
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      onTextChange(e.target.result);  // Notify parent about the change
    };
    reader.readAsText(file);
  };

  return (
    <div>
      <TextField
        fullWidth
        multiline
        rows={4}
        variant="outlined"
        value={text}
        onChange={(e) => onTextChange(e.target.value)}
        label="Paste list here"
        margin="normal"
      />
      <label htmlFor="file-upload">
        <Input accept=".txt" id="file-upload" type="file" onChange={handleFileChange} />
        <Button variant="contained" component="span">
          Upload Text File
        </Button>
      </label>
    </div>
  );
};

export default TextFileInput;
