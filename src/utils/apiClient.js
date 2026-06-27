/**
 * Centralized API Client for Moove
 * Handles all HTTP requests, authentication, error handling, and retries
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';
const API_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// Request/Response interceptors
let requestInterceptors = [];
let responseInterceptors = [];

/**
 * Add request interceptor (e.g., for adding auth tokens)
 */
export const addRequestInterceptor = (callback) => {
  requestInterceptors.push(callback);
};

/**
 * Add response interceptor (e.g., for error handling)
 */
export const addResponseInterceptor = (callback) => {
  responseInterceptors.push(callback);
};

/**
 * Internal function to apply request interceptors
 */
const applyRequestInterceptors = async (options) => {
  let finalOptions = { ...options };
  for (const interceptor of requestInterceptors) {
    finalOptions = await interceptor(finalOptions);
  }
  return finalOptions;
};

/**
 * Internal function to apply response interceptors
 */
const applyResponseInterceptors = async (response, options) => {
  let finalResponse = response;
  for (const interceptor of responseInterceptors) {
    finalResponse = await interceptor(finalResponse, options);
  }
  return finalResponse;
};

/**
 * Core fetch function with error handling, retries, and interceptors
 */
const fetchWithRetry = async (url, options = {}, retryCount = 0) => {
  try {
    // Apply request interceptors
    const finalOptions = await applyRequestInterceptors({
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    // Set timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

    const response = await fetch(url, {
      ...finalOptions,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Apply response interceptors
    const finalResponse = await applyResponseInterceptors(response, finalOptions);

    // Handle non-2xx responses
    if (!finalResponse.ok) {
      throw new APIError(
        `HTTP ${finalResponse.status}`,
        finalResponse.status,
        await finalResponse.json().catch(() => ({}))
      );
    }

    return finalResponse;
  } catch (error) {
    // Retry logic for network errors (not for 4xx/5xx)
    if (retryCount < MAX_RETRIES && isRetryableError(error)) {
      await delay(RETRY_DELAY * (retryCount + 1)); // Exponential backoff
      return fetchWithRetry(url, options, retryCount + 1);
    }

    throw error;
  }
};

/**
 * Check if error is retryable
 */
const isRetryableError = (error) => {
  return (
    error instanceof TypeError || // Network errors
    (error instanceof APIError && error.status >= 500) // Server errors
  );
};

/**
 * Sleep utility for delays
 */
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Custom API Error class
 */
export class APIError extends Error {
  constructor(message, status, data = {}) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }

  toString() {
    return `${this.name}: ${this.message}`;
  }
}

/**
 * Main API client with common methods
 */
export const apiClient = {
  baseURL: API_BASE_URL,

  /**
   * GET request
   */
  get: async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetchWithRetry(url, {
      method: 'GET',
      ...options,
    });
    return response.json();
  },

  /**
   * POST request
   */
  post: async (endpoint, data, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetchWithRetry(url, {
      method: 'POST',
      body: JSON.stringify(data),
      ...options,
    });
    return response.json();
  },

  /**
   * PUT request
   */
  put: async (endpoint, data, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetchWithRetry(url, {
      method: 'PUT',
      body: JSON.stringify(data),
      ...options,
    });
    return response.json();
  },

  /**
   * PATCH request
   */
  patch: async (endpoint, data, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetchWithRetry(url, {
      method: 'PATCH',
      body: JSON.stringify(data),
      ...options,
    });
    return response.json();
  },

  /**
   * DELETE request
   */
  delete: async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetchWithRetry(url, {
      method: 'DELETE',
      ...options,
    });
    return response.json();
  },

  /**
   * File upload with progress tracking (for multipart/form-data)
   */
  upload: async (endpoint, formData, onProgress, options = {}) => {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const url = `${API_BASE_URL}${endpoint}`;

      // Track upload progress
      if (onProgress) {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const progress = Math.round((e.loaded / e.total) * 100);
            onProgress(progress);
          }
        });
      }

      // Handle response
      xhr.addEventListener('load', () => {
        try {
          if (xhr.status >= 200 && xhr.status < 300) {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } else {
            const error = JSON.parse(xhr.responseText);
            reject(
              new APIError(
                error.error || `HTTP ${xhr.status}`,
                xhr.status,
                error
              )
            );
          }
        } catch (err) {
          reject(new APIError('Failed to parse response', xhr.status));
        }
      });

      // Handle network error
      xhr.addEventListener('error', () => {
        reject(new APIError('Network error', 0));
      });

      // Handle abort
      xhr.addEventListener('abort', () => {
        reject(new APIError('Request aborted', 0));
      });

      // Set headers
      if (options.headers) {
        Object.entries(options.headers).forEach(([key, value]) => {
          xhr.setRequestHeader(key, value);
        });
      }

      xhr.open('POST', url);
      xhr.send(formData);
    });
  },

  /**
   * Download file
   */
  download: async (endpoint, filename, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      method: 'GET',
      ...options,
    });

    if (!response.ok) {
      throw new APIError(
        `Download failed: ${response.statusText}`,
        response.status
      );
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },
};

/**
 * Video Analysis API Endpoints
 */
export const videoAPI = {
  /**
   * Upload video for analysis
   */
  upload: async (formData, onProgress) => {
    return apiClient.upload('/api/upload', formData, onProgress);
  },

  /**
   * Start processing video
   */
  process: async (jobId) => {
    return apiClient.post(`/api/process/${jobId}`, {});
  },

  /**
   * Get processing results
   */
  getResults: async (jobId) => {
    return apiClient.get(`/api/results/${jobId}`);
  },

  /**
   * Get analysis data
   */
  getAnalysisData: async (jobId) => {
    return apiClient.get(`/api/analysis/${jobId}`);
  },

  /**
   * Get summary report
   */
  getSummaryReport: async (jobId) => {
    return apiClient.get(`/api/summary/${jobId}`);
  },

  /**
   * Get movement data
   */
  getMovementData: async (jobId) => {
    return apiClient.get(`/api/movement/${jobId}`);
  },

  /**
   * Get analytics data
   */
  getAnalytics: async (jobId) => {
    return apiClient.get(`/api/analytics/${jobId}`);
  },

  /**
   * Get visualizations
   */
  getVisualizations: async (jobId) => {
    return apiClient.get(`/api/visualizations/${jobId}`);
  },

  /**
   * Download report as PDF
   */
  downloadReport: async (jobId, filename = 'report.pdf') => {
    return apiClient.download(`/api/download/report/${jobId}`, filename);
  },
};

/**
 * Auth API Endpoints (if needed)
 */
export const authAPI = {
  login: async (credentials) => {
    return apiClient.post('/api/auth/login', credentials);
  },

  logout: async () => {
    return apiClient.post('/api/auth/logout', {});
  },

  refreshToken: async () => {
    return apiClient.post('/api/auth/refresh', {});
  },
};

/**
 * Example: Add authentication token interceptor
 * Call this in your app initialization (e.g., in main.jsx or App.jsx)
 */
export const setupAuthInterceptor = (getToken) => {
  addRequestInterceptor(async (options) => {
    const token = await getToken();
    if (token) {
      return {
        ...options,
        headers: {
          ...options.headers,
          Authorization: `Bearer ${token}`,
        },
      };
    }
    return options;
  });
};

/**
 * Example: Add error logging interceptor
 */
export const setupErrorInterceptor = () => {
  addResponseInterceptor(async (response, options) => {
    if (!response.ok) {
      console.error(`API Error: ${response.status}`, {
        url: response.url,
        method: options.method,
        status: response.status,
      });
    }
    return response;
  });
};

export default apiClient;
