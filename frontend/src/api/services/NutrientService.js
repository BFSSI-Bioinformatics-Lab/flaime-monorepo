import { ApiQueryGet } from "../Api";

const GetAllNutrients = async () => {
  try {
    const data = await ApiQueryGet("nutrients/");
    return { error: false, nutrients: data };
  } catch (error) {
    return { error: true, message: error.message };
  }
};

export {
    GetAllNutrients,
};