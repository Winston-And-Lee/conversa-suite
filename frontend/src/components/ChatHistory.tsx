import React, { useState, useEffect } from 'react';
import { List, Card, Button, Typography, Popconfirm, message, Skeleton, Empty } from 'antd';
import { DeleteOutlined, HistoryOutlined, LoadingOutlined } from '@ant-design/icons';
import { chatbotApi, ChatMessage, ChatHistory as ChatHistoryType } from '../services/api';

const { Text, Title } = Typography;

interface SessionItem {
  id: string;
  lastMessage?: string;
  timestamp?: string;
  messageCount: number;
}

interface ChatHistoryProps {
  onSelectSession: (sessionId: string) => void;
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ onSelectSession }) => {
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  // In a real application, you would need an API endpoint to list all sessions
  // For now, we'll use local storage to track sessions (this is just for demo purposes)
  useEffect(() => {
    const loadSessions = async () => {
      try {
        setLoading(true);
        // In a real app, you would fetch this from an API
        const sessionIds = JSON.parse(localStorage.getItem('chatSessionIds') || '[]');
        
        const sessionsData: SessionItem[] = [];
        
        for (const id of sessionIds) {
          try {
            const history = await chatbotApi.getChatHistory(id);
            const lastMessage = history.messages[history.messages.length - 1];
            
            sessionsData.push({
              id,
              lastMessage: lastMessage?.content.substring(0, 50) + (lastMessage?.content.length > 50 ? '...' : ''),
              timestamp: lastMessage?.timestamp || new Date().toISOString(),
              messageCount: history.messages.length
            });
          } catch (error) {
            console.error(`Failed to load history for session ${id}`, error);
          }
        }
        
        setSessions(sessionsData);
      } catch (error) {
        message.error('Failed to load chat sessions');
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadSessions();
  }, []);

  const handleDeleteSession = async (sessionId: string) => {
    try {
      setLoading(true);
      await chatbotApi.deleteSession(sessionId);
      
      // Update local storage
      const sessionIds = JSON.parse(localStorage.getItem('chatSessionIds') || '[]');
      localStorage.setItem('chatSessionIds', JSON.stringify(sessionIds.filter((id: string) => id !== sessionId)));
      
      // Update state
      setSessions(prev => prev.filter(session => session.id !== sessionId));
      message.success('Session deleted successfully');
    } catch (error) {
      message.error('Failed to delete session');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSession = (sessionId: string) => {
    setSelectedSessionId(sessionId);
    onSelectSession(sessionId);
  };

  return (
    <Card 
      title={
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <HistoryOutlined style={{ marginRight: 8 }} />
          <span>Chat History</span>
        </div>
      }
      style={{ width: '100%', maxWidth: 800, margin: '0 auto', marginBottom: 20 }}
    >
      {loading ? (
        <div style={{ padding: 24 }}>
          <Skeleton active avatar paragraph={{ rows: 2 }} />
          <Skeleton active avatar paragraph={{ rows: 2 }} style={{ marginTop: 16 }} />
        </div>
      ) : sessions.length === 0 ? (
        <Empty description="No chat sessions available" />
      ) : (
        <List
          itemLayout="horizontal"
          dataSource={sessions}
          renderItem={(session) => (
            <List.Item
              actions={[
                <Popconfirm
                  title="Are you sure you want to delete this session?"
                  onConfirm={() => handleDeleteSession(session.id)}
                  okText="Yes"
                  cancelText="No"
                >
                  <Button 
                    type="text" 
                    danger 
                    icon={<DeleteOutlined />}
                  />
                </Popconfirm>
              ]}
            >
              <List.Item.Meta
                title={
                  <Button 
                    type="link" 
                    onClick={() => handleSelectSession(session.id)}
                    style={{ 
                      fontWeight: selectedSessionId === session.id ? 'bold' : 'normal',
                      padding: 0,
                      textAlign: 'left'
                    }}
                  >
                    Session {session.id.substring(0, 8)}...
                  </Button>
                }
                description={
                  <>
                    <Text type="secondary">
                      {session.messageCount} messages
                      {session.timestamp && ` • ${new Date(session.timestamp).toLocaleString()}`}
                    </Text>
                    {session.lastMessage && (
                      <div style={{ marginTop: 4 }}>
                        <Text ellipsis>{session.lastMessage}</Text>
                      </div>
                    )}
                  </>
                }
              />
            </List.Item>
          )}
        />
      )}
    </Card>
  );
};

export default ChatHistory; 