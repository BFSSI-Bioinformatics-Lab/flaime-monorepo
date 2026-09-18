import { ApiQueryGet } from "../Api";

const GetStoreProductByID = async (productId, controller = null) => {
    console.log(`GetStoreProductByID called with productId: ${productId}`);
    try {
        const data = await ApiQueryGet(`storeproducts/${productId}/`, controller);
        return { error: false, data: data };
    } catch (error) {
        console.error(`Error in GetStoreProductByID: ${error.message}`);
        return { error: true, message: error.message };
    }
};
  
export {
    GetStoreProductByID,
};