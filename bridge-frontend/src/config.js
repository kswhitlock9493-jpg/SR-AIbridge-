const config = {
  // API Base URL - configurable via environment variable for Netlify/Render deployments
  // Support both Vite (VITE_API_BASE) and Create React App (REACT_APP_API_URL) patterns
  API_BASE_URL: import.meta.env?.VITE_API_BASE || 
    process.env.VITE_API_BASE || 
    process.env.REACT_APP_API_BASE || 
    process.env.REACT_APP_API_URL || 
    (process.env.NODE_ENV === 'development' ? "http://localhost:8000" : "https://sr-aibridge-backend.onrender.com")
};

export default config;
