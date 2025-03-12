import React, { useState, useEffect, useRef } from 'react';
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
import { Button, Typography, Avatar, Tooltip, message, Spin } from 'antd';
import { MarkdownText } from './markdown-text';
import axios from 'axios';
import { useAuth } from '@/hooks/useAuth';

const { Text } = Typography;

interface ThreadProps {
  themeColors: Record<string, string>;
  threadId?: string | null;
  onThreadCreated?: (threadId: string) => void;
}

interface ThreadMessage {
  role: string;
  content: string;
  timestamp: number;
}

export const Thread = ({ themeColors, threadId, onThreadCreated }: ThreadProps) => {
  const runtime = useAssistantRuntime();
  const { getAccessToken } = useAuth();
  const [threadTitle, setThreadTitle] = useState("Current Conversation");
  const [messages, setMessages] = useState<ThreadMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const apiCallInProgressRef = useRef(false);
  
  // Load thread when threadId changes
  useEffect(() => {
    // Reset state if no threadId
    if (!threadId) {
      setThreadTitle("Current Conversation");
      setMessages([]);
      return;
    }
    
    // Prevent duplicate API calls
    if (apiCallInProgressRef.current) {
      return;
    }
    
    // Always fetch thread details when threadId changes
    setIsLoading(true);
    apiCallInProgressRef.current = true;
    
    const fetchThreadDetails = async () => {
      try {
        const accessToken = await getAccessToken();
        const backendUrl = import.meta.env.VITE_APP_API_ENDPOINT || 'http://localhost:8000';
        
        // Fetch thread details
        const threadResponse = await axios.get(`${backendUrl}/api/assistant-ui/threads/${threadId}`, {
          headers: {
            Authorization: `Bearer ${accessToken}`
          }
        });
        
        if (threadResponse.data) {
          setThreadTitle(threadResponse.data.title || "Current Conversation");
          // Set messages from the thread
          if (threadResponse.data.messages && Array.isArray(threadResponse.data.messages)) {
            // Ensure each message has the required properties
            const validMessages = threadResponse.data.messages.filter((msg: any) => 
              msg && typeof msg === 'object' && msg.role && msg.content
            );
            setMessages(validMessages);
          } else {
            setMessages([]);
          }
        } else {
          setThreadTitle("Current Conversation");
          setMessages([]);
        }
      } catch (error) {
        message.error('Failed to load conversation');
        setThreadTitle("Current Conversation");
        setMessages([]);
      } finally {
        setIsLoading(false);
        apiCallInProgressRef.current = false;
      }
    };
    
    fetchThreadDetails();
    
    // Clean up function to reset the API call flag if the component unmounts
    return () => {
      apiCallInProgressRef.current = false;
    };
  }, [threadId]);
  
  // Handle message submission and thread creation
  const handleMessageSubmit = async (content: string) => {
    if (!runtime) return;
    
    try {
      // Create a custom API call to send the message and create a thread if needed
      const accessToken = await getAccessToken();
      const backendUrl = import.meta.env.VITE_APP_API_ENDPOINT || 'http://localhost:8000';
      
      // Add the user message to the local state immediately for better UX
      const userMessage = {
        role: 'user',
        content: content,
        timestamp: Date.now()
      };
      
      setMessages((prevMessages: ThreadMessage[]) => [...prevMessages, userMessage]);
      
      // Create a temporary AI message for immediate visual feedback
      const tempAiMessage: ThreadMessage = {
        role: 'assistant',
        content: 'Thinking...',
        timestamp: Date.now() + 1
      };

      setMessages((prevMessages: ThreadMessage[]) => [...prevMessages, tempAiMessage]);

      // Store a local reference to the current threadId to handle state transitions properly
      const currentThreadId = threadId;
      
      // Determine the API endpoint based on whether we have a thread ID
      const endpoint = currentThreadId 
        ? `${backendUrl}/api/assistant-ui/threads/${currentThreadId}/messages` 
        : `${backendUrl}/api/assistant-ui/threads`;
      
      // Handle streaming responses differently
      if (!currentThreadId) {
        // Creating a new thread with streaming response handling
        try {
          // First, add the user message to the display
          const userMessageObject = {
            role: 'user',
            content: content,
            timestamp: Date.now() - 1000
          };
          
          // Add an initial placeholder AI response that we'll update
          const initialAiMessage = {
            role: 'assistant',
            content: 'Thinking...',
            timestamp: Date.now()
          };
          
          // Set initial messages with user message and placeholder
          setMessages([userMessageObject, initialAiMessage]);
          
          // Get the response as a stream using fetch API
          const response = await fetch(`${backendUrl}/api/assistant-ui/threads`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ content })
          });
          
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          
          // Try to extract thread ID from URL
          const responseUrl = response.url;
          
          let newThreadId: string | null = null;
          const urlMatch = responseUrl.match(/\/threads\/([^/]+)/);
          if (urlMatch && urlMatch[1]) {
            newThreadId = urlMatch[1];
            
            // Notify parent about the new thread
            if (onThreadCreated && newThreadId) {
              onThreadCreated(newThreadId);
            }
          }
          
          if (!response.body) {
            throw new Error("No response body");
          }
          
          // Setup stream reading
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let aiResponse = '';
          
          // Process the stream
          while (true) {
            const { done, value } = await reader.read();
            if (done) {
              break;
            }
            
            // Decode the chunk
            const chunk = decoder.decode(value, { stream: true });
            
            // Process each line (DataStreamEncoder format)
            const lines = chunk.split('\n');
            for (const line of lines) {
              if (line.trim() === '') continue;
              
              try {
                // Format is type:data
                const colonIndex = line.indexOf(':');
                if (colonIndex === -1) continue;
                
                const type = line.substring(0, colonIndex);
                const dataStr = line.substring(colonIndex + 1);
                
                if (type === '0') {
                  // Text delta (incremental update)
                  // Format: 0:"text delta"
                  const textDelta = JSON.parse(dataStr);
                  
                  aiResponse += textDelta;
                  
                  // Update the AI message with the accumulated response
                  setMessages((prevMessages: ThreadMessage[]) => {
                    const newMessages = [...prevMessages];
                    const assistantIdx = newMessages.findIndex(m => m.role === 'assistant');
                    if (assistantIdx >= 0) {
                      newMessages[assistantIdx] = {
                        ...newMessages[assistantIdx],
                        content: aiResponse
                      };
                    }
                    return newMessages;
                  });
                }
                else if (type === '2') {
                  // Data message (complete message)
                  // Format: 2:[{data object}]
                  const dataArray = JSON.parse(dataStr);
                  if (dataArray && dataArray.length > 0) {
                    const data = dataArray[0];
                    
                    // If this data contains content, update our AI response
                    if (data && data.content !== undefined) {
                      aiResponse = data.content;
                      
                      // Update the AI message with complete content
                      setMessages((prevMessages: ThreadMessage[]) => {
                        const newMessages = [...prevMessages];
                        const assistantIdx = newMessages.findIndex(m => m.role === 'assistant');
                        if (assistantIdx >= 0) {
                          newMessages[assistantIdx] = {
                            ...newMessages[assistantIdx],
                            content: aiResponse
                          };
                        }
                        return newMessages;
                      });
                    }
                    
                    // Check if we found a thread_id in the data
                    if (!newThreadId && data && data.thread_id) {
                      newThreadId = data.thread_id;
                      
                      if (onThreadCreated && newThreadId) {
                        onThreadCreated(newThreadId);
                      }
                    }
                  }
                }
                else if (type === '3') {
                  // Error message
                  // Format: 3:"error message"
                  const errorMessage = JSON.parse(dataStr);
                  
                  // Update the AI message with the error
                  setMessages((prevMessages: ThreadMessage[]) => {
                    const newMessages = [...prevMessages];
                    const assistantIdx = newMessages.findIndex(m => m.role === 'assistant');
                    if (assistantIdx >= 0) {
                      newMessages[assistantIdx] = {
                        ...newMessages[assistantIdx],
                        content: `Error: ${errorMessage}`
                      };
                    }
                    return newMessages;
                  });
                }
              } catch (e) {
                // Ignore parsing errors, might be incomplete chunks
              }
            }
          }
          
          // If we didn't get any AI response after processing the stream
          if (!aiResponse || aiResponse === 'Thinking...') {
            setMessages((prevMessages: ThreadMessage[]) => {
              const newMessages = [...prevMessages];
              const assistantIdx = newMessages.findIndex(m => m.role === 'assistant');
              if (assistantIdx >= 0) {
                newMessages[assistantIdx] = {
                  ...newMessages[assistantIdx],
                  content: "I encountered an error processing your message. Please try again."
                };
              }
              return newMessages;
            });
          } else {
            // Ensure the final message is properly set with the complete response
            setMessages((prevMessages: ThreadMessage[]) => {
              const newMessages = [...prevMessages];
              const assistantIdx = newMessages.findIndex(m => m.role === 'assistant');
              if (assistantIdx >= 0) {
                newMessages[assistantIdx] = {
                  ...newMessages[assistantIdx],
                  content: aiResponse
                };
              }
              return newMessages;
            });
          }
          
          // CRITICAL FIX: Update the local threadId state variable so subsequent messages use the existing thread
          if (newThreadId) {
            // We've already notified the parent through onThreadCreated, but let's verify it
            if (!currentThreadId) {
              // If our component hasn't been updated with the thread ID yet (which can happen due to React's async nature)
              
              // Call onThreadCreated again just to be sure - this is safe because the parent has logic to avoid duplicate updates
              if (onThreadCreated) {
                onThreadCreated(newThreadId);
              }
              
              // Fetch the complete thread details to ensure we have all messages
              setTimeout(async () => {
                try {
                  const accessToken = await getAccessToken();
                  const threadResponse = await axios.get(`${backendUrl}/api/assistant-ui/threads/${newThreadId}`, {
                    headers: {
                      Authorization: `Bearer ${accessToken}`
                    }
                  });
                  
                  if (threadResponse.data && threadResponse.data.messages && Array.isArray(threadResponse.data.messages)) {
                    // Make sure to replace all messages with those from the server
                    const validMessages = threadResponse.data.messages.filter((msg: any) => 
                      msg && typeof msg === 'object' && msg.role && msg.content
                    );
                    
                    if (validMessages.length > 0) {
                      setMessages(validMessages);
                    }
                  }
                } catch (error) {
                  // Error handling is already in place
                }
              }, 500);
            }
          }
          
        } catch (error: any) {
          message.error('Failed to create conversation');
          
          // On error, update the thinking message with an error message
          setMessages((prevMessages: ThreadMessage[]) => {
            const userMessages = prevMessages.filter(msg => msg.role === 'user');
            return [
              ...userMessages,
              {
                role: 'assistant',
                content: 'I encountered an error processing your message. Please try again.',
                timestamp: Date.now()
              }
            ];
          });
        }
      } else {
        // For existing threads, use the current approach
        const response = await axios.post(endpoint, {
          content: content
        }, {
          headers: {
            Authorization: `Bearer ${accessToken}`
          }
        });
        
        // For existing threads, fetch the updated messages
        setTimeout(async () => {
          try {
            const threadResponse = await axios.get(`${backendUrl}/api/assistant-ui/threads/${currentThreadId}`, {
              headers: {
                Authorization: `Bearer ${accessToken}`
              }
            });
            
            if (threadResponse.data && threadResponse.data.messages && Array.isArray(threadResponse.data.messages)) {
              // Make sure to replace all messages with those from the server, but filter out any 'Thinking...' messages
              const realMessages = threadResponse.data.messages.filter(
                (msg: ThreadMessage) => msg.content !== 'Thinking...'
              );
              
              if (realMessages.length > 0) {
                setMessages(realMessages);
              } else {
                // If the server didn't return any valid messages, create a default response
                const aiMessage = {
                  role: 'assistant',
                  content: 'I received your message. How can I help you further?',
                  timestamp: Date.now() + 2
                };
                setMessages((prevMessages: ThreadMessage[]) => {
                  const filteredMessages = prevMessages.filter((msg: ThreadMessage) => msg.content !== 'Thinking...');
                  return [...filteredMessages, aiMessage];
                });
              }
            } else {
              // If we don't get a valid response, replace the temporary message with a real one
              const aiMessage = {
                role: 'assistant',
                content: 'I received your message. How can I help you further?',
                timestamp: Date.now() + 2
              };
              setMessages((prevMessages: ThreadMessage[]) => {
                const filteredMessages = prevMessages.filter((msg: ThreadMessage) => msg.content !== 'Thinking...');
                return [...filteredMessages, aiMessage];
              });
            }
          } catch (error) {
            message.error('Failed to load conversation');
            // If there's an error, replace the temporary message with a real one
            const aiMessage = {
              role: 'assistant',
              content: 'I received your message, but I encountered an error. Please try again.',
              timestamp: Date.now() + 2
            };
            setMessages((prevMessages: ThreadMessage[]) => {
              const filteredMessages = prevMessages.filter((msg: ThreadMessage) => msg.content !== 'Thinking...');
              return [...filteredMessages, aiMessage];
            });
          }
        }, 1000); // Reduced wait time for better UX
      }
    } catch (error) {
      message.error('Failed to send message');
      // If there's an error, add a fallback AI message
      const aiMessage = {
        role: 'assistant',
        content: 'I encountered an error processing your message. Please try again.',
        timestamp: Date.now() + 1
      };
      setMessages((prevMessages: ThreadMessage[]) => {
        const filteredMessages = prevMessages.filter((msg: ThreadMessage) => msg.content !== 'Thinking...');
        return [...filteredMessages, aiMessage];
      });
    }
  };
  
  // Debug render of messages - this will help us verify if messages are being processed
  const debugMessages = () => {
    if (!messages || messages.length === 0) {
      return <div style={{ padding: '10px', color: 'gray' }}>No messages to display</div>;
    }
    
    return (
      <div style={{ padding: '10px', border: '1px solid #ccc', margin: '10px 0' }}>
        <h4>Debug: Messages in state ({messages.length})</h4>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ margin: '5px 0', padding: '5px', border: '1px solid #eee' }}>
            <strong>Role:</strong> {msg.role}, <strong>Content:</strong> {msg.content}
          </div>
        ))}
      </div>
    );
  };
  
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
          {threadTitle}
        </Text>
      </div>
      
      <ThreadPrimitive.Viewport style={{ flex: 1, overflowY: 'auto', padding: '0' }}>
        {isLoading ? (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%' 
          }}>
            <Spin tip="Loading conversation..." />
          </div>
        ) : messages && messages.length > 0 ? (
          <div style={{ padding: '16px' }}>
            {/* Add debug output in development */}
            {/* {process.env.NODE_ENV !== 'production' && debugMessages()} */}
            
            {messages.map((msg, index) => {
              return (
                <div key={`message-${index}-${msg.timestamp || index}`} style={{ marginBottom: '16px', display: 'block' }}>
                  {msg.role === 'user' ? (
                    <UserMessage message={msg} themeColors={themeColors} />
                  ) : (
                    <AssistantMessage message={msg} themeColors={themeColors} />
                  )}
                </div>
              );
            })}
          </div>
        ) : (
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
        )}
      </ThreadPrimitive.Viewport>
      
      <ThreadScrollToBottom themeColors={themeColors} />
      <Composer themeColors={themeColors} onSubmit={handleMessageSubmit} />
    </ThreadPrimitive.Root>
  );
};

