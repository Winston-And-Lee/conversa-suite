import React, { useState, useEffect, useRef } from 'react';
import {
  ThreadListItemPrimitive,
  ThreadListPrimitive,
  useAssistantRuntime,
} from "@assistant-ui/react";
import { PlusOutlined, DeleteOutlined, LoadingOutlined, MessageOutlined } from '@ant-design/icons';
import { Button, Typography, Spin, Divider, message } from 'antd';
import axios from 'axios';
import { useAuth } from '@/hooks/useAuth';

const { Text, Paragraph } = Typography;

interface ThreadListProps {
  themeColors: Record<string, string>;
  selectedThreadId?: string | null;
  onThreadSelect?: (threadId: string) => void;
  onNewChat?: () => void;
}

interface ThreadData {
  thread_id: string;
  title: string;
  summary: string;
  updated_at: string;
}

export const ThreadList = ({ themeColors, selectedThreadId, onThreadSelect, onNewChat }: ThreadListProps) => {
  const runtime = useAssistantRuntime();
  const [isLoading, setIsLoading] = useState(true);
  const [threads, setThreads] = useState<ThreadData[]>([]);
  const { getAccessToken } = useAuth();
  const lastSelectedThreadRef = useRef<string | null>(null);
  const threadSelectionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const fetchThreads = async () => {
    try {
      setIsLoading(true);
      const accessToken = await getAccessToken();
      
      // Get the backend URL from environment variables
      const backendUrl = import.meta.env.VITE_APP_API_ENDPOINT || 'http://localhost:8000';
      
      const response = await axios.get(`${backendUrl}/api/assistant-ui/threads`, {
        headers: {
          Authorization: `Bearer ${accessToken}`
        }
      });
      
      if (response.data && response.data.threads) {
        setThreads(response.data.threads);
      }
    } catch (error) {
      console.error('Error fetching threads:', error);
      message.error('Failed to load conversation history');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Initial fetch when component mounts
  useEffect(() => {
    if (runtime) {
      console.log("Initial fetch of threads");
      fetchThreads();
    }
  }, [runtime]);

  // Refresh threads when selectedThreadId changes
  useEffect(() => {
    if (runtime && selectedThreadId) {
      console.log("Selected thread ID changed, refreshing thread list");
      // Small delay to ensure the backend has completed processing
      setTimeout(() => {
        fetchThreads();
      }, 500);
    }
  }, [selectedThreadId, runtime]);

  // Set up polling to refresh the thread list periodically
  // useEffect(() => {
  //   if (!runtime) return;
    
  //   console.log("Setting up thread list polling");
  //   // Refresh the thread list every 10 seconds
  //   const intervalId = setInterval(() => {
  //     console.log("Polling for threads");
  //     fetchThreads();
  //   }, 10000);
    
  //   // Clean up the interval when the component unmounts
  //   return () => {
  //     console.log("Cleaning up thread list polling");
  //     clearInterval(intervalId);
  //   };
  // }, [runtime]);
  
  // Handle thread selection with debounce
  const handleThreadClick = (threadId: string) => {
    // Prevent selecting the same thread multiple times
    if (threadId === lastSelectedThreadRef.current) {
      return;
    }
    
    // Update the last selected thread
    lastSelectedThreadRef.current = threadId;
    
    // Clear any existing timeout
    if (threadSelectionTimeoutRef.current) {
      clearTimeout(threadSelectionTimeoutRef.current);
    }
    
    // Set a timeout to debounce the selection
    threadSelectionTimeoutRef.current = setTimeout(() => {
      if (onThreadSelect) {
        onThreadSelect(threadId);
      }
      // Reset the timeout ref
      threadSelectionTimeoutRef.current = null;
    }, 300); // 300ms debounce
  };
  
  // Handle new chat creation
  const handleNewChat = () => {
    if (onNewChat) {
      onNewChat();
    }
    // Refresh the thread list after a short delay to allow the new thread to be created
    setTimeout(fetchThreads, 1000);
  };
  
  // Clean up timeouts when component unmounts
  useEffect(() => {
    return () => {
      if (threadSelectionTimeoutRef.current) {
        clearTimeout(threadSelectionTimeoutRef.current);
      }
    };
  }, []);
  
  if (isLoading && threads.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100px',
        padding: '20px 0'
      }}>
        <Spin indicator={<LoadingOutlined style={{ fontSize: 16, color: themeColors.primary_01 }} spin />} tip="Loading conversations..." />
      </div>
    );
  }
  
  return (
    <ThreadListPrimitive.Root style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      padding: '0 16px',
    }}>
      <ThreadListNew themeColors={themeColors} onNewChat={handleNewChat} />
      {/* <Divider style={{ margin: '8px 0', borderColor: themeColors.neutral_08 }} /> */}
      <ThreadListItems 
        themeColors={themeColors} 
        threads={threads} 
        selectedThreadId={selectedThreadId}
        onThreadSelect={handleThreadClick}
      />
    </ThreadListPrimitive.Root>
  );
};

