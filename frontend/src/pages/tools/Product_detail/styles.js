import { Box, Paper, IconButton } from "@mui/material";
import { styled } from "@mui/system";
import costcoImage from './logos/costco.png';
import loblawsImage from './logos/loblaws.png';
import metroImage from './logos/metro.png';
import longosImage from './logos/longos.png';
// import saveonfoodsImage from './logos/saveonfoods.png';
import voilaImage from './logos/voila.png';
import nofrillsImage from './logos/nofrills.png';

const imageMap = {
    COSTCO: costcoImage,
    LOBLAWS: loblawsImage,
    METRO: metroImage,
    LONGOS: longosImage,
    // SAVEONFOODS: saveonfoodsImage,
    VOILA: voilaImage,
    NOFRILLS: nofrillsImage,
};

export const ExpandMore = styled((props) => {
    const { expand, ...other } = props;
    return <IconButton {...other} />;
})(({ theme, expand }) => ({
    transform: !expand ? 'rotate(0deg)' : 'rotate(180deg)',
    marginLeft: 'auto',
    transition: theme.transitions.create('transform', {
        duration: theme.transitions.duration.shortest,
    }),
}));

export const DescriptionHeader = styled('div')({
    display: 'flex',
    alignItems: 'center',
    cursor: 'pointer',
    userSelect: 'none',
});

export const ProductInfoBox = styled(Box)(() => ({
    padding: "40px 0" 
}));

export const ProductStatItem = styled(Paper)(({ theme }) => ({
    backgroundColor:  '#fff',
    ...theme.typography.body1,
    padding: theme.spacing(1),
    textAlign: 'center',
    color: theme.palette.text.secondary,
    boxShadow: "none"
  }));

  export const PageIcon = styled(Box)(({ theme, product }) => ({
    display: imageMap[product.toUpperCase()] ? 'block' : 'none',
    backgroundColor: theme.palette.landing.main,
    padding: theme.spacing(1),
    width: 140,
    height: 40,
    border: 0,
    marginRight: theme.spacing(2),
    backgroundImage: `url(${imageMap[product.toUpperCase()]})`,
    backgroundSize: 'contain',
    backgroundRepeat: 'no-repeat',
    // backgroundPosition: 'center 10px',
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
}));

export const PageTitle = styled(Paper)(({ theme }) => ({
    backgroundColor:  '#D9965B',
    ...theme.typography.h4,
    padding: theme.spacing(1),
    textAlign: 'center',
    color: '#f5f5f5',
    boxShadow: "none"
}));

export const DetailItem = styled(Paper)(({ theme }) => ({
    backgroundColor:  '#fff',
    ...theme.typography.body2,
    paddingBottom: theme.spacing(2),
    paddingLeft: theme.spacing(2),
    marginTop: theme.spacing(2),
    textAlign: 'start',
    color: '#191919',
    letterSpacing: '0.7px',
    boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
}));

export const ProductImageContainer = styled("div")(() => ({
    margin: "50px 0"
}));

export const ProductIngredientsHeadingContainer = styled("div")(() => ({
    marginTop: "40px", 
    // marginBottom: "10px"
}));
