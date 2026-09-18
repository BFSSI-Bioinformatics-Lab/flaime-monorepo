import { ApiQueryGet } from "../Api";

const GetAllCategories = async () => {
  try {
    const data = await ApiQueryGet("categories/");
    return { error: false, categories: data };
  } catch (error) {
    return { error: true, message: error.message };
  }
};

const GetAllCategorySchemes = async () => {
  try {
    const data = await ApiQueryGet("categoryschemes/");
    return { error: false, categories: data };
  } catch (error) {
    return { error: true, message: error.message };
  }
};

export {
  GetAllCategories,
  GetAllCategorySchemes,
};