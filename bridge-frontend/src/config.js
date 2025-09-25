const config = {
  // API Base URL - configurable via environment variable for Netlify/Render deployments
  // Support both Vite (VITE_API_BASE) and Create React App (REACT_APP_API_URL) patterns
  API_BASE_URL: import.meta.env?.VITE_API_BASE || 
    import.meta.env?.VITE_API_BASE_URL ||
    (typeof process !== 'undefined' ? process.env.VITE_API_BASE : null) || 
    (typeof process !== 'undefined' ? process.env.REACT_APP_API_BASE : null) || 
    (typeof process !== 'undefined' ? process.env.REACT_APP_API_URL : null) || 
    (import.meta.env?.MODE === 'development' || (typeof process !== 'undefined' && process.env.NODE_ENV === 'development')
      ? "http://localhost:8000" 
      : "https://sr-aibridge.onrender.com")
};

export default config;
