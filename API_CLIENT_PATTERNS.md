# API Client - Quick Reference

## Common Patterns

### Pattern 1: Simple Data Fetching

```jsx
import { useState, useEffect } from 'react';
import { apiClient, APIError } from '../utils/apiClient';

function MyComponent({ id }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await apiClient.get(`/api/resource/${id}`);
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  return <div>{JSON.stringify(data)}</div>;
}
```

### Pattern 2: Form Submission

```jsx
import { useState } from 'react';
import { apiClient, APIError } from '../utils/apiClient';

function MyForm() {
  const [formData, setFormData] = useState({ name: '', email: '' });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    
    try {
      const response = await apiClient.post('/api/submit', formData);
      setMessage('Success! ' + response.message);
      setFormData({ name: '', email: '' });
    } catch (error) {
      setMessage('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="text" 
        value={formData.name} 
        onChange={(e) => setFormData({...formData, name: e.target.value})}
      />
      <button disabled={loading}>
        {loading ? 'Submitting...' : 'Submit'}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
}
```

### Pattern 3: File Upload with Progress

```jsx
import { useState } from 'react';
import { apiClient, APIError } from '../utils/apiClient';

function FileUpload() {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('idle'); // idle, uploading, done, error

  const handleUpload = async (e) => {
    const uploadFile = e.target.files[0];
    if (!uploadFile) return;

    setFile(uploadFile);
    setProgress(0);
    setStatus('uploading');

    try {
      const formData = new FormData();
      formData.append('file', uploadFile);

      const response = await apiClient.upload('/api/upload', formData, (progress) => {
        setProgress(progress);
      });

      setStatus('done');
      console.log('Upload complete:', response);
    } catch (error) {
      setStatus('error');
      console.error('Upload failed:', error.message);
    }
  };

  return (
    <div>
      <input 
        type="file" 
        onChange={handleUpload}
        disabled={status === 'uploading'}
      />
      {status === 'uploading' && (
        <div>
          <progress value={progress} max={100}></progress>
          <span>{progress}%</span>
        </div>
      )}
      {status === 'done' && <p>Upload complete!</p>}
      {status === 'error' && <p>Upload failed!</p>}
    </div>
  );
}
```

### Pattern 4: Custom Hook for API Calls

```jsx
// hooks/useApi.js
import { useState, useCallback } from 'react';
import { apiClient, APIError } from '../utils/apiClient';

export const useApi = (apiMethod) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);
      try {
        const result = await apiMethod(...args);
        setData(result);
        return result;
      } catch (err) {
        const errorMessage = err instanceof APIError ? err.message : 'Unknown error';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiMethod]
  );

  return { data, loading, error, execute };
};

// Usage
import { videoAPI } from '../utils/apiClient';

function VideoUpload() {
  const { loading, error, execute } = useApi((formData, onProgress) => 
    videoAPI.upload(formData, onProgress)
  );

  const handleUpload = async () => {
    try {
      const result = await execute(formData, setProgress);
      console.log('Done:', result);
    } catch (err) {
      console.error('Failed');
    }
  };

  return (
    <div>
      <button onClick={handleUpload} disabled={loading}>
        {loading ? 'Uploading...' : 'Upload'}
      </button>
      {error && <p>Error: {error}</p>}
    </div>
  );
}
```

### Pattern 5: Retry with Exponential Backoff

```jsx
// hooks/useApiWithRetry.js
import { useState, useCallback } from 'react';
import { apiClient, APIError } from '../utils/apiClient';

export const useApiWithRetry = (apiMethod, maxRetries = 3) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const execute = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);

      for (let i = 0; i <= maxRetries; i++) {
        try {
          const result = await apiMethod(...args);
          setData(result);
          setRetryCount(0);
          return result;
        } catch (err) {
          if (i === maxRetries) {
            setError(err.message);
            setRetryCount(i + 1);
            throw err;
          }
          // Wait before retry (exponential backoff)
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
        }
      }
    },
    [apiMethod, maxRetries]
  );

  return { data, loading, error, retryCount, execute };
};
```

### Pattern 6: Parallel Requests

