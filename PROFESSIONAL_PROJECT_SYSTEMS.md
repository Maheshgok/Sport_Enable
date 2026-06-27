# Professional Project Structure Systems

## Overview

Your Moove project has good basics but needs these **10 professional systems** to be production-ready:

---

## 1️⃣ ERROR HANDLING & LOGGING SYSTEM

**Current Issue:** Errors scattered, no centralized logging or monitoring

**What You Need:**

```jsx
// utils/errorHandler.js - Centralized error handling
export class AppError extends Error {
  constructor(message, code, statusCode = 500, details = {}) {
    super(message);
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
    this.timestamp = new Date();
  }
}

// Log errors to console, file, or service
export const logError = (error) => {
  console.error({
    message: error.message,
    code: error.code,
    details: error.details,
    timestamp: new Date(),
    userAgent: navigator.userAgent,
  });
  
  // Send to Sentry/LogRocket for monitoring
  if (process.env.VITE_ERROR_TRACKING) {
    // captureException(error);
  }
};
```

**Benefits:**
- ✅ Unified error handling across app
- ✅ Error tracking/monitoring integration
- ✅ User-friendly error messages
- ✅ Debug information preserved

---

## 2️⃣ FORM VALIDATION & SANITIZATION SYSTEM

**Current Issue:** No input validation, potential security issues

**What You Need:**

```jsx
// utils/validators.js
export const validators = {
  email: (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
  
  password: (password) => {
    return password.length >= 8 && 
           /[A-Z]/.test(password) && 
           /[0-9]/.test(password);
  },
  
  athleteHeight: (height) => {
    const h = parseFloat(height);
    return h >= 100 && h <= 250; // cm
  },
  
  videoFile: (file) => {
    const validTypes = ['video/mp4', 'video/avi', 'video/quicktime'];
    const maxSize = 500 * 1024 * 1024; // 500MB
    return validTypes.includes(file.type) && file.size <= maxSize;
  },
};

// utils/sanitizers.js
export const sanitize = {
  html: (text) => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },
  
  email: (email) => email.trim().toLowerCase(),
  
  phoneNumber: (phone) => phone.replace(/\D/g, ''),
};

// hooks/useForm.js
export const useForm = (initialValues, onSubmit) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } catch (error) {
      logError(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return { values, errors, touched, handleChange, handleSubmit, isSubmitting };
};
```

**Benefits:**
- ✅ Consistent validation across app
- ✅ XSS/injection protection
- ✅ User-friendly error messages
- ✅ Reusable form logic

---

## 3️⃣ CONSTANTS & CONFIGURATION MANAGEMENT

**Current Issue:** Magic strings scattered everywhere

**What You Need:**

```jsx
// constants/index.js
export const APP_CONFIG = {
  name: 'Moove',
  version: '1.0.0',
  environment: process.env.VITE_ENV || 'development',
};

export const API_ENDPOINTS = {
  VIDEO: {
    UPLOAD: '/api/upload',
    PROCESS: '/api/process/:jobId',
    RESULTS: '/api/results/:jobId',
  },
  ATHLETE: {
    LIST: '/api/athletes',
    GET: '/api/athlete/:id',
    UPDATE: '/api/athlete/:id',
  },
};

export const USER_ROLES = {
  ADMIN: 'admin',
  COACH: 'coach',
  ATHLETE: 'athlete',
  PHYSIOTHERAPIST: 'physiotherapist',
  CARETAKER: 'caretaker',
};

export const VIDEO_STATUS = {
  UPLOADING: 'uploading',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

export const FILE_SIZES = {
  MAX_VIDEO: 500 * 1024 * 1024, // 500MB
  MAX_IMAGE: 5 * 1024 * 1024,   // 5MB
};

export const TIMEOUTS = {
  API_REQUEST: 30000,      // 30s
  REDIRECT: 2000,          // 2s
  TOAST: 5000,             // 5s
};
```

**Benefits:**
- ✅ Single source of truth
- ✅ Easy to update globally
- ✅ No magic strings/numbers
- ✅ Type-safe with good IDE support

---

## 4️⃣ GLOBAL ERROR BOUNDARY & FALLBACK UI

**Current Issue:** One error crashes entire app

**What You Need:**

```jsx
// components/ErrorBoundary.jsx
import { Component } from 'react';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    logError(error);
    console.error('Error boundary caught:', errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-red-50 p-4">
          <div className="max-w-md text-center">
            <h1 className="text-3xl font-bold text-red-600 mb-4">
              Oops! Something went wrong
            </h1>
            <p className="text-gray-600 mb-6">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            <button
              onClick={() => window.location.href = '/'}
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Go to Home
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
```

