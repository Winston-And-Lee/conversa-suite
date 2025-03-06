import React, { useState } from 'react';
import { Refine } from '@refinedev/core';
import { ConfigProvider, Button, Select, Space, Typography } from 'antd';
import { 
  MenuOutlined,
  DashboardOutlined,
  MessageOutlined,
  TeamOutlined
} from '@ant-design/icons';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemedLayoutV2 as Layout } from '@refinedev/antd';

import './App.css';
import ChatInterface from './components/ChatInterface';
import ChatHistory from './components/ChatHistory';

const { Title } = Typography;
const { Option } = Select;

// This would normally be populated from an API
const AVAILABLE_ASSISTANTS = [
  { id: 'default', name: 'Default Assistant' },
  { id: 'customer-support', name: 'Customer Support' },
  { id: 'technical', name: 'Technical Assistant' },
];

function App() {
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [selectedAssistantId, setSelectedAssistantId] = useState<string>('default');

  const handleNewChat = () => {
    setActiveSessionId(null);
  };

  const handleSelectSession = (sessionId: string) => {
    setActiveSessionId(sessionId);
  };

  const handleChangeAssistant = (value: string) => {
    setSelectedAssistantId(value);
    setActiveSessionId(null);  // Reset active session when changing assistant
  };

  return (
    <BrowserRouter>
      <ConfigProvider
        theme={{
          token: {
            colorPrimary: '#1677ff',
          },
        }}
      >
        <Refine
          options={{
            syncWithLocation: true,
            warnWhenUnsavedChanges: true,
          }}
          resources={[
            {
              name: "dashboard",
              list: "/dashboard",
              meta: {
                label: "Dashboard",
                icon: <DashboardOutlined />,
              },
            },
            {
              name: "chat",
              list: "/chat",
              meta: {
                label: "Chat",
                icon: <MessageOutlined />,
              },
            },
          ]}
        >
          <Layout>
            <Routes>
              <Route path="/dashboard" element={
                <div style={{ padding: 20 }}>
                  <Title level={2}>Chatbot Dashboard</Title>
                  <p>Welcome to the Chatbot application. Use the chat feature to interact with AI assistants.</p>
                </div>
              } />
              <Route path="/chat" element={
                <div className="chat-container" style={{ padding: 20 }}>
                  <div style={{ marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Title level={2}>Chat with AI Assistant</Title>
                    
                    <Space>
                      <Select 
                        value={selectedAssistantId} 
                        onChange={handleChangeAssistant}
                        style={{ width: 200 }}
                      >
                        {AVAILABLE_ASSISTANTS.map(assistant => (
                          <Option key={assistant.id} value={assistant.id}>
                            {assistant.name}
                          </Option>
                        ))}
                      </Select>
                      
                      <Button 
                        type="primary" 
                        onClick={handleNewChat}
                      >
                        New Chat
                      </Button>
                    </Space>
                  </div>
                  
                  <ChatHistory onSelectSession={handleSelectSession} />
                  
                  {/* Active Chat Interface */}
                  <ChatInterface 
                    assistantId={activeSessionId ? undefined : selectedAssistantId} 
                  />
                </div>
              } />
              <Route path="*" element={<Navigate to="/chat" replace />} />
            </Routes>
          </Layout>
        </Refine>
      </ConfigProvider>
    </BrowserRouter>
  );
}

export default App;
