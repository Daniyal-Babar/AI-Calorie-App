import { request, setAuthToken } from './client';

export async function loginApi(credentials) {
  const data = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
  if (data?.token) {
    setAuthToken(data.token);
  }
  return data;
}

export async function registerApi(userData) {
  const data = await request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  });
  if (data?.token) {
    setAuthToken(data.token);
  }
  return data;
}

export async function getMeApi() {
  return await request('/auth/me', { method: 'GET' });
}

export async function updateProfileApi(profileData) {
  return await request('/auth/profile', {
    method: 'PUT',
    body: JSON.stringify(profileData),
  });
}

export async function logoutApi() {
  try {
    await request('/auth/logout', { method: 'POST' });
  } catch {
    // Ignore error on logout
  } finally {
    setAuthToken(null);
  }
}