interface ThreadComponentProps {
  themeColors: Record<string, string>;
  onNewChat?: () => void;
}

const ThreadListNew = ({ themeColors, onNewChat }: ThreadComponentProps) => {
  const handleClick = () => {
    console.log("New Chat button clicked");
    if (onNewChat) {
      onNewChat();
    }
  };

  return (
    <Button 
      onClick={handleClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        padding: '10px 16px',
        height: 'auto',
        borderRadius: '12px',
        backgroundColor: themeColors.primary_02,
        color: 'white',
        fontWeight: 500,
      //   boxShadow: `0 2px 8px ${themeColors.primary_02}`,
      }}
      type="primary"
      icon={<PlusOutlined />}
    >
      New Chat
    </Button>
  );
};

interface ThreadListItemsProps extends ThreadComponentProps {
  threads: ThreadData[];
  selectedThreadId?: string | null;
  onThreadSelect?: (threadId: string) => void;
}

const ThreadListItems = ({ themeColors, threads, selectedThreadId, onThreadSelect }: ThreadListItemsProps) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <Text style={{ 
        fontSize: '14px', 
        color: themeColors.neutral_07, 
        padding: '0 4px'
      }}>
        Recent Conversations
      </Text>
      {threads.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {threads.map((thread) => (
            <CustomThreadListItem 
              key={thread.thread_id} 
              thread={thread} 
              themeColors={themeColors} 
              isSelected={selectedThreadId === thread.thread_id}
              onThreadSelect={onThreadSelect}
            />
          ))}
        </div>
      ) : (
        <Text style={{ color: themeColors.neutral_07, padding: '16px 0', textAlign: 'center' }}>
          No conversations yet. Start a new chat!
        </Text>
      )}
    </div>
  );
};

interface CustomThreadListItemProps {
  thread: ThreadData;
  themeColors: Record<string, string>;
  isSelected?: boolean;
  onThreadSelect?: (threadId: string) => void;
}

const CustomThreadListItem = ({ thread, themeColors, isSelected, onThreadSelect }: CustomThreadListItemProps) => {
  const handleThreadClick = () => {
    if (onThreadSelect) {
      onThreadSelect(thread.thread_id);
    }
  };
  
  return (
    <ThreadListItemPrimitive.Root 
      id={thread.thread_id}
      style={{
        display: 'flex',
        flexDirection: 'column',
        padding: '12px',
        borderRadius: '12px',
        cursor: 'pointer',
        transition: 'background-color 0.2s',
        border: '1px solid transparent',
        backgroundColor: isSelected ? themeColors.secondary_02 : 'transparent',
        borderColor: isSelected ? themeColors.neutral_08 : 'transparent',
        '&:hover': {
          backgroundColor: themeColors.secondary_02,
          border: `1px solid ${themeColors.neutral_08}`,
        },
      }}
      onClick={handleThreadClick}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <MessageOutlined style={{ color: themeColors.primary_01 }} />
          <Text
            style={{
              fontSize: '14px',
              fontWeight: 500,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              color: themeColors.primary_01,
            }}
          >
            {thread.title}
          </Text>
        </div>
        <ThreadListItemArchive themeColors={themeColors} />
      </div>
      <Paragraph 
        ellipsis={{ rows: 2 }}
        style={{ 
          fontSize: '12px', 
          color: themeColors.neutral_07, 
          margin: '4px 0 0 24px',
        }}
      >
        {thread.summary}
      </Paragraph>
    </ThreadListItemPrimitive.Root>
  );
};

const ThreadListItemArchive = ({ themeColors }: ThreadComponentProps) => {
  return (
    <ThreadListItemPrimitive.Archive asChild>
      <Button
        type="text"
        size="small"
        icon={<DeleteOutlined />}
        style={{
          opacity: 0,
          transition: 'opacity 0.2s',
          '&:hover': {
            opacity: 1,
            color: '#ff4d4f',
          },
        }}
      />
    </ThreadListItemPrimitive.Archive>
  );
}; 