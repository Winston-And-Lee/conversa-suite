/**
 * API client for making requests to the backend with proper CORS and referrer policy
 */

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

// Custom fetch with proper headers
export async function apiFetch(
  endpoint: string, 
  options: RequestInit = {}
): Promise<Response> {
  const url = endpoint.startsWith('http') ? endpoint : `${backendUrl}${endpoint}`;
  
  const fetchOptions: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    credentials: 'include',
    mode: 'cors',
  };
  
  return fetch(url, fetchOptions);
}

// API client for assistant
export const assistantApi = {
  // Create a new thread
  createThread: async (systemMessage?: string, assistantId?: string) => {
    const response = await apiFetch('/api/assistant/assistant/threads', {
      method: 'POST',
      body: JSON.stringify({ 
        system_message: systemMessage,
        assistant_id: assistantId
      }),
    });
    return response.json();
  },
  
  // Send a message to a thread
  sendMessage: async (threadId: string, content: string, stream: boolean = false) => {
    const response = await apiFetch(`/api/assistant/assistant/threads/${threadId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content, stream }),
    });
    return response.json();
  },
  
  // Stream a message to a thread
  streamMessage: (threadId: string, content: string) => {
    return apiFetch(`/api/assistant/assistant/threads/${threadId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content, stream: true }),
    });
  },
  
  // Get messages from a thread
  getThreadMessages: async (threadId: string) => {
    const response = await apiFetch(`/api/assistant/assistant/threads/${threadId}/messages`);
    return response.json();
  },
  
  // Delete a thread
  deleteThread: async (threadId: string) => {
    const response = await apiFetch(`/api/assistant/assistant/threads/${threadId}`, {
      method: 'DELETE',
    });
    return response.json();
  },
};

// API client for assistant-ui
export const assistantUiApi = {
  // Send a chat request
  chat: (request: any) => {
    return apiFetch('/api/assistant-ui/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },
}; 