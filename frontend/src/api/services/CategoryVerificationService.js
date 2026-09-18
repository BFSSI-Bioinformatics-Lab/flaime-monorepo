import { ApiQueryGet, ApiQueryPost, ApiQueryPatch } from "../Api";


const GetCategoriesToVerify = async (scheme = 9, source = 178, page = 1, pageSize = 50) => {
  try {
    const data = await ApiQueryGet(
      `category-verifications/get_predictions/?scheme=${scheme}&source=${source}&page=${page}&page_size=${pageSize}`
    );
    return { 
      error: false, 
      products: data.results || data,
      count: data.count || (data.results ? data.results.length : data.length),
      next: data.next || null,
      previous: data.previous || null
    };
  } catch (error) {
    return { error: true, message: error.message };
  }
};


const SubmitCategoryVerification = async (verification) => {
  try {
    const response = await ApiQueryPost("category-verifications/create_verification/", verification);
    return { error: false, data: response };
  } catch (error) {
    return { error: true, message: error.message };
  }
};


const GetVerificationStats = async (scheme = 9, source = 178) => {
  try {
    const data = await ApiQueryGet(`category-verifications/get_predictions/?scheme=${scheme}&source=${source}&stats_only=true`);
    return {
      error: false,
      stats: {
        total: data.total_count || 0,
        verified: data.verified_count || 0,
        pending: (data.total_count || 0) - (data.verified_count || 0)
      }
    };
  } catch (error) {
    return {
      error: true,
      message: error.message,
      stats: { total: 0, verified: 0, pending: 0 }
    };
  }
};


const GetProblematicVerifications = async (scheme = 9, source = 178, page = 1, pageSize = 50) => {
  try {
    const data = await ApiQueryGet(
      `category-verifications/get_predictions/?scheme=${scheme}&source=${source}&problematic=true&page=${page}&page_size=${pageSize}`
    );
    return { 
      error: false, 
      products: data.results || data,
      count: data.count || (data.results ? data.results.length : data.length),
      next: data.next || null,
      previous: data.previous || null
    };
  } catch (error) {
    return { error: true, message: error.message };
  }
};


const GetUserVerifications = async (scheme = 9, source = 178, userId = null, page = 1, pageSize = 50) => {
  try {
    let url = `category-verifications/get_predictions/?scheme=${scheme}&source=${source}&verified=true&page=${page}&page_size=${pageSize}`;
    if (userId) {
      url += `&user=${userId}`;
    }
    const data = await ApiQueryGet(url);
    return { 
      error: false, 
      products: data.results || data,
      count: data.count || (data.results ? data.results.length : data.length),
      next: data.next || null,
      previous: data.previous || null
    };
  } catch (error) {
    return { error: true, message: error.message };
  }
};


const UpdateCategoryVerification = async (verificationId, updates) => {
  try {
    const response = await ApiQueryPatch(`category-verifications/${verificationId}/update_verification/`, updates);
    return { error: false, data: response };
  } catch (error) {
    return { error: true, message: error.message };
  }
};


const GetAllUsers = async () => {
  try {
    const data = await ApiQueryGet('users/');
    return { error: false, users: data };
  } catch (error) {
    return { error: true, message: error.message };
  }
};


export {
  GetCategoriesToVerify,
  SubmitCategoryVerification,
  GetVerificationStats,
  GetProblematicVerifications,
  GetUserVerifications,
  UpdateCategoryVerification,
  GetAllUsers
};