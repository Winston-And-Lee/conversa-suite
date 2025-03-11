import React, { useState } from 'react';
import {
  ThreadPrimitive,
  MessagePrimitive,
  ComposerPrimitive,
  ActionBarPrimitive,
  useAssistantRuntime,
} from "@assistant-ui/react";
import { 
  SendOutlined, 
  EditOutlined, 
  CopyOutlined, 
  ReloadOutlined,
  ArrowDownOutlined,
  PaperClipOutlined,
  FileImageOutlined,
} from '@ant-design/icons';
import { Button, Typography, Avatar, Tooltip } from 'antd';
import { MarkdownText } from './markdown-text';

const { Text } = Typography;

interface ThreadProps {
  themeColors: Record<string, string>;
}

export const Thread = ({ themeColors }: ThreadProps) => {
  const runtime = useAssistantRuntime();
  
  return (
    <ThreadPrimitive.Root style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Thread Topic Header */}
      <div style={{ 
        padding: '8px 16px', 
        borderBottom: `1px solid ${themeColors.neutral_08}`,
      }}>
        <Text style={{ 
          fontSize: '18px', 
          fontWeight: 600,
          color: themeColors.primary_01
        }}>
          Current Conversation
        </Text>
      </div>
      
      <ThreadPrimitive.Viewport style={{ flex: 1, overflowY: 'auto', padding: '0' }}>
        <ThreadPrimitive.Empty>
          <div style={{ 
            padding: '48px 16px', 
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%'
          }}>
            <Text style={{ 
              fontSize: '28px', 
              fontWeight: 600,
              color: themeColors.primary_01
            }}>
              How can I help you today?
            </Text>
            <Text style={{ 
              fontSize: '18px', 
              color: themeColors.neutral_07,
              margin: '16px 0 32px'
            }}>
              Ask me anything or try one of these examples
            </Text>
            <div style={{
              width: '100%',
              maxWidth: '600px',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}>
              <ThreadPrimitive.Suggestion
                style={{
                  width: '100%',
                  padding: '16px',
                  borderRadius: '12px',
                  border: `1px solid ${themeColors.neutral_08}`,
                  backgroundColor: themeColors.secondary_02,
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  ':hover': {
                    backgroundColor: themeColors.primary_05,
                    borderColor: themeColors.primary_03,
                  }
                }}
                prompt="What is the weather in Tokyo?"
                method="replace"
                autoSend
              >
                <Text style={{ fontSize: '16px', color: themeColors.primary_01 }}>What is the weather in Tokyo?</Text>
              </ThreadPrimitive.Suggestion>
              
              <ThreadPrimitive.Suggestion
                style={{
                  width: '100%',
                  padding: '16px',
                  borderRadius: '12px',
                  border: `1px solid ${themeColors.neutral_08}`,
                  backgroundColor: themeColors.secondary_02,
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  ':hover': {
                    backgroundColor: themeColors.primary_05,
                    borderColor: themeColors.primary_03,
                  }
                }}
                prompt="What is assistant-ui?"
                method="replace"
                autoSend
              >
                <Text style={{ fontSize: '16px', color: themeColors.primary_01 }}>What is assistant-ui?</Text>
              </ThreadPrimitive.Suggestion>
            </div>
          </div>
        </ThreadPrimitive.Empty>
        
        <ThreadPrimitive.Messages
          components={{
            UserMessage: (props: any) => <UserMessage {...props} themeColors={themeColors} />,
            AssistantMessage: (props: any) => <AssistantMessage {...props} themeColors={themeColors} />,
            EditComposer: (props: any) => <EditComposer {...props} themeColors={themeColors} />,
          }}
        />
      </ThreadPrimitive.Viewport>
      
      <ThreadScrollToBottom themeColors={themeColors} />
      <Composer themeColors={themeColors} />
    </ThreadPrimitive.Root>
  );
};

interface ThreadComponentProps {
  themeColors: Record<string, string>;
}

const ThreadScrollToBottom = ({ themeColors }: ThreadComponentProps) => {
  return (
    <ThreadPrimitive.ScrollToBottom asChild>
      <Button
        icon={<ArrowDownOutlined />}
        type="primary"
        shape="circle"
        style={{
          position: 'absolute',
          bottom: '80px',
          right: '20px',
          width: '40px',
          height: '40px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: `0 2px 8px ${themeColors.primary_04}`,
          backgroundColor: themeColors.primary_02,
          color: themeColors.neutral_07,
        }}
      />
    </ThreadPrimitive.ScrollToBottom>
  );
};