```jsx
import { useState, useEffect } from 'react';
import { apiClient } from '../utils/apiClient';

function Dashboard() {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAllData = async () => {
      try {
        // Make multiple requests in parallel
        const [profile, analytics, history] = await Promise.all([
          apiClient.get('/api/profile'),
          apiClient.get('/api/analytics'),
          apiClient.get('/api/history'),
        ]);

        setData({ profile, analytics, history });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>{data.profile.name}</h1>
      <p>{data.analytics.score}</p>
    </div>
  );
}
```

### Pattern 7: Sequential Requests (Dependent)

```jsx
import { useState } from 'react';
import { apiClient } from '../utils/apiClient';

function DependentRequests() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFetch = async () => {
    setLoading(true);
    try {
      // Step 1: Get athlete ID
      const athleteList = await apiClient.get('/api/athletes');
      const athleteId = athleteList.athletes[0].id;

      // Step 2: Get athlete details using ID from step 1
      const athleteDetails = await apiClient.get(`/api/athlete/${athleteId}`);

      // Step 3: Get analytics for that athlete
      const analytics = await apiClient.get(`/api/athlete/${athleteId}/analytics`);

      setResult({ athleteDetails, analytics });
    } catch (err) {
      console.error('Error:', err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleFetch} disabled={loading}>
        {loading ? 'Loading...' : 'Fetch'}
      </button>
      {result && <div>{JSON.stringify(result)}</div>}
    </div>
  );
}
```

### Pattern 8: Polling Data

```jsx
import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../utils/apiClient';

function PollingComponent({ jobId }) {
  const [status, setStatus] = useState('pending');
  const [data, setData] = useState(null);
  const pollIntervalRef = useRef(null);

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await apiClient.get(`/api/job/${jobId}`);
        
        if (response.status === 'completed') {
          setStatus('completed');
          setData(response.data);
          clearInterval(pollIntervalRef.current);
        } else if (response.status === 'failed') {
          setStatus('failed');
          clearInterval(pollIntervalRef.current);
        } else {
          setStatus(response.status); // 'processing', etc.
        }
      } catch (err) {
        console.error('Poll error:', err.message);
      }
    };

    // Poll every 2 seconds
    pollIntervalRef.current = setInterval(pollStatus, 2000);

    return () => clearInterval(pollIntervalRef.current);
  }, [jobId]);

  return (
    <div>
      <p>Status: {status}</p>
      {data && <p>Result: {JSON.stringify(data)}</p>}
    </div>
  );
}
```

### Pattern 9: Request Cancellation

```jsx
import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../utils/apiClient';

function CancellableRequest({ url }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const controllerRef = useRef(new AbortController());

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(url, {
          signal: controllerRef.current.signal,
        });
        const json = await response.json();
        setData(json);
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Fetch error:', err);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    return () => {
      // Cancel request on unmount
      controllerRef.current.abort();
    };
  }, [url]);

  return (
    <div>
      {loading ? 'Loading...' : JSON.stringify(data)}
    </div>
  );
}
```

### Pattern 10: Error Boundary with API

```jsx
import { useState } from 'react';
import { apiClient, APIError } from '../utils/apiClient';

function SafeApiCall() {
  const [error, setError] = useState(null);

  const handleApiCall = async () => {
    try {
      const data = await apiClient.get('/api/data');
      console.log('Success:', data);
    } catch (err) {
      if (err instanceof APIError) {
        if (err.status === 401) {
          // Handle unauthorized
          setError('Please log in');
        } else if (err.status === 404) {
          // Handle not found
          setError('Resource not found');
        } else if (err.status >= 500) {
          // Handle server error
          setError('Server error, please try again later');
        } else {
          setError(`Error: ${err.message}`);
        }
      } else {
        setError('Unknown error occurred');
      }
    }
  };

  return (
    <div>
      <button onClick={handleApiCall}>Call API</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}
```

---

## Summary

| Pattern | Use Case |
|---------|----------|
| Pattern 1 | Simple data fetching with loading/error states |
| Pattern 2 | Form submissions |
| Pattern 3 | File uploads with progress tracking |
| Pattern 4 | Reusable hook for any API method |
| Pattern 5 | Automatic retries with backoff |
| Pattern 6 | Multiple parallel requests |
| Pattern 7 | Sequential requests with dependencies |
| Pattern 8 | Polling for job status |
| Pattern 9 | Cancelable requests |
| Pattern 10 | Error handling and recovery |

Choose the pattern that fits your use case! 🚀
