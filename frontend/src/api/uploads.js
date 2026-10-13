import { API_BASE, getAuthToken } from './client';

export async function uploadImageApi(file) {
  const token = getAuthToken();
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/uploads`, {
    method: 'POST',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: formData,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.error || 'Image upload failed');
  }

  return data;
}
