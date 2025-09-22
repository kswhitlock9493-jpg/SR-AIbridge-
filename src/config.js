// src/config.js
// Point API calls to your Railway backend.
// Update `API_BASE_URL` after deployment with your Railway-provided URL.

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

export default {
  API_BASE_URL,
};