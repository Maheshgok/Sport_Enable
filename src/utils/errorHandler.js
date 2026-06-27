/**
 * Centralized Error Handling System
 * Handle all errors consistently across the app
 */

// Custom Error Class
export class AppError extends Error {
  constructor(message, code, statusCode = 500, details = {}) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
    this.timestamp = new Date();
  }

  toJSON() {
    return {
      message: this.message,
      code: this.code,
      statusCode: this.statusCode,
      details: this.details,
      timestamp: this.timestamp,
    };
  }
}

// Error Logger
class ErrorLogger {
  constructor() {
    this.isDev = import.meta.env.VITE_ENV === 'development';
    this.listeners = [];
  }

  subscribe(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback);
    };
  }

  notify(error) {
    this.listeners.forEach(listener => listener(error));
  }

  log(error) {
    // Format error for logging
    const errorLog = {
      message: error.message,
      code: error.code || 'UNKNOWN',
      statusCode: error.statusCode || 500,
      details: error.details || {},
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      stack: error.stack,
    };

    // Console logging (always in dev)
    if (this.isDev) {
      console.error('❌ Error Log:', errorLog);
    }

    // Send to error tracking service
    this.sendToRemote(errorLog);

    // Notify listeners (for UI toasts, etc.)
    this.notify(error);
  }

  logWarning(message, code = 'WARNING') {
    const warningLog = {
      level: 'warning',
      message,
      code,
      timestamp: new Date().toISOString(),
    };

    if (this.isDev) {
      console.warn('⚠️ Warning:', warningLog);
    }
  }

  logInfo(message, data = {}) {
    if (this.isDev) {
      console.log('ℹ️ Info:', { message, data });
    }
  }

  async sendToRemote(errorLog) {
    // If using Sentry, LogRocket, or other error tracking:
    // try {
    //   await fetch('https://your-error-tracking-service.com/log', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify(errorLog),
    //   });
    // } catch (err) {
    //   console.error('Failed to send error log to remote:', err);
    // }
  }
}

export const errorLogger = new ErrorLogger();

// Helper to create errors
export const createError = (message, code, statusCode = 500, details = {}) => {
  return new AppError(message, code, statusCode, details);
};

// Error codes for consistency
export const ERROR_CODES = {
  // Network errors
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT',
  API_ERROR: 'API_ERROR',

  // Auth errors
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',

  // Validation errors
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_FILE: 'INVALID_FILE',
  INVALID_INPUT: 'INVALID_INPUT',

  // Video errors
  VIDEO_UPLOAD_FAILED: 'VIDEO_UPLOAD_FAILED',
  VIDEO_PROCESS_FAILED: 'VIDEO_PROCESS_FAILED',
  VIDEO_NOT_FOUND: 'VIDEO_NOT_FOUND',

  // Firebase errors
  FIREBASE_ERROR: 'FIREBASE_ERROR',
  AUTH_ERROR: 'AUTH_ERROR',

  // Generic
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
};

// Error messages for users
export const ERROR_MESSAGES = {
  [ERROR_CODES.NETWORK_ERROR]: 'Network error. Please check your connection.',
  [ERROR_CODES.TIMEOUT]: 'Request timed out. Please try again.',
  [ERROR_CODES.UNAUTHORIZED]: 'You are not authorized. Please log in.',
  [ERROR_CODES.FORBIDDEN]: 'You do not have permission to access this.',
  [ERROR_CODES.NOT_FOUND]: 'Resource not found.',
  [ERROR_CODES.VALIDATION_ERROR]: 'Invalid input. Please check your data.',
  [ERROR_CODES.INVALID_FILE]: 'Invalid file format or size.',
  [ERROR_CODES.VIDEO_UPLOAD_FAILED]: 'Failed to upload video. Please try again.',
  [ERROR_CODES.VIDEO_PROCESS_FAILED]: 'Failed to process video. Please try again.',
  [ERROR_CODES.SERVER_ERROR]: 'Server error. Please try again later.',
  [ERROR_CODES.UNKNOWN_ERROR]: 'An unexpected error occurred.',
};

// Get user-friendly message
export const getUserMessage = (errorCode, customMessage = null) => {
  return customMessage || ERROR_MESSAGES[errorCode] || ERROR_MESSAGES[ERROR_CODES.UNKNOWN_ERROR];
};

// Hook to use error logging
export const useErrorHandler = () => {
  return {
    handle: (error) => {
      if (error instanceof AppError) {
        errorLogger.log(error);
      } else {
        const appError = new AppError(
          error.message || 'An unexpected error occurred',
          ERROR_CODES.UNKNOWN_ERROR,
          500,
          error
        );
        errorLogger.log(appError);
      }
    },

    createAndLog: (message, code, statusCode = 500, details = {}) => {
      const error = createError(message, code, statusCode, details);
      errorLogger.log(error);
      return error;
    },

    warn: (message, code = 'WARNING') => {
      errorLogger.logWarning(message, code);
    },

    info: (message, data = {}) => {
      errorLogger.logInfo(message, data);
    },
  };
};

export default errorLogger;