const Composer = ({ themeColors }: ThreadComponentProps) => {
  const runtime = useAssistantRuntime();
  const [showAttachOptions, setShowAttachOptions] = useState(false);
  
  const handleAttachImage = () => {
    // This would be implemented to handle file uploads
    console.log('Attach image clicked');
    // Here you would trigger a file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        console.log('File selected:', file);
        // Here you would handle the file upload
      }
    };
    input.click();
  };
  
  return (
    <ComposerPrimitive.Root style={{ 
      padding: '8px', 
      borderTop: `1px solid ${themeColors.neutral_08}`,
      backgroundColor: themeColors.neutral_13
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        // padding: '8px 16px',
        // borderRadius: '16px',
        // border: `1px solid ${themeColors.neutral_08}`,
        // backgroundColor: themeColors.neutral_13,
        // boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
      }}>
        <Tooltip title="Attach image">
          <Button
            type="text"
            icon={<PaperClipOutlined />}
            onClick={() => setShowAttachOptions(!showAttachOptions)}
            style={{
              border: 'none',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: themeColors.neutral_07,
            }}
          />
        </Tooltip>
        
        {showAttachOptions && (
          <Tooltip title="Upload image">
            <Button
              type="text"
              icon={<FileImageOutlined />}
              onClick={handleAttachImage}
              style={{
                border: 'none',
                padding: '4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: themeColors.neutral_07,
              }}
            />
          </Tooltip>
        )}
        
        <ComposerPrimitive.Input
          placeholder="Message ConverSA..."
          style={{
            width: '100%',
            padding: '8px',
            border: 'none',
            resize: 'none',
            outline: 'none',
            fontSize: '16px',
            lineHeight: '24px',
          }}
        />
        <ComposerPrimitive.Send asChild>
          <Button 
            type="primary" 
            shape="circle"
            icon={<SendOutlined />}
            style={{
              marginLeft: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: themeColors.neutral_07,
              padding: '18px',
              backgroundColor: themeColors.primary_02,
            }}
          />
        </ComposerPrimitive.Send>
      </div>
    </ComposerPrimitive.Root>
  );
};

interface MessageComponentProps extends ThreadComponentProps {
  [key: string]: any;
}

const UserMessage = ({ themeColors, ...props }: MessageComponentProps) => {
  return (
    <MessagePrimitive.Root style={{ padding: '8px 16px' }}>
      <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'flex-start', gap: '12px' }}>
        <div style={{ 
          maxWidth: '80%', 
          backgroundColor: themeColors.primary_02, 
          color: 'white',
          borderRadius: '16px 16px 0 16px', 
          padding: '12px 16px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
        }}>
          <MessagePrimitive.Content>
            {(content: any) => (
              <MarkdownText fontSize={16} style={{ color: 'white' }}>{content}</MarkdownText>
            )}
          </MessagePrimitive.Content>
        </div>
        <Avatar style={{ backgroundColor: themeColors.primary_02, color: 'white' }}>U</Avatar>
      </div>
      
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '4px' }}>
        <ActionBarPrimitive.Root hideWhenRunning autohide="not-last">
          <ActionBarPrimitive.Edit asChild>
            <Button type="text" size="small" icon={<EditOutlined />} />
          </ActionBarPrimitive.Edit>
        </ActionBarPrimitive.Root>
      </div>
    </MessagePrimitive.Root>
  );
};

const AssistantMessage = ({ themeColors, ...props }: MessageComponentProps) => {
  return (
    <MessagePrimitive.Root style={{ padding: '8px 16px' }}>
      <div style={{ display: 'flex', justifyContent: 'flex-start', alignItems: 'flex-start', gap: '12px' }}>
        <Avatar style={{ backgroundColor: themeColors.primary_01, color: 'white' }}>AI</Avatar>
        <div style={{ 
          maxWidth: '80%', 
        //   backgroundColor: themeColors.secondary_02, 
          borderRadius: '16px 16px 16px 0', 
          padding: '12px 16px',
          border: `1px solid ${themeColors.neutral_08}`,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
        }}>
          <MessagePrimitive.Content>
            {(content: any) => <MarkdownText fontSize={16}>{content}</MarkdownText>}
          </MessagePrimitive.Content>
        </div>
      </div>
      
      <div style={{ display: 'flex', justifyContent: 'flex-start', marginTop: '4px', marginLeft: '44px' }}>
        <ActionBarPrimitive.Root autohide="always">
          <ActionBarPrimitive.Copy asChild>
            <Button type="text" size="small" icon={<CopyOutlined />} />
          </ActionBarPrimitive.Copy>
          <ActionBarPrimitive.Reload asChild>
            <Button type="text" size="small" icon={<ReloadOutlined />} />
          </ActionBarPrimitive.Reload>
        </ActionBarPrimitive.Root>
      </div>
    </MessagePrimitive.Root>
  );
};

const EditComposer = ({ themeColors, ...props }: MessageComponentProps) => {
  return (
    <ComposerPrimitive.Root style={{ 
      margin: '8px 16px', 
      padding: '12px', 
      borderRadius: '12px',
      backgroundColor: themeColors.secondary_02,
      border: `1px solid ${themeColors.neutral_08}`,
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
    }}>
      <ComposerPrimitive.Input style={{
        width: '100%',
        resize: 'none',
        border: 'none',
        backgroundColor: 'transparent',
        padding: '8px',
        outline: 'none',
        fontSize: '16px',
        lineHeight: '24px',
      }} />
      
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '12px' }}>
        <ComposerPrimitive.Cancel asChild>
          <Button size="small">Cancel</Button>
        </ComposerPrimitive.Cancel>
        <ComposerPrimitive.Send asChild>
          <Button type="primary" size="small" style={{ backgroundColor: themeColors.primary_01 }}>Send</Button>
        </ComposerPrimitive.Send>
      </div>
    </ComposerPrimitive.Root>
  );
}; 