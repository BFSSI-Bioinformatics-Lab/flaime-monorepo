import { ApiQueryGet, ApiQueryPost } from "../Api";
import { axiosInstance } from "./authService";

/**
 * Product search / aggregation / export services.
 *
 * These replace the browser's former direct Elasticsearch calls
 * (`data/_search`, `images_v1/_doc/{id}`). All of them go through the
 * authenticated DRF API now.
 *
 * The shared request body for /search/, /store-counts/ and /export/ is:
 *   { text?: {...}, filters?: {...}, sort?: { field, order }, page?, page_size? }
 * See buildProductFinderBody / buildAdvancedSearchBody in ../../pages/tools/util.js.
 */

// POST /api/storeproducts/search/  ->  { count, next, previous, results: [StoreProductSearchResult] }
const SearchStoreProducts = async (body, controller = null) => {
  try {
    const data = await ApiQueryPost("storeproducts/search/", body, controller);
    return { error: false, data };
  } catch (error) {
    return { error: true, message: error.message };
  }
};

// POST /api/storeproducts/store-counts/  ->  [{ store, count }] (count desc)
const GetStoreCounts = async (body, controller = null) => {
  try {
    const data = await ApiQueryPost("storeproducts/store-counts/", body, controller);
    return { error: false, data };
  } catch (error) {
    return { error: true, message: error.message };
  }
};

// GET /api/storeproducts/collection-stats/?source=<id>  ->  CollectionStats
// `sourceId` omitted => stats across every source.
const GetCollectionStats = async (sourceId = null, controller = null) => {
  try {
    const qs = sourceId ? `?source=${encodeURIComponent(sourceId)}` : "";
    const data = await ApiQueryGet(`storeproducts/collection-stats/${qs}`, controller);
    return { error: false, data };
  } catch (error) {
    return { error: true, message: error.message };
  }
};

/**
 * POST /api/storeproducts/export/  ->  a CSV Blob.
 * `columns` is one of 'simple' | 'full' | 'full_supplemented'.
 * On a 4xx the server returns JSON `{ detail: "..." }`; because we ask for a
 * blob response that arrives as a Blob too, so read it back as text.
 */
const ExportStoreProducts = async (searchBody, columns = "simple") => {
  try {
    const res = await axiosInstance.post(
      "/api/storeproducts/export/",
      { ...searchBody, columns },
      { responseType: "blob" }
    );
    return { error: false, blob: res.data };
  } catch (error) {
    let message = error.message;
    const data = error?.response?.data;
    if (data && typeof data.text === "function") {
      try {
        const parsed = JSON.parse(await data.text());
        message = parsed.detail || JSON.stringify(parsed);
      } catch {
        /* keep the default message */
      }
    } else if (data?.detail) {
      message = data.detail;
    }
    return { error: true, message };
  }
};

export {
  SearchStoreProducts,
  GetStoreCounts,
  GetCollectionStats,
  ExportStoreProducts,
};
