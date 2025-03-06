import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, Card, List, Avatar, Typography, message, Spin } from 'antd';
import { SendOutlined, DeleteOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';
import { chatbotApi, ChatMessage, ChatSession } from '../services/api';

const { Text } = Typography;

interface ChatInterfaceProps {
  assistantId?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ assistantId }) => {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize chat session
  useEffect(() => {
    const initSession = async () => {
      try {
        setLoading(true);
        const newSession = await chatbotApi.createSession(assistantId);
        setSession(newSession);
        setMessages([]);
      } catch (error) {
        message.error('Failed to initialize chat session');
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    initSession();
  }, [assistantId]);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !session) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputValue,
    };

    try {
      setLoading(true);
      setMessages(prev => [...prev, userMessage]);
      setInputValue('');

      // Send message to API
      console.log(`Sending message to session ${session.session_id}: ${inputValue}`);
      const response = await chatbotApi.sendMessage(session.session_id, inputValue);
      
      console.log("Received response:", response);
      
      if (!response || !response.content) {
        console.error("Empty or invalid response received:", response);
        message.error("Received an empty response from the assistant");
        
        // Add a fallback message if response is empty
        const fallbackMessage: ChatMessage = {
          role: 'assistant',
          content: "I apologize, but I couldn't generate a response. Please try again.",
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, fallbackMessage]);
        return;
      }
      
      // Add assistant's response to messages
      setMessages(prev => [...prev, response]);
    } catch (error) {
      console.error("Error sending message:", error);
      message.error('Failed to send message');
      
      // Add a fallback message if there's an error
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: "I apologize, but there was an error processing your request. Please try again later.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleResetChat = async () => {
    if (!session) return;
    
    try {
      setLoading(true);
      // Delete current session
      await chatbotApi.deleteSession(session.session_id);
      
      // Create new session
      const newSession = await chatbotApi.createSession(assistantId);
      setSession(newSession);
      setMessages([]);
      message.success('Chat session reset successfully');
    } catch (error) {
      message.error('Failed to reset chat session');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card 
      title="Chat with AI Assistant" 
      extra={
        <Button 
          type="text" 
          danger 
          icon={<DeleteOutlined />} 
          onClick={handleResetChat}
          disabled={loading || !session}
        >
          Reset Chat
        </Button>
      }
      style={{ width: '100%', maxWidth: 800, margin: '0 auto' }}
    >
      <div style={{ height: 400, overflowY: 'auto', marginBottom: 16, padding: '0 4px' }}>
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', marginTop: 120 }}>
            <RobotOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
            <p>Start a conversation with the AI assistant</p>
          </div>
        ) : (
          <List
            itemLayout="horizontal"
            dataSource={messages}
            renderItem={(item) => (
              <List.Item style={{ padding: '8px 0' }}>
                <List.Item.Meta
                  avatar={
                    <Avatar 
                      icon={item.role === 'user' ? <UserOutlined /> : <RobotOutlined />} 
                      style={{ 
                        backgroundColor: item.role === 'user' ? '#1890ff' : '#52c41a' 
                      }}
                    />
                  }
                  title={item.role === 'user' ? 'You' : 'Assistant'}
                  description={
                    <div style={{ 
                      whiteSpace: 'pre-wrap', 
                      wordBreak: 'break-word',
                      marginTop: 4
                    }}>
                      {item.content}
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: 'flex', marginTop: 16 }}>
        <Input
          placeholder="Type your message here..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onPressEnter={handleSendMessage}
          disabled={loading || !session}
          style={{ marginRight: 8 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSendMessage}
          disabled={loading || !session || !inputValue.trim()}
        >
          Send
        </Button>
      </div>
      
      {loading && (
        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Spin size="small" />
          <Text type="secondary" style={{ marginLeft: 8 }}>
            {!session ? 'Initializing chat...' : 'Processing...'}
          </Text>
        </div>
      )}
    </Card>
  );
};

export default ChatInterface; 