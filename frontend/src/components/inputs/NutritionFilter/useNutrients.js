import { useState, useEffect } from 'react';

// Replace with your actual API method
import { GetAllNutrients } from '../../../api/services/NutrientService';

const useNutrients = () => {
    const [nutrients, setNutrients] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchNutrients = async () => {
        setLoading(true);
        try {
            const { error, nutrients } = await GetAllNutrients();
            console.log(nutrients)
            if (error || !nutrients) {
                console.error('Error fetching nutrients:', error);
                setNutrients([]);
            } else {
                setNutrients(nutrients.map(nutrient => ({ label: nutrient.name, value: nutrient.id })));
            }
        } catch (error) {
            console.error('Exception when fetching nutrients', error);
            setNutrients([]);
        } finally {
            setLoading(false);
        }
    };
    
    useEffect(() => {
        fetchNutrients();
        return () => {};
    }, []);


    return { nutrients, loading };
};

export default useNutrients;