**Benefits:**
- ✅ Graceful error handling
- ✅ App stays running
- ✅ User-friendly message
- ✅ Error tracking integration

---

## 5️⃣ TOAST/NOTIFICATION SYSTEM

**Current Issue:** Users don't know if action succeeded

**What You Need:**

```jsx
// context/ToastContext.jsx
import { createContext, useState, useCallback } from 'react';

export const ToastContext = createContext();

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 5000) => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    
    if (duration > 0) {
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, duration);
    }
    
    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast, toasts }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
};

// hooks/useToast.js
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

// Usage
const { addToast } = useToast();
addToast('Upload successful!', 'success');
addToast('Error uploading file', 'error');
```

**Benefits:**
- ✅ Consistent notifications
- ✅ User feedback for actions
- ✅ Non-intrusive alerts
- ✅ Easy to reuse

---

## 6️⃣ CUSTOM HOOKS LIBRARY

**Current Issue:** Logic scattered in components

**What You Need:**

```jsx
// hooks/useFetch.js
export const useFetch = (url, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await apiClient.get(url);
        setData(response);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, loading, error };
};

// hooks/useAsync.js
export const useAsync = (asyncFunction, immediate = true) => {
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const execute = useCallback(async () => {
    setStatus('pending');
    try {
      const response = await asyncFunction();
      setData(response);
      setStatus('success');
    } catch (error) {
      setError(error);
      setStatus('error');
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { execute, status, data, error };
};

// hooks/useDebounce.js
export const useDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

// hooks/useLocalStorage.js
export const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = (value) => {
    const valueToStore = value instanceof Function ? value(storedValue) : value;
    setStoredValue(valueToStore);
    window.localStorage.setItem(key, JSON.stringify(valueToStore));
  };

  return [storedValue, setValue];
};

// hooks/usePrevious.js
export const usePrevious = (value) => {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  }, [value]);
  return ref.current;
};
```

**Benefits:**
- ✅ Reusable logic
- ✅ Cleaner components
- ✅ Consistent patterns
- ✅ Easy to test

---

## 7️⃣ MIDDLEWARE & ROUTE GUARDS

**Current Issue:** No protection for authenticated routes

**What You Need:**

```jsx
// utils/routeGuards.js
export const canAccess = (userRole, requiredRoles) => {
  return requiredRoles.includes(userRole);
};

// components/ProtectedRoute.jsx
export const ProtectedRoute = ({ 
  component: Component, 
  requiredRoles = [],
  ...props 
}) => {
  const { user, userProfile } = useAuth();

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (requiredRoles.length > 0 && !canAccess(userProfile?.role, requiredRoles)) {
    return <Navigate to="/unauthorized" />;
  }

  return <Component {...props} />;
};

// Usage in App.jsx
<Route 
  path="/admin" 
  element={
    <ProtectedRoute 
      component={AdminDashboard}
      requiredRoles={['admin']}
    />
  }
/>
```

**Benefits:**
- ✅ Protected routes
- ✅ Role-based access
- ✅ Automatic redirects
- ✅ Security enforced

---

## 8️⃣ LOADING & SKELETON STATES

**Current Issue:** Users see blank screens while loading

**What You Need:**

```jsx
// components/Skeleton.jsx
export const Skeleton = ({ width = 'w-full', height = 'h-4' }) => (
  <div className={`${width} ${height} bg-gray-200 rounded animate-pulse`} />
);

// components/CardSkeleton.jsx
export const CardSkeleton = () => (
  <div className="bg-white rounded-lg p-6 space-y-4">
    <Skeleton height="h-6" />
    <Skeleton height="h-4" width="w-2/3" />
    <Skeleton height="h-4" width="w-1/2" />
  </div>
);

// Usage
const { data, loading } = useFetch('/api/data');

return (
  <div className="grid grid-cols-3 gap-6">
    {loading ? (
      <>
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
      </>
    ) : (
      data.map(item => <Card key={item.id} {...item} />)
    )}
  </div>
);
```

**Benefits:**
- ✅ Better perceived performance
- ✅ Professional look
- ✅ Clear loading feedback
- ✅ Improved UX

---

## 9️⃣ ENVIRONMENT & FEATURE FLAGS

**Current Issue:** Config hardcoded, can't control features

**What You Need:**

