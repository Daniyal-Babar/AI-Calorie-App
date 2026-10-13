import { API_BASE, getAuthToken, request } from './client';

export async function fetchChatHistory(conversationId = null) {
  const url = conversationId ? `/chat/history?conversation_id=${conversationId}` : '/chat/history';
  return await request(url, { method: 'GET' });
}

export async function confirmActionApi(actionId, conversationId, confirmed) {
  return await request('/chat/confirm', {
    method: 'POST',
    body: JSON.stringify({
      action_id: actionId,
      conversation_id: conversationId,
      confirmed: Boolean(confirmed),
    }),
  });
}

export async function streamChatMessage({
  message,
  conversationId,
  imageId,
  onStatus,
  onToolCall,
  onToolResult,
  onToken,
  onDone,
  onError,
}) {
  const token = getAuthToken();

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        image_id: imageId,
      }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || `HTTP error! Status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data: ')) {
          try {
            const payload = JSON.parse(trimmed.slice(6));
            if (payload.event === 'status' && onStatus) {
              onStatus(payload);
            } else if (payload.event === 'tool_call' && onToolCall) {
              onToolCall(payload);
            } else if (payload.event === 'tool_result' && onToolResult) {
              onToolResult(payload);
            } else if (payload.event === 'token' && onToken) {
              onToken(payload.token);
            } else if (payload.event === 'done' && onDone) {
              onDone(payload);
            }
          } catch (e) {
            console.error('SSE JSON parse error:', e, trimmed);
          }
        }
      }
    }
  } catch (err) {
    if (onError) onError(err);
    else throw err;
  }
}
