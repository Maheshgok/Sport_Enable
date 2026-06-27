/**
 * Toast Notification System
 * Provides global notifications for success, error, warning, info
 */

import { createContext, useContext, useState, useCallback } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

// Create context
const ToastContext = createContext();

// Toast Provider Component
export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 5000, id = null) => {
    const toastId = id || Date.now().toString();
    const newToast = {
      id: toastId,
      message,
      type, // 'success', 'error', 'warning', 'info'
      createdAt: Date.now(),
    };

    setToasts(prev => [...prev, newToast]);

    // Auto remove after duration
    if (duration > 0) {
      setTimeout(() => {
        removeToast(toastId);
      }, duration);
    }

    return toastId;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const success = useCallback(
    (message, duration = 5000) => addToast(message, 'success', duration),
    [addToast]
  );

  const error = useCallback(
    (message, duration = 5000) => addToast(message, 'error', duration),
    [addToast]
  );

  const warning = useCallback(
    (message, duration = 5000) => addToast(message, 'warning', duration),
    [addToast]
  );

  const info = useCallback(
    (message, duration = 5000) => addToast(message, 'info', duration),
    [addToast]
  );

  const value = {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    warning,
    info,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
};

// Hook to use toasts
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

// Toast Container Component
const ToastContainer = ({ toasts, onRemove }) => {
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-3 pointer-events-none">
      {toasts.map(toast => (
        <Toast
          key={toast.id}
          toast={toast}
          onRemove={() => onRemove(toast.id)}
        />
      ))}
    </div>
  );
};

// Individual Toast Component
const Toast = ({ toast, onRemove }) => {
  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5" />;
      case 'error':
        return <AlertCircle className="w-5 h-5" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />;
      case 'info':
        return <Info className="w-5 h-5" />;
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  const getStyles = (type) => {
    switch (type) {
      case 'success':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          icon: 'text-green-600',
          text: 'text-green-900',
        };
      case 'error':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: 'text-red-600',
          text: 'text-red-900',
        };
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: 'text-yellow-600',
          text: 'text-yellow-900',
        };
      case 'info':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          icon: 'text-blue-600',
          text: 'text-blue-900',
        };
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          icon: 'text-gray-600',
          text: 'text-gray-900',
        };
    }
  };

  const styles = getStyles(toast.type);

  return (
    <div
      className={`
        ${styles.bg} 
        ${styles.border} 
        border 
        rounded-lg 
        shadow-lg 
        p-4 
        flex 
        items-start 
        gap-3 
        max-w-sm 
        w-full 
        pointer-events-auto
        animate-in 
        slide-in-from-right-5 
        fade-in-0 
        duration-200
      `}
    >
      {/* Icon */}
      <div className={`flex-shrink-0 mt-0.5 ${styles.icon}`}>
        {getIcon(toast.type)}
      </div>

      {/* Message */}
      <div className={`flex-1 ${styles.text} text-sm font-medium`}>
        {toast.message}
      </div>

      {/* Close Button */}
      <button
        onClick={onRemove}
        className={`flex-shrink-0 ${styles.icon} hover:opacity-70 transition-opacity`}
      >
        <X className="w-5 h-5" />
      </button>
    </div>
  );
};

export default ToastProvider;
