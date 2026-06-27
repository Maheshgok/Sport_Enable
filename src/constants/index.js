/**
 * Application Constants
 * Single source of truth for config values, endpoints, and status codes
 */

// App Configuration
export const APP_CONFIG = {
  name: 'Moove',
  version: '1.0.0',
  environment: import.meta.env.VITE_ENV || 'development',
};

// API Configuration
export const API_CONFIG = {
  baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8080',
  timeout: 30000, // 30 seconds
  retries: 3,
};

// File Size Limits
export const FILE_SIZES = {
  MAX_VIDEO: 500 * 1024 * 1024, // 500MB
  MAX_IMAGE: 5 * 1024 * 1024,   // 5MB
  MAX_PDF: 10 * 1024 * 1024,    // 10MB
};

// Valid File Types
export const VALID_FILE_TYPES = {
  VIDEO: ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 'video/webm'],
  IMAGE: ['image/jpeg', 'image/png', 'image/webp'],
  PDF: ['application/pdf'],
};

// User Roles
export const USER_ROLES = {
  ADMIN: 'admin',
  COACH: 'coach',
  ATHLETE: 'athlete',
  PHYSIOTHERAPIST: 'physiotherapist',
  CARETAKER: 'caretaker',
};

// User Status
export const USER_STATUS = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  ACTIVE: 'active',
  INACTIVE: 'inactive',
};

// Video Status
export const VIDEO_STATUS = {
  IDLE: 'idle',
  UPLOADING: 'uploading',
  UPLOADED: 'uploaded',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  ERROR: 'error',
};

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
};

// Timeouts (milliseconds)
export const TIMEOUTS = {
  API_REQUEST: 30000,      // 30 seconds
  SHORT_OPERATION: 5000,   // 5 seconds
  REDIRECT: 2000,          // 2 seconds
  TOAST: 5000,             // 5 seconds
  POLL_INTERVAL: 2000,     // 2 seconds (for status polling)
};

// Athletes Height Range (cm)
export const ATHLETE_HEIGHT = {
  MIN: 100,
  MAX: 250,
};

// Video Frame Rates
export const VIDEO_FPS = {
  MIN: 24,
  RECOMMENDED: 30,
  MAX: 120,
};

// API Endpoints
export const API_ENDPOINTS = {
  // Video endpoints
  VIDEO: {
    UPLOAD: '/api/upload',
    PROCESS: '/api/process/:jobId',
    RESULTS: '/api/results/:jobId',
    ANALYSIS: '/api/analysis/:jobId',
    SUMMARY: '/api/summary/:jobId',
    MOVEMENT: '/api/movement/:jobId',
    ANALYTICS: '/api/analytics/:jobId',
    VISUALIZATIONS: '/api/visualizations/:jobId',
    DOWNLOAD_REPORT: '/api/download/report/:jobId',
  },

  // Athlete endpoints
  ATHLETE: {
    LIST: '/api/athletes',
    GET: '/api/athlete/:id',
    CREATE: '/api/athlete',
    UPDATE: '/api/athlete/:id',
    DELETE: '/api/athlete/:id',
    PROFILE: '/api/athlete/:id/profile',
    HISTORY: '/api/athlete/:id/history',
  },

  // Coach endpoints
  COACH: {
    LIST: '/api/coaches',
    GET: '/api/coach/:id',
    ATHLETES: '/api/coach/:id/athletes',
  },

  // Auth endpoints
  AUTH: {
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    VERIFY: '/api/auth/verify',
  },
};

// Local Storage Keys
export const LOCAL_STORAGE_KEYS = {
  AUTH_TOKEN: 'moove_auth_token',
  USER_PROFILE: 'moove_user_profile',
  THEME: 'moove_theme',
  LANGUAGE: 'moove_language',
  LAST_ATHLETE_ID: 'moove_last_athlete_id',
};

// Regular Expressions
export const REGEX = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PASSWORD: /^(?=.*[A-Z])(?=.*[0-9])(?=.{8,})/, // Min 8 chars, 1 uppercase, 1 number
  PHONE_NUMBER: /^[\d\s\-\+\(\)]+$/,
  URL: /^https?:\/\/.+/,
};

// Animation Durations (milliseconds)
export const ANIMATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
  VERY_SLOW: 1000,
};

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 20,
  MAX_LIMIT: 100,
};

// Features (for feature flags)
export const FEATURES = {
  ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  ENABLE_BETA_FEATURES: import.meta.env.VITE_ENABLE_BETA_FEATURES === 'true',
  ENABLE_OFFLINE_MODE: import.meta.env.VITE_ENABLE_OFFLINE_MODE === 'true',
};

// Environment Checks
export const ENV = {
  isDev: import.meta.env.VITE_ENV === 'development',
  isProd: import.meta.env.VITE_ENV === 'production',
  isStaging: import.meta.env.VITE_ENV === 'staging',
};

// Messages
export const MESSAGES = {
  UPLOAD_SUCCESS: 'Video uploaded successfully!',
  UPLOAD_ERROR: 'Failed to upload video. Please try again.',
  PROCESS_SUCCESS: 'Video processing started.',
  PROCESS_ERROR: 'Failed to start processing.',
  DELETE_CONFIRM: 'Are you sure you want to delete this item?',
  DELETE_SUCCESS: 'Deleted successfully.',
  SAVE_SUCCESS: 'Saved successfully!',
  SAVE_ERROR: 'Failed to save. Please try again.',
};

export default {
  APP_CONFIG,
  API_CONFIG,
  FILE_SIZES,
  VALID_FILE_TYPES,
  USER_ROLES,
  USER_STATUS,
  VIDEO_STATUS,
  HTTP_STATUS,
  TIMEOUTS,
  API_ENDPOINTS,
  LOCAL_STORAGE_KEYS,
  REGEX,
  ANIMATION,
  FEATURES,
  ENV,
  MESSAGES,
};
