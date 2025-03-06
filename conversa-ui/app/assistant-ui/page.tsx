'use client';

import { useEffect, useState } from 'react';
import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/react-ai-sdk";
import { Thread } from "@/components/assistant-ui/thread";
import { ThreadList } from "@/components/assistant-ui/thread-list";

export default function AssistantUIPage() {
  const [error, setError] = useState<string | null>(null);
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';
  
  useEffect(() => {
    console.log("AssistantUI page loaded with backendUrl:", backendUrl);
  }, [backendUrl]);
  
  // Initialize the chat runtime with our backend API endpoint
  const runtime = useChatRuntime({
    api: `${backendUrl}/api/assistant-ui/chat`,
    onError: (error) => {
      console.error("Assistant UI runtime error:", error);
      setError(`Error: ${error.message || "Something went wrong"}`);
    }
  });

  return (
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
  );
} 