import React from 'react';
import { Typography, Box } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

const SupplementedFoodFlags = ({ labelFlags }) => {
    if (!labelFlags) {
        return null;
    }

    const flagLabels = {
        has_supplemental_caution_id: 'Supplemental Caution',
        has_nutrient_content_claim: 'Nutrient Content Claim',
        has_nutrient_function_claim: 'Nutrient Function Claim',
        has_disease_risk_reduction_claim: 'Disease Risk Reduction Claim',
        has_probiotic_claim: 'Probiotic Claim',
        has_therapeutic_claim: 'Therapeutic Claim',
        has_function_claim: 'Function Claim',
        has_general_health_claim: 'General Health Claim',
        has_quantitative_nutrient_declaration: 'Quantitative Nutrient Declaration',
        has_implied_nonspecific_claim: 'Implied Nonspecific Claim',
        has_logos_icons: 'Logos/Icons',
        has_third_party_label: 'Third Party Label'
    };

    return (
        <Box 
            sx={{ 
                padding: '20px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                borderLeft: '4px solid #2e7d32'
            }}
        >
            <Typography 
                variant="subtitle1" 
                sx={{ 
                    fontWeight: 'bold', 
                    marginBottom: '16px',
                    color: '#2e7d32'
                }}
            >
                Supplemented Food Label Flags
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {Object.entries(labelFlags).map(([key, value]) => (
                    <Box 
                        key={key}
                        sx={{ 
                            display: 'flex', 
                            alignItems: 'center',
                            gap: '8px'
                        }}
                    >
                        {value ? (
                            <CheckCircleIcon sx={{ color: '#2e7d32', fontSize: '18px' }} />
                        ) : (
                            <CancelIcon sx={{ color: '#bdbdbd', fontSize: '18px' }} />
                        )}
                        <Typography 
                            variant="body2"
                            sx={{ 
                                color: value ? '#333' : '#757575',
                                fontWeight: value ? 500 : 400
                            }}
                        >
                            {flagLabels[key] || key}
                        </Typography>
                    </Box>
                ))}
            </Box>
        </Box>
    );
};

export default SupplementedFoodFlags;