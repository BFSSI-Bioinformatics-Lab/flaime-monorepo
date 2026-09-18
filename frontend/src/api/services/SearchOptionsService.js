import { ApiQueryGet } from "../Api";

const GetSearchOptions = async () => {
  try {
    const data = await ApiQueryGet("options/");
    
    return { error: false, data: data }; 
  } catch (error) {
    return { error: true, message: error.message };
  }
};

export {
    GetSearchOptions,
};