interface ThreadComponentProps {
  themeColors: Record<string, string>;
  onSubmit?: (content: string) => void;
  message?: ThreadMessage;
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

const Composer = ({ themeColors, onSubmit }: ThreadComponentProps) => {
  const runtime = useAssistantRuntime();
  const [showAttachOptions, setShowAttachOptions] = useState(false);
  const [inputValue, setInputValue] = useState('');
  
  const handleAttachImage = () => {
    // This would be implemented to handle file uploads
    // Here you would trigger a file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = (e: Event) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        // Here you would handle the file upload
      }
    };
    input.click();
  };
  
  const handleSubmit = (e: any) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    
    if (onSubmit) {
      onSubmit(inputValue);
    }
    
    setInputValue('');
  };
  
  return (
    <ComposerPrimitive.Root asChild style={{ 
      padding: '8px', 
      borderTop: `1px solid ${themeColors.neutral_08}`,
      backgroundColor: themeColors.neutral_13
    }}>
      <form onSubmit={handleSubmit}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
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
            value={inputValue}
            onChange={(e: any) => setInputValue(e.target.value)}
          />
          
          <Button 
            type="primary" 
            shape="circle"
            htmlType="submit"
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
        </div>
      </form>
    </ComposerPrimitive.Root>
  );
};

