'use client';

import { useEffect, useState } from 'react';
import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/react-ai-sdk";
import { Thread } from "@/components/assistant-ui/thread";
import { ThreadList } from "@/components/assistant-ui/thread-list";

// Add a meta tag for referrer policy
const ReferrerPolicyMeta = () => {
  useEffect(() => {
    // Add meta tag to control referrer policy
    const meta = document.createElement('meta');
    meta.name = 'referrer';
    meta.content = 'no-referrer-when-downgrade';
    document.head.appendChild(meta);
    
    return () => {
      // Remove on unmount
      document.head.removeChild(meta);
    };
  }, []);
  
  return null;
};

export default function AssistantUIPage() {
  const [error, setError] = useState<string | null>(null);
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';
  
  useEffect(() => {
    console.log("AssistantUI page loaded with backend URL:", backendUrl);
    
    // Override fetch globally just for this component
    const originalFetch = window.fetch;
    window.fetch = (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;
      
      // Only modify requests to our backend
      if (url.includes('/api/assistant') || url.includes(backendUrl)) {
        const newInit = {
          ...init,
          headers: {
            ...init?.headers,
            'Content-Type': 'application/json',
          },
          credentials: 'include' as RequestCredentials,
          mode: 'cors' as RequestMode,
        };
        
        return originalFetch(input, newInit);
      }
      
      return originalFetch(input, init);
    };
    
    // Restore original fetch when component unmounts
    return () => {
      window.fetch = originalFetch;
    };
  }, [backendUrl]);
  
  // Initialize the chat runtime with API endpoint
  const runtime = useChatRuntime({
    api: `${backendUrl}/api/assistant-ui/chat`,
    onError: (error) => {
      console.error("Assistant UI runtime error:", error);
      setError(`Error: ${error.message || "Something went wrong"}`);
    }
  });

  return (
    <>
      <ReferrerPolicyMeta />
      <AssistantRuntimeProvider runtime={runtime}>
        <div className="grid h-dvh grid-cols-[250px_1fr] gap-x-4 px-4 py-4">
          <div className="flex flex-col">
            <h2 className="text-xl font-bold mb-4">Conversations</h2>
            <ThreadList />
          </div>
          <div className="flex flex-col">
            <h2 className="text-xl font-bold mb-4">ConverSA Assistant</h2>
            {error ? (
              <div className="p-4 bg-red-100 text-red-700 rounded-lg mb-4">
                {error}
                <button 
                  onClick={() => setError(null)} 
                  className="ml-2 px-2 py-1 bg-red-200 rounded hover:bg-red-300"
                >
                  Dismiss
                </button>
              </div>
            ) : null}
            <div className="flex-1 overflow-hidden rounded-lg border">
              <Thread />
            </div>
          </div>
        </div>
      </AssistantRuntimeProvider>
    </>
  );
} 