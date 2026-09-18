import { axiosInstance } from "./services/authService";

const ApiInstance = axiosInstance;

// Helper to cleanly join API extension and endpoint
const cleanUrl = (ext, url) => {
  const cleanExt = ext.endsWith('/') ? ext.slice(0, -1) : ext;
  const cleanUrl = url.startsWith('/') ? url.slice(1) : url;
  return `${cleanExt}/${cleanUrl}`;
};

const ApiQueryGet = async (url, controller, apiExt = "/api/") => {
  try {
    const fullUrl = cleanUrl(apiExt, url);
    const res = await ApiInstance.get(fullUrl, {
      signal: controller ? controller.signal : null
    });
    return res.data;
  } catch (error) {
    console.error(`API error for ${url}:`, error);
    throw error;
  }
};

const ApiQueryPost = async (url, data, controller, apiExt = "/api/") => {
  try {
    const fullUrl = cleanUrl(apiExt, url);
    const res = await ApiInstance.post(fullUrl, data, {
      signal: controller ? controller.signal : null
    });
    return res.data;
  } catch (error) {
    console.error(`API error for ${url}:`, error);
    throw error;
  }
};

const ApiQueryPatch = async (url, data, controller, apiExt = "/api/") => {
  try {
    const fullUrl = cleanUrl(apiExt, url);
    const res = await ApiInstance.patch(fullUrl, data, {
      signal: controller ? controller.signal : null
    });
    return res.data;
  } catch (error) {
    console.error(`API error for ${url}:`, error);
    throw error;
  }
};

const ApiQueryPut = async (url, data, controller, apiExt = "/api/") => {
  try {
    const fullUrl = cleanUrl(apiExt, url);
    const res = await ApiInstance.put(fullUrl, data, {
      signal: controller ? controller.signal : null
    });
    return res.data;
  } catch (error) {
    console.error(`API error for ${url}:`, error);
    throw error;
  }
};

export default ApiInstance;
export { ApiQueryGet, ApiQueryPost, ApiQueryPatch, ApiQueryPut };