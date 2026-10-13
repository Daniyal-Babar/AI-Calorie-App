const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export function getAuthToken() {
  return localStorage.getItem('nutri_token');
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('nutri_token', token);
  } else {
    localStorage.removeItem('nutri_token');
  }
}

export async function request(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const config = {
    ...options,
    headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, config);

  if (response.status === 401) {
    // Clear token if expired or unauthorized
    setAuthToken(null);
  }

  const contentType = response.headers.get('content-type') || '';
  let data = null;
  if (contentType.includes('application/json')) {
    data = await response.json();
  }

  if (!response.ok) {
    const errorMsg = data?.error || `HTTP error! Status: ${response.status}`;
    const err = new Error(errorMsg);
    err.status = response.status;
    err.details = data?.details;
    throw err;
  }

  return data;
}

export { API_BASE };
