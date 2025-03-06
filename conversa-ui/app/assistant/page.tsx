'use client';

import { useEffect, useState } from 'react';

export default function AssistantPage() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<{ role: string; content: string }[]>([]);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

  // Log environment variables to debug
  useEffect(() => {
    console.log('Environment variables:', {
      backendUrl,
      NEXT_PUBLIC_BACKEND_API_URL: process.env.NEXT_PUBLIC_BACKEND_API_URL
    });
  }, []);

  const sendMessage = async () => {
    if (!message.trim()) return;
    
    // Add user message to chat history
    const updatedHistory = [
      ...chatHistory,
      { role: 'user', content: message }
    ];
    setChatHistory(updatedHistory);
    setIsLoading(true);
    setMessage('');

    try {
      if (!threadId) {
        console.error('No thread ID available');
        throw new Error('No thread ID available');
      }

      // The correct endpoint from the OpenAPI doc is /api/assistant/assistant/threads/{thread_id}/messages
      const url = `${backendUrl}/api/assistant/assistant/threads/${threadId}/messages`;
      console.log('Sending message to:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: message,
          stream: false
        })
      });

      if (!response.ok) {
        console.error('API Error:', response.status, response.statusText);
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Response data:', data);
      
      // Update chat history with messages
      setChatHistory(data.messages);
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message to chat
      setChatHistory([
        ...updatedHistory,
        { role: 'assistant', content: 'Sorry, there was an error processing your request.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Create a thread when the component mounts
  useEffect(() => {
    if (!threadId) {
      createThread();
    }
  }, []);

  const createThread = async () => {
    try {
      // The correct endpoint from the OpenAPI doc is /api/assistant/assistant/threads
      const url = `${backendUrl}/api/assistant/assistant/threads`;
      console.log('Creating thread at:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          system_message: 'You are a helpful assistant. Answer questions clearly and concisely.',
          assistant_id: 'default'
        })
      });

      if (!response.ok) {
        console.error('API Error:', response.status, response.statusText);
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Thread created:', data);
      setThreadId(data.thread_id);
    } catch (error) {
      console.error('Error creating thread:', error);
    }
  };

  return (
    <div className="flex flex-col h-screen p-4">
      <div className="text-2xl font-bold mb-4">ConverSA Assistant</div>
      <div className="flex-1 overflow-y-auto mb-4 border rounded-lg p-4">
        {threadId ? (
          <div className="text-xs text-gray-500 mb-4">Thread ID: {threadId}</div>
        ) : (
          <div className="text-xs text-gray-500 mb-4">Creating thread...</div>
        )}
        {chatHistory.map((msg, index) => (
          <div key={index} className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="text-left mb-4">
            <div className="inline-block p-3 rounded-lg bg-gray-200">
              Thinking...
            </div>
          </div>
        )}
      </div>
      <div className="flex">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message here..."
          className="flex-1 p-2 border rounded-l-lg"
          disabled={isLoading || !threadId}
        />
        <button
          onClick={sendMessage}
          disabled={isLoading || !message.trim() || !threadId}
          className="bg-blue-500 text-white p-2 rounded-r-lg disabled:bg-blue-300"
        >
          Send
        </button>
      </div>
    </div>
  );
} 