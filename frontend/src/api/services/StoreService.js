import { ApiQueryGet } from "../Api";

const GetAllStores = async () => {
  try {
    const data = await ApiQueryGet("stores/");
    return { error: false, stores: data };
  } catch (error) {
    return { error: true, message: error.message };
  }
};

export {
    GetAllStores,
};