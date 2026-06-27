# API Helper Client - Usage Guide

## Overview

The `apiClient` is a centralized HTTP client for all API requests in Moove. It provides:

- ✅ Error handling & retries
- ✅ Authentication token injection
- ✅ Request/response interceptors
- ✅ File upload with progress tracking
- ✅ Timeout handling
- ✅ Automatic retries for network errors

## Quick Start

### Basic GET Request

```jsx
import { apiClient } from '../utils/apiClient';

// Simple GET
const data = await apiClient.get('/api/athlete/123');
console.log(data); // Response data
```

### Basic POST Request

```jsx
import { apiClient } from '../utils/apiClient';

// POST with data
const result = await apiClient.post('/api/create', {
  name: 'John Doe',
  age: 25
});
```

### File Upload with Progress

```jsx
import { videoAPI } from '../utils/apiClient';

const formData = new FormData();
formData.append('video', videoFile);
formData.append('height', athleteHeight);

const result = await videoAPI.upload(
  formData,
  (progress) => {
    console.log(`Upload: ${progress}%`);
    setUploadProgress(progress);
  }
);

console.log(result.job_id); // Job ID from response
```

## Video Analysis API

Pre-built endpoints for video analysis:

### Upload Video

```jsx
import { videoAPI } from '../utils/apiClient';

const formData = new FormData();
formData.append('front_video', frontVideoFile);
formData.append('side_video', sideVideoFile);
formData.append('athlete_height', heightInCm);

try {
  const response = await videoAPI.upload(formData, (progress) => {
    setUploadProgress(progress); // 0-100
  });
  
  const jobId = response.job_id;
  setJobId(jobId);
} catch (error) {
  console.error('Upload failed:', error.message);
}
```

### Start Processing

```jsx
import { videoAPI } from '../utils/apiClient';

try {
  await videoAPI.process(jobId);
  setStatus('processing');
} catch (error) {
  console.error('Processing failed:', error.message);
}
```

### Get Results

```jsx
import { videoAPI } from '../utils/apiClient';

try {
  const data = await videoAPI.getResults(jobId);
  setResults(data.files);
} catch (error) {
  console.error('Failed to fetch results:', error.message);
}
```

### Get Analysis Data

```jsx
import { videoAPI } from '../utils/apiClient';

try {
  const analysisData = await videoAPI.getAnalysisData(jobId);
  setAnalysisData(analysisData);
} catch (error) {
  console.error('Failed to fetch analysis:', error.message);
}
```

### Get Summary Report

```jsx
import { videoAPI } from '../utils/apiClient';

try {
  const report = await videoAPI.getSummaryReport(jobId);
  setSummaryReport(report);
} catch (error) {
  console.error('Failed to fetch report:', error.message);
}
```

### Download Report

```jsx
import { videoAPI } from '../utils/apiClient';

try {
  await videoAPI.downloadReport(jobId, 'athlete_report.pdf');
} catch (error) {
  console.error('Download failed:', error.message);
}
```

## Error Handling

All requests throw `APIError` on failure:

```jsx
import { apiClient, APIError } from '../utils/apiClient';

try {
  const data = await apiClient.get('/api/data');
} catch (error) {
  if (error instanceof APIError) {
    console.error(`Error ${error.status}: ${error.message}`);
    console.log('Error data:', error.data);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## Setup with Authentication

In your `main.jsx` or `App.jsx`, add the auth interceptor:

```jsx
import { setupAuthInterceptor, setupErrorInterceptor } from './utils/apiClient';
import { useAuth } from './context/AuthContext';

// In your app initialization
setupAuthInterceptor(async () => {
  // Get token from your auth context/provider
  const token = await getAuthToken(); // Your token getter
  return token;
});

setupErrorInterceptor(); // Optional: logs errors
```

Then all requests will automatically include the auth token:

```jsx
// This request will automatically include Bearer token
const data = await apiClient.get('/api/protected-endpoint');
```

## Before vs After

### ❌ Before (Scattered code)

```jsx
// In VideoAnalysisTool.jsx - code spread everywhere
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const handleUpload = async () => {
  const xhr = new XMLHttpRequest();
  xhr.open('POST', `${API_BASE_URL}/api/upload`);
  xhr.send(formData);
};

