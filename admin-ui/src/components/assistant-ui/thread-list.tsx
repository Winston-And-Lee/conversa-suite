import React, { useState, useEffect } from 'react';
import {
  ThreadListItemPrimitive,
  ThreadListPrimitive,
  useAssistantRuntime,
} from "@assistant-ui/react";
import { PlusOutlined, DeleteOutlined, LoadingOutlined, MessageOutlined } from '@ant-design/icons';
import { Button, Typography, Spin, Divider } from 'antd';

const { Text, Paragraph } = Typography;

interface ThreadListProps {
  themeColors: Record<string, string>;
}

export const ThreadList = ({ themeColors }: ThreadListProps) => {
  const runtime = useAssistantRuntime();
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Check if runtime is ready
    if (runtime) {
      // Give a small delay to ensure runtime is fully initialized
      const timer = setTimeout(() => {
        setIsLoading(false);
      }, 500);
      
      return () => clearTimeout(timer);
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
      <ThreadListNew themeColors={themeColors} />
      {/* <Divider style={{ margin: '8px 0', borderColor: themeColors.neutral_08 }} /> */}
      <ThreadListItems themeColors={themeColors} />
    </ThreadListPrimitive.Root>
  );
};

interface ThreadComponentProps {
  themeColors: Record<string, string>;
}

const ThreadListNew = ({ themeColors }: ThreadComponentProps) => {
  return (
    <ThreadListPrimitive.New asChild>
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

const ThreadListItems = ({ themeColors }: ThreadComponentProps) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <Text style={{ 
        fontSize: '14px', 
        color: themeColors.neutral_07, 
        padding: '0 4px'
      }}>
        Recent Conversations
      </Text>
      <ThreadListPrimitive.Items components={{ 
        ThreadListItem: (props: any) => <ThreadListItem {...props} themeColors={themeColors} /> 
      }} />
    </div>
  );
};

interface ThreadListItemProps extends ThreadComponentProps {
  [key: string]: any;
}

const ThreadListItem = ({ themeColors, ...props }: ThreadListItemProps) => {
  return (
    <ThreadListItemPrimitive.Root 
      {...props}
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
          <ThreadListItemTitle themeColors={themeColors} />
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
        Recent conversation messages will appear here...
      </Paragraph>
    </ThreadListItemPrimitive.Root>
  );
};

const ThreadListItemTitle = ({ themeColors }: ThreadComponentProps) => {
  return (
    <ThreadListItemPrimitive.Title asChild>
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
        {/* Default text will be replaced by the actual title */}
        Chat Topic
      </Text>
    </ThreadListItemPrimitive.Title>
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