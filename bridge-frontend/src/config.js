const config = {
  // Use React environment variable in production, fallback to production backend for deployment
  API_BASE_URL: process.env.REACT_APP_API_URL || "https://sr-aibridge.onrender.com"
};

export default config;
