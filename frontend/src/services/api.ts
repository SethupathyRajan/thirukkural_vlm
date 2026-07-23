import axios from 'axios';
import { CONFIG } from '@/config/environment';

// Create axios instance with enhanced configuration
const api = axios.create({
  baseURL: CONFIG.API_URL,
  timeout: 15000, // Increased timeout for better UX
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor for adding auth tokens and logging
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add request ID for debugging
    const requestId = Math.random().toString(36).substring(2, 10);
    config.headers['X-Request-ID'] = requestId;

    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params,
        headers: config.headers
      });
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for standardized error handling and logging
api.interceptors.response.use(
  (response) => {
    // Log successful response in development
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
        headers: response.headers
      });
    }

    return response;
  },
  async (error) => {
    // Log error in development
    if (import.meta.env.DEV) {
      console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}`, {
        message: error.message,
        code: error.code,
        status: error.response?.status,
        data: response?.data
      });
    }

    // Enhance error messages for better UX
    if (!error.response) {
      // Network or timeout error
      if (error.code === 'ECONNABORTED') {
        return Promise.reject(
          new Error('Request timed out. Please check your connection and try again.')
        );
      }

      if (!navigator.onLine) {
        return Promise.reject(
          new Error('No internet connection. Please check your connection and try again.')
        );
      }

      return Promise.reject(
        new Error('Unable to connect to the server. Please check your connection and try again.')
      );
    }

    // Handle specific HTTP status codes
    const status = error.response.status;
    const data = error.response.data;

    switch (status) {
      case 400:
        return Promise.reject(
          new Error(
            data?.message || 'Bad request. Please check your input and try again.'
          )
        );
      case 401:
        // Redirect to login or refresh token
        return Promise.reject(
          new Error('Authentication required. Please log in again.')
        );
      case 403:
        return Promise.reject(
          new Error('Access denied. You do not have permission to perform this action.')
        );
      case 404:
        return Promise.reject(
          new Error('The requested resource was not found.')
        );
      case 429:
        return Promise.reject(
          new Error('Too many requests. Please wait a moment and try again.')
        );
      case 500:
        return Promise.reject(
          new Error('Internal server error. Please try again later.')
        );
      case 502:
      case 503:
      case 504:
        return Promise.reject(
          new Error('Service temporarily unavailable. Please try again later.')
        );
      default:
        return Promise.reject(
          new Error(
            data?.message ||
            `An unexpected error occurred (Status: ${status}). Please try again.`
          )
        );
    }
  }
);

// Request cancellation utility
const pendingRequests = new Map();

export const apiWithCancel = {
  get: (url, config = {}) => {
    const source = axios.CancelToken.source();
    const promise = api.get(url, {
      ...config,
      cancelToken: source.token
    });

    // Store for potential cancellation
    const key = `${url}:${JSON.stringify(config.params || {})}`;
    pendingRequests.set(key, { cancel: () => source.cancel('Cancelled by user') });

    // Clean up after completion
    promise.finally(() => {
      pendingRequests.delete(key);
    });

    return promise;
  },

  post: (url, data, config = {}) => {
    const source = axios.CancelToken.source();
    const promise = api.post(url, data, {
      ...config,
      cancelToken: source.token
    });

    // Store for potential cancellation
    const key = `${url}:${JSON.stringify(data)}`;
    pendingRequests.set(key, { cancel: () => source.cancel('Cancelled by user') });

    // Clean up after completion
    promise.finally(() => {
      pendingUrls.delete(key);
    });

    return promise;
  },

  // Cancel all pending requests
  cancelAll: () => {
    pendingRequests.forEach(({ cancel }) => {
      cancel('Batch cancellation');
    });
    pendingRequests.clear();
  }
};

// Export both the regular API and the enhanced version
export default api;
export { apiWithCancel };