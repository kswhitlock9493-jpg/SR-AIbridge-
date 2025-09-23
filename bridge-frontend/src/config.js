const config = {
  // Use Netlify environment variable in production, fallback to localhost for dev
  API_BASE_URL: import.meta.env.VITE_API_URL || "http://localhost:8000"
};

export default config;