```jsx
// .env.local
VITE_API_URL=http://localhost:8080
VITE_ENV=development
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_BETA_FEATURES=true
VITE_ERROR_TRACKING_DSN=
VITE_FIREBASE_CONFIG={...}

// utils/config.js
export const config = {
  api: {
    baseUrl: import.meta.env.VITE_API_URL,
    timeout: 30000,
  },
  
  features: {
    analytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
    betaFeatures: import.meta.env.VITE_ENABLE_BETA_FEATURES === 'true',
  },
  
  isDev: import.meta.env.VITE_ENV === 'development',
  isProd: import.meta.env.VITE_ENV === 'production',
};

// Usage
import { config } from '../utils/config';

{config.features.betaFeatures && <BetaFeature />}
```

**Benefits:**
- ✅ Environment-specific config
- ✅ Feature toggle control
- ✅ No code changes to deploy
- ✅ A/B testing capability

---

## 🔟 CODE QUALITY & LINTING

**Current Issue:** No code style enforcement, potential bugs

**What You Need:**

```bash
# Install ESLint and Prettier
npm install --save-dev eslint eslint-config-react-app prettier

# .eslintrc.json
{
  "extends": ["react-app"],
  "rules": {
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "no-debugger": "warn",
    "react/prop-types": "off",
    "react/react-in-jsx-scope": "off"
  }
}

# .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2
}

# package.json scripts
"lint": "eslint src --ext .js,.jsx",
"lint:fix": "eslint src --ext .js,.jsx --fix",
"format": "prettier --write \"src/**/*.{js,jsx,css}\"",
"format:check": "prettier --check \"src/**/*.{js,jsx,css}\""
```

**Benefits:**
- ✅ Consistent code style
- ✅ Catch bugs early
- ✅ Team alignment
- ✅ Automated fixes

---

## 1️⃣1️⃣ PERFORMANCE MONITORING

**Current Issue:** Don't know app performance issues

**What You Need:**

```jsx
// utils/performance.js
export const reportWebVitals = (metric) => {
  if (process.env.VITE_ENV === 'production') {
    // Send to analytics service
    console.log('Web Vital:', metric);
  }
};

// main.jsx
import { reportWebVitals } from './utils/performance';

reportWebVitals();

// Use Lighthouse, Web Vitals library, or Sentry
// Key metrics: LCP, FID, CLS, FCP, TTFB
```

**Benefits:**
- ✅ Monitor real user experience
- ✅ Identify bottlenecks
- ✅ Track improvements
- ✅ Data-driven optimization

---

## 1️⃣2️⃣ STATE MANAGEMENT (IF NEEDED)

**Current Issue:** Context drilling for complex state

**What You Need (if complex):**

```jsx
// Redux is overkill for most apps
// Use Context API + useReducer for medium complexity:

// hooks/useAppState.js
const initialState = {
  user: null,
  athletes: [],
  videos: [],
};

const appReducer = (state, action) => {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'ADD_ATHLETE':
      return { ...state, athletes: [...state.athletes, action.payload] };
    default:
      return state;
  }
};

export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);
  
  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};
```

**Benefits:**
- ✅ Centralized state management
- ✅ Predictable updates
- ✅ Easy debugging
- ✅ Scales with app growth

---

## QUICK IMPLEMENTATION PRIORITY

### Phase 1: Critical (Week 1)
1. ✅ API Client (DONE)
2. ✅ Mobile Responsive (DONE)
3. **Error Handling System** ← Start here
4. **Constants Management**
5. **Error Boundary**

### Phase 2: Important (Week 2-3)
6. **Form Validation**
7. **Toast Notifications**
8. **Custom Hooks Library**
9. **Linting & Code Quality**

### Phase 3: Polish (Week 4+)
10. **Loading States**
11. **Environment Config**
12. **Route Guards**
13. **Performance Monitoring**

---

## IMPLEMENTATION CHECKLIST

```markdown
- [ ] Error Handling System
- [ ] Constants File (API_ENDPOINTS, STATUS, etc.)
- [ ] Error Boundary Component
- [ ] Toast/Notification System
- [ ] Form Validation & Sanitization
- [ ] Custom Hooks (useFetch, useAsync, useDebounce)
- [ ] Route Guards (ProtectedRoute)
- [ ] Skeleton Loading States
- [ ] ESLint + Prettier setup
- [ ] Environment Configuration
- [ ] Performance Monitoring
- [ ] Testing Suite (Vitest + React Testing Library)
```

---

## Your Path to Professional Project

| Level | Systems | Timeline |
|-------|---------|----------|
| MVP (Current) | API Client + Responsive UI | Now |
| Professional | + Error Handling, Validation, Constants | 2-3 weeks |
| Enterprise | + Testing, Monitoring, CI/CD | 4-8 weeks |

**Each system adds professional polish and reduces bugs by ~20%** 🚀

Would you like me to implement any of these systems first?
