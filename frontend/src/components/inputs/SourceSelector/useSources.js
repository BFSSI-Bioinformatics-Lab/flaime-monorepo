import { useState, useEffect } from 'react';
import { GetAllSources } from '../../../api/services/SourceService';

const useSources = () => {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSources = async () => {
      setLoading(true);
      try {
        const data = await GetAllSources();
        if (data.error) {
          console.error('Error fetching Sources:', data.message);
          setSources([]);
        } else {
          setSources(data.sources.map(source => ({ label: source.name, value: source.id })));
        }
      } catch (e) {
        console.error('Exception when fetching sources', e);
        setSources([]);
      } finally {
        setLoading(false);
      }
    };

    fetchSources();
  }, []);

  return { sources, loading };
};

export default useSources;