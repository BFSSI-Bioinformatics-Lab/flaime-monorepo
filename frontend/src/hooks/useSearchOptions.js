import { useState, useEffect } from 'react';
import { GetSearchOptions } from '../api/services/SearchOptionsService';

const useSearchOptions = () => {
  const [sourceOptions, setSourceOptions] = useState([]);
  const [storeOptions, setStoreOptions] = useState([]);
  const [regionOptions, setRegionOptions] = useState([]);
  const [storageOptions, setStorageOptions] = useState([]);
  const [packagingOptions, setPackagingOptions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchOptions = async () => {
      setLoading(true);
      try {
        const result = await GetSearchOptions();

        if (result.error) {
          console.error('Error fetching Options:', result.message);
        } else {
          const data = result.data;
          
          if (data.sources) setSourceOptions(data.sources);
          if (data.stores) setStoreOptions(data.stores);
          if (data.regions) setRegionOptions(data.regions);
          if (data.storage) setStorageOptions(data.storage);
          if (data.packaging) setPackagingOptions(data.packaging);
        }
      } catch (e) {
        console.error('Exception when fetching options', e);
      } finally {
        setLoading(false);
      }
    };

    fetchOptions();
  }, []);

  return { 
    sourceOptions, 
    storeOptions, 
    regionOptions, 
    storageOptions, 
    packagingOptions, 
    loading 
  };
};

export default useSearchOptions;