const handleProcess = async () => {
  const response = await fetch(`${API_BASE_URL}/api/process/${jobId}`, {
    method: 'POST'
  });
  const data = await response.json();
};

const fetchResults = async () => {
  const response = await fetch(`${API_BASE_URL}/api/results/${jobId}`);
  const data = await response.json();
};
```

### ✅ After (Centralized)

```jsx
// In VideoAnalysisTool.jsx - clean and simple
import { videoAPI } from '../utils/apiClient';

const handleUpload = async () => {
  const response = await videoAPI.upload(formData, setUploadProgress);
  setJobId(response.job_id);
};

const handleProcess = async () => {
  await videoAPI.process(jobId);
};

const fetchResults = async () => {
  const data = await videoAPI.getResults(jobId);
  setResults(data.files);
};
```

## Custom API Endpoints

Create custom endpoint groups:

```jsx
// In utils/apiClient.js - add new endpoints

export const athleteAPI = {
  getProfile: (athleteId) => {
    return apiClient.get(`/api/athlete/${athleteId}`);
  },

  updateProfile: (athleteId, data) => {
    return apiClient.put(`/api/athlete/${athleteId}`, data);
  },

  getHistory: (athleteId) => {
    return apiClient.get(`/api/athlete/${athleteId}/history`);
  },
};
```

Then use it:

```jsx
import { athleteAPI } from '../utils/apiClient';

const profile = await athleteAPI.getProfile(123);
await athleteAPI.updateProfile(123, { name: 'New Name' });
```

## Features

### Automatic Retries

Network errors automatically retry up to 3 times with exponential backoff:

```
Retry 1: After 1s
Retry 2: After 2s
Retry 3: After 3s
```

### Request Timeout

All requests timeout after 30 seconds. No hanging requests.

### Interceptors

Add custom logic before/after every request:

```jsx
import { addRequestInterceptor, addResponseInterceptor } from '../utils/apiClient';

// Log all requests
addRequestInterceptor((options) => {
  console.log('API Request:', options);
  return options;
});

// Log all responses
addResponseInterceptor((response) => {
  console.log('API Response:', response.status);
  return response;
});
```

## Environment Configuration

Set API URL in `.env`:

```env
VITE_API_URL=http://localhost:8080
```

Or for production:

```env
VITE_API_URL=https://api.moove.ai
```

The client automatically uses `import.meta.env.VITE_API_URL`.

## Migration Guide

To migrate existing code to use `apiClient`:

1. **Find all `fetch()` calls in your components**
2. **Replace with `apiClient` equivalents**
3. **Remove error handling boilerplate** (client handles it)
4. **Remove loading state management** (consider custom hook)

Example migration:

```jsx
// ❌ Old
const response = await fetch(`${API_BASE_URL}/api/data`, {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' }
});
const data = await response.json();

// ✅ New
const data = await apiClient.get('/api/data');
```

## Type Safety (TypeScript)

If using TypeScript, add types:

```typescript
import { apiClient, APIError } from '../utils/apiClient';

interface VideoUploadResponse {
  job_id: string;
  status: string;
}

try {
  const response: VideoUploadResponse = await videoAPI.upload(
    formData,
    onProgress
  );
} catch (error) {
  if (error instanceof APIError) {
    console.error(`Error: ${error.status}`);
  }
}
```

## Testing

Mock the API client in your tests:

```javascript
import { vi } from 'vitest';
import { apiClient } from '../utils/apiClient';

vi.mock('../utils/apiClient', () => ({
  apiClient: {
    get: vi.fn().mockResolvedValue({ data: 'test' }),
    post: vi.fn().mockResolvedValue({ id: 1 }),
  }
}));
```

---

**That's it! Use `apiClient` for all HTTP requests and enjoy cleaner, more maintainable code.** 🚀
