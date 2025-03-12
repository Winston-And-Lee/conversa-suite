import React, { useState, useEffect } from 'react';
import { AssistantRuntimeProvider } from '@assistant-ui/react';
import { useChatRuntime } from '@assistant-ui/react-ai-sdk';
import { Layout, Typography, Row, Col, Alert, Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import { CustomLayout } from '@/components/customLayout';
import { Thread } from '../../components/assistant-ui/thread';
import { ThreadList } from '../../components/assistant-ui/thread-list';
import { COLORS } from '../../constant/color';
import { useAuth } from '@/hooks/useAuth';

const { Title } = Typography;
const { Content } = Layout;

// Use the green theme colors from the color.ts file
const themeColors = COLORS.default;

export const AssistantUIPage = () => {
  const [error, setError] = useState(null);
  const { getAccessToken } = useAuth();
  const [accessToken, setAccessToken] = useState<string | null>(null);
  
  // Get the backend URL from environment variables
  const backendUrl = import.meta.env.VITE_APP_API_ENDPOINT || 'http://localhost:8000';
  
  // Fetch the access token when the component mounts
  useEffect(() => {
    const fetchToken = async () => {
      try {
        const token = await getAccessToken();
        setAccessToken(token);
      } catch (error) {
        console.error('Error fetching access token:', error);
        setError('Authentication error. Please log in again.');
      }
    };
    
    fetchToken();
  }, []);
  
  // Initialize the chat runtime with API endpoint and access token
  const runtime = useChatRuntime({
    api: `${backendUrl}/api/assistant-ui/chat`,
    headers: accessToken ? {
      Authorization: `Bearer ${accessToken}`
    } : undefined,
    onError: (error: any) => {
      console.error('Assistant UI runtime error:', error);
      setError(`Error: ${error.message || 'Something went wrong'}`);
    }
  });

  // Show loading state if runtime is not available yet or we're fetching the token
  if (!runtime || !accessToken) {
    return (
      <CustomLayout>
        <Content style={{ padding: '0' }}>
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: 'calc(100vh - 132px)',
          }}>
            <Spin indicator={<LoadingOutlined style={{ fontSize: 24, color: themeColors.primary_01 }} spin />} />
            <div style={{ marginTop: '16px', color: themeColors.primary_01 }}>Loading assistant...</div>
          </div>
        </Content>
      </CustomLayout>
    );
  }

  return (
      <Content style={{ padding: '0' }}>
        <AssistantRuntimeProvider runtime={runtime}>
          <Row gutter={[0, 0]} style={{ height: 'calc(100vh - 0px)' }}>
            {/* Left sidebar with conversations list */}
            <Col span={5} style={{ height: '100%' }}>
              <div style={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                borderRight: `1px solid ${themeColors.neutral_07}`,
                background: themeColors.neutral_13,
                padding: '0'
              }}>
                <Title level={5} style={{ margin: '16px', color: themeColors.primary_01 }}>Conversations</Title>
                <div style={{ flex: 1, overflow: 'auto' }}>
                  <ThreadList themeColors={themeColors} />
                </div>
              </div>
            </Col>
            
            {/* Right side with chat interface */}
            <Col span={19} style={{ height: '100%' }}>
              <div style={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                background: themeColors.neutral_13,
                padding: '0'
              }}>
                {error && (
                  <Alert
                    message={error}
                    type="error"
                    closable
                    style={{ margin: '0 16px 16px' }}
                    onClose={() => setError(null)}
                  />
                )}
                
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                  <Thread themeColors={themeColors} />
                </div>
              </div>
            </Col>
          </Row>
        </AssistantRuntimeProvider>
      </Content>
  );
}; 