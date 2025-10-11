// API Configuration - Environment-aware
// Uses values piped from backend .env file via npm start
const isDevelopment = process.env.NODE_ENV === 'development';
const backendPort = process.env.REACT_APP_BACKEND_PORT || '8000';

const API_BASE = isDevelopment 
  ? `http://localhost:${backendPort}/api/v1/research`
  : '/api/v1/research';

export { API_BASE };
