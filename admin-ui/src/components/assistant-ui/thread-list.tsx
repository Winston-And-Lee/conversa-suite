import React, { useState, useEffect } from 'react';
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
}

interface ThreadData {
  thread_id: string;
  title: string;
  summary: string;
  updated_at: string;
}

export const ThreadList = ({ themeColors }: ThreadListProps) => {
  const runtime = useAssistantRuntime();
  const [isLoading, setIsLoading] = useState(true);
  const [threads, setThreads] = useState<ThreadData[]>([]);
  const { getAccessToken } = useAuth();
  
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
  
  useEffect(() => {
    // Check if runtime is ready
    if (runtime) {
      // Fetch threads when component mounts
      fetchThreads();
    }
  }, [runtime]);
  
  if (isLoading || !runtime) {
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
      <ThreadListNew themeColors={themeColors} onNewChat={() => fetchThreads()} />
      {/* <Divider style={{ margin: '8px 0', borderColor: themeColors.neutral_08 }} /> */}
      <ThreadListItems themeColors={themeColors} threads={threads} />
    </ThreadListPrimitive.Root>
  );
};

interface ThreadComponentProps {
  themeColors: Record<string, string>;
  onNewChat?: () => void;
}

const ThreadListNew = ({ themeColors, onNewChat }: ThreadComponentProps) => {
  return (
    <ThreadListPrimitive.New 
      asChild
      onSelect={() => {
        // Call the onNewChat callback when a new chat is created
        if (onNewChat) {
          setTimeout(onNewChat, 1000); // Give it a second to create the thread
        }
      }}
    >
      <Button 
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
    </ThreadListPrimitive.New>
  );
};

interface ThreadListItemsProps extends ThreadComponentProps {
  threads: ThreadData[];
}

const ThreadListItems = ({ themeColors, threads }: ThreadListItemsProps) => {
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
}

const CustomThreadListItem = ({ thread, themeColors }: CustomThreadListItemProps) => {
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
        '&:hover': {
          backgroundColor: themeColors.secondary_02,
          border: `1px solid ${themeColors.neutral_08}`,
        },
      }}
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