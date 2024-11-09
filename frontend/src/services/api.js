import axios from 'axios';

const API_BASE_URL = 'https://earthquake-prediction-using-ml.onrender.com';

export const predictEarthquakes = async (dateTime) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/predict`, dateTime);
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.message || 
      'Failed to generate predictions. Please try again.'
    );
  }
};
