import axios from 'axios';

// Create axios instance with base URL
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types based on backend entities
export interface ChatSession {
  session_id: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatHistory {
  messages: ChatMessage[];
}

// API functions
export const chatbotApi = {
  // Create a new chat session
  createSession: async (assistant_id?: string): Promise<ChatSession> => {
    const params = assistant_id ? { assistant_id } : {};
    const response = await apiClient.post('/api/chatbot/sessions', null, { params });
    return response.data;
  },

  // Send a message to the chatbot
  sendMessage: async (session_id: string, message: string): Promise<ChatMessage> => {
    const response = await apiClient.post(`/api/chatbot/sessions/${session_id}/messages`, {
      message,
    });
    
    // The backend returns a structure with { session_id, response, messages }
    // but we need to return a ChatMessage object
    return {
      role: 'assistant',
      content: response.data.response,
      timestamp: new Date().toISOString()
    };
  },

  // Get chat history for a session
  getChatHistory: async (session_id: string): Promise<ChatHistory> => {
    const response = await apiClient.get(`/api/chatbot/sessions/${session_id}/history`);
    return response.data;
  },

  // Delete a chat session
  deleteSession: async (session_id: string): Promise<void> => {
    await apiClient.delete(`/api/chatbot/sessions/${session_id}`);
  },
}; 