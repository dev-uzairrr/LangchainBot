/**
 * API client for backend communication.
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1_PREFIX = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

/**
 * RAG API
 */
export const ragAPI = {
  query: async (query, lang = 'en') => {
    const response = await apiClient.post(`${API_V1_PREFIX}/rag/query`, {
      query,
      lang,
    });
    return response.data;
  },
};

/**
 * ML API
 */
export const mlAPI = {
  sentiment: async (text) => {
    const response = await apiClient.post(`${API_V1_PREFIX}/ml/sentiment`, {
      text,
    });
    return response.data;
  },
};

/**
 * Tone API
 */
export const toneAPI = {
  adjust: async (text) => {
    const response = await apiClient.post(`${API_V1_PREFIX}/tone/adjust`, {
      text,
    });
    return response.data;
  },
};

/**
 * Admin API
 */
export const adminAPI = {
  embed: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(`${API_V1_PREFIX}/admin/embed`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

/**
 * Health API
 */
export const healthAPI = {
  check: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default apiClient;

