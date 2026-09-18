import React from 'react';
import { Link } from 'react-router-dom';
import { CardContent, Typography, CardActions, Button } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { DataCard } from './styles';

const DataSourceCard = ({ title, content, link }) => {
  return (
    <DataCard>
      <CardContent>
        <Typography variant='h5'>
          {title}
        </Typography>
        <Typography variant='body1' style={{ marginTop: '15px' }}>
          {content}
        </Typography>
        <CardActions>
          <Link to={link}>
            <Button> Learn More <SearchIcon fontSize="medium" style={{ marginLeft: '10px' }}/></Button>
          </Link>
        </CardActions>
      </CardContent>
    </DataCard>
  );
}

export default DataSourceCard;