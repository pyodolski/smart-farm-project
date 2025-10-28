const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? "https://smart-farm-ignore.onrender.com"
  : "http://localhost:5001";

export default API_BASE_URL;