interface MessageComponentProps extends ThreadComponentProps {
  [key: string]: any;
}

const UserMessage = ({ themeColors, message }: MessageComponentProps) => {
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'flex-end', 
      alignItems: 'flex-start', 
      gap: '12px',
      width: '100%'
    }}>
      <div style={{ 
        maxWidth: '80%', 
        backgroundColor: themeColors.primary_02, 
        color: 'white',
        borderRadius: '16px 16px 0 16px', 
        padding: '12px 16px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
        display: 'block'
      }}>
        <div style={{ color: 'white', fontSize: '16px' }}>
          {message?.content || "No content"}
        </div>
      </div>
      <Avatar style={{ backgroundColor: themeColors.primary_02, color: 'white' }}>U</Avatar>
    </div>
  );
};

const AssistantMessage = ({ themeColors, message }: MessageComponentProps) => {
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'flex-start', 
      alignItems: 'flex-start', 
      gap: '12px',
      width: '100%'
    }}>
      <Avatar style={{ backgroundColor: themeColors.primary_01, color: 'white' }}>AI</Avatar>
      <div style={{ 
        maxWidth: '80%', 
        borderRadius: '16px 16px 16px 0', 
        padding: '12px 16px',
        border: `1px solid ${themeColors.neutral_08}`,
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
        display: 'block'
      }}>
        <div style={{ fontSize: '16px' }}>
          {message?.content || "No content"}
        </div>
      </div>
    </div>
  );
}; 