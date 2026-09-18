import { useState, useEffect } from 'react';
import { GetAllStores } from '../../../api/services/StoreService';

const useStores = () => {
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchStores = async () => {
      setLoading(true);
      try {
        const data = await GetAllStores();
        if (data.error) {
          console.error('Error fetching Stores:', data.message);
          setStores([]);
        } else {
          setStores(data.stores.map(store => ({ label: store.name, value: store.id })));
        }
      } catch (e) {
        console.error('Exception when fetching stores', e);
        setStores([]);
      } finally {
        setLoading(false);
      }
    };

    fetchStores();
  }, []);

  return { stores, loading };
};

export default useStores;