import React from 'react';
import { Grid, Paper } from '@mui/material';
import { PhotoProvider, PhotoView } from 'react-photo-view';
import 'react-photo-view/dist/react-photo-view.css';

// Image paths now arrive on the product payload itself
// (DetailedStoreProduct.store_product_images), so there is no separate fetch.
const ProductImages = ({ product }) => {
    const images = Array.isArray(product?.store_product_images) ? product.store_product_images : [];

    const imagePathToUrl = (imagePath) => `${process.env.REACT_APP_IMG_SERVER_URL}/images/${imagePath}`;
    const thumbPathToUrl = (imagePath) => `${process.env.REACT_APP_IMG_SERVER_URL}/thumb/${imagePath}`;

    const handleImageError = (e) => {
        e.target.style.display = 'none';
    };

    if (images.length === 0) return null;

    return (
        <PhotoProvider>
            <Grid container spacing={2} style={{ marginTop: '20px' }}>
                {images.map((imagePath, index) => (
                    <Grid key={index} item xs={12} sm={4} md={4} lg={4}>
                        <Paper elevation={3} style={{ padding: '10px', cursor: 'pointer' }}>
                            <PhotoView src={imagePathToUrl(imagePath)}>
                                <img
                                    src={thumbPathToUrl(imagePath)}
                                    alt={product.site_name}
                                    style={{ width: '100%', height: 'auto', objectFit: 'contain' }}
                                    onError={handleImageError}
                                />
                            </PhotoView>
                        </Paper>
                    </Grid>
                ))}
            </Grid>
        </PhotoProvider>
    );
};

export default ProductImages;
