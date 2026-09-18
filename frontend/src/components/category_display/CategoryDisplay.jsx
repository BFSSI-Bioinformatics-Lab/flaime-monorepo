import React from 'react';
import { Typography, Box } from '@mui/material';

const CategoryDisplay = ({ categories }) => {
    const allCategories = categories 
        ? Object.entries(categories)
            .flatMap(([scheme, data]) => [...data.manual])
            .filter(cat => !cat.verification_info?.problematic)
        : [];

    const categoriesByScheme = allCategories.reduce((acc, cat) => {
        if (!acc[cat.scheme]) {
            acc[cat.scheme] = [];
        }
        acc[cat.scheme].push(cat);
        return acc;
    }, {});

    Object.keys(categoriesByScheme).forEach(scheme => {
        categoriesByScheme[scheme].sort((a, b) => a.level - b.level);
    });

    if (Object.keys(categoriesByScheme).length === 0) {
        return null;
    }

    return (
        <Box sx={{ padding: '10px' }}>
            {Object.entries(categoriesByScheme).map(([scheme, categories]) => (
                <Box 
                    key={scheme} 
                    sx={{ 
                        marginBottom: '25px',
                        padding: '15px',
                        backgroundColor: '#f8f9fa',
                        borderRadius: '8px',
                        borderLeft: '4px solid #1976d2'
                    }}
                >
                    <Typography 
                        variant="subtitle1" 
                        sx={{ 
                            fontWeight: 'bold', 
                            marginBottom: '12px', 
                            textTransform: 'capitalize',
                            color: '#1976d2'
                        }}
                    >
                        {scheme}
                    </Typography>
                    {categories.map((cat) => (
                        <Typography 
                            key={cat.id} 
                            variant="body2" 
                            sx={{ 
                                marginLeft: `${cat.level * 15}px`,
                                marginBottom: '8px',
                                color: '#555'
                            }}
                        >
                            <span style={{ fontWeight: 500 }}>{cat.code}</span> - {cat.name}
                        </Typography>
                    ))}
                </Box>
            ))}
        </Box>
    );
};

export default CategoryDisplay;