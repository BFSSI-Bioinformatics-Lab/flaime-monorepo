import React from 'react';
import { Link } from 'react-router-dom';
import { CardContent, Typography, CardActions, Button } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { SearchCards } from './styles';

const SearchCard = ({ title, content, link }) => {
  return (
    <SearchCards>
      <CardContent>
        <Typography variant='h5'>
          {title}
        </Typography>
        <Typography variant='body1' style={{ marginTop: '15px', minHeight: '96px' }}>
          {content}
        </Typography>
        <CardActions>
          <Link to={link}>
            <Button> {title} <SearchIcon fontSize="medium" style={{ marginLeft: '10px' }}/></Button>
          </Link>
        </CardActions>
      </CardContent>
    </SearchCards>
  );
}

export default SearchCard;