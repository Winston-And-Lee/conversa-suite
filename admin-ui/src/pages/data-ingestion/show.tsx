import { Show } from '@refinedev/antd';
import { useShow, useOne } from '@refinedev/core';
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';

import { convertDate } from '@/utils';
import { Space, Tag, Typography, Button, Empty, Radio, Spin, Alert } from 'antd';
import { ArrowLeftOutlined, FilePdfOutlined, FileWordOutlined, DownloadOutlined, ReloadOutlined } from '@ant-design/icons';
import { ROUTES } from '@/constant';
import { TOKEN_KEY } from '@/api-requests';

const { Text } = Typography;

export const DataIngestionShow = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const params = useParams();
  const { queryResult, refetch } = useShow({
    resource: "data-ingestion",
    id: params?.id,
    dataProviderName: "custom",
    meta: {
      headers: {
        'Content-Type': 'application/json',
      }
    }
  });
  
  const { data, isLoading, error } = queryResult;
  
  useEffect(() => {
    console.log('Show page params:', params);
    console.log('Show page data:', data);
    console.log('Show page loading:', isLoading);
    console.log('Show page error:', error);
  }, [data, isLoading, error, params]);
  
  // Handle the standardized response format
  const record = data?.data;
  
  // Function to download the file
  const handleDownload = async () => {
    if (!record?.file_url) return;
    
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      const response = await fetch(record.file_url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to download file');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = record.file_name || 'download';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };
  
  // Determine file type
  const getFileType = () => {
    if (!record?.file_url) return null;
    
    const fileName = record.file_name || record.file_url;
    if (fileName.toLowerCase().endsWith('.pdf')) {
      return 'pdf';
    } else if (fileName.toLowerCase().endsWith('.doc') || fileName.toLowerCase().endsWith('.docx')) {
      return 'doc';
    }
    return null;
  };
  
  const fileType = getFileType();

  if (error) {
    return (
      <Alert
        message="Error"
        description={
          <div>
            <p>Failed to load data: {error?.message || "Unknown error"}</p>
            <Button 
              type="primary" 
              icon={<ReloadOutlined />} 
              onClick={() => refetch()}
            >
              Try Again
            </Button>
          </div>
        }
        type="error"
        showIcon
      />
    );
  }

  return (
    <Show 
      isLoading={isLoading}
      title="ข้อมูลสำหรับ AI"
      resource="data-ingestion"
      goBack={<Button icon={<ArrowLeftOutlined />} onClick={() => navigate(`/${ROUTES.DATA_INGESTION}`)}>กลับ</Button>}
    >
      {isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}>
          <Spin size="large" tip="กำลังโหลดข้อมูล..." />
        </div>
      ) : !record ? (
        <Alert
          message="ไม่พบข้อมูล"
          description="ไม่พบข้อมูลที่ต้องการแสดง กรุณาลองใหม่อีกครั้ง"
          type="warning"
          showIcon
        />
      ) : (
        <div style={{ display: 'flex', gap: '24px' }}>
          {/* Left Column */}
          <div style={{ flex: 1 }}>
            <div style={{ marginBottom: '24px' }}>
              <Text strong style={{ fontSize: '16px' }}>หัวข้อ</Text>
              <div style={{ marginTop: '8px', padding: '8px', background: '#f5f5f5', borderRadius: '4px' }}>
                {record?.title || '-'}
              </div>
            </div>
            
            <div style={{ marginBottom: '24px' }}>
              <Text strong style={{ fontSize: '16px' }}>ประเภทข้อมูล</Text>
              <div style={{ marginTop: '8px' }}>
                <Radio.Group value={record?.data_type} disabled style={{ width: '100%' }}>
                  <div style={{ display: 'flex', width: '100%' }}>
                    <Radio.Button value="ตัวบทกฎหมาย" style={{ flex: 1, textAlign: 'center' }}>
                      ตัวบทกฎหมาย
                    </Radio.Button>
                    <Radio.Button value="FAQ" style={{ flex: 1, textAlign: 'center' }}>
                      FAQ
                    </Radio.Button>
                    <Radio.Button value="คำแนะนำ" style={{ flex: 1, textAlign: 'center' }}>
                      คำแนะนำ
                    </Radio.Button>
                  </div>
                </Radio.Group>
              </div>
            </div>
            
            <div style={{ marginBottom: '24px' }}>
              <Text strong style={{ fontSize: '16px' }}>อ้างอิง</Text>
              <div style={{ marginTop: '8px', padding: '8px', background: '#f5f5f5', borderRadius: '4px' }}>
                {record?.reference || '-'}
              </div>
            </div>
            
            <div style={{ marginBottom: '24px' }}>
              <Text strong style={{ fontSize: '16px' }}>คีย์เวิร์ด</Text>
              <div style={{ marginTop: '8px' }}>
                <Space wrap>
                  {record?.keywords?.length > 0 ? 
                    record.keywords.map((keyword: string) => (
                      <Tag key={keyword}>{keyword}</Tag>
                    )) 
                    : '-'}
                </Space>
              </div>
            </div>
            
            <div style={{ marginBottom: '24px' }}>
              <Text strong style={{ fontSize: '16px' }}>ระบุ</Text>
              <div style={{ marginTop: '8px', padding: '8px', background: '#f5f5f5', borderRadius: '4px', minHeight: '100px' }}>
                {record?.specified_text || '-'}
              </div>
            </div>
            
            {record?.content && (
              <div style={{ marginBottom: '24px' }}>
                <Text strong style={{ fontSize: '16px' }}>เนื้อหา</Text>
                <div style={{ marginTop: '8px', padding: '8px', background: '#f5f5f5', borderRadius: '4px', minHeight: '100px' }}>
                  {record.content}
                </div>
              </div>
            )}
            
            <div style={{ marginBottom: '24px' }}>
              <Text strong style={{ fontSize: '16px' }}>วันที่สร้าง</Text>
              <div style={{ marginTop: '8px', padding: '8px', background: '#f5f5f5', borderRadius: '4px' }}>
                {record?.created_at ? convertDate(record.created_at, 'DD/MM/YYYY, HH:mm:ss', 'th') : '-'}
              </div>
            </div>
            
            <div style={{ marginBottom: '24px' }}>
              <Text strong style={{ fontSize: '16px' }}>วันที่แก้ไข</Text>
              <div style={{ marginTop: '8px', padding: '8px', background: '#f5f5f5', borderRadius: '4px' }}>
                {record?.updated_at ? convertDate(record.updated_at, 'DD/MM/YYYY, HH:mm:ss', 'th') : '-'}
              </div>
            </div>
          </div>
          
          {/* Right Column */}
          <div style={{ flex: 1 }}>
            <div style={{ border: '1px solid #f0f0f0', borderRadius: '8px', padding: '24px', height: '100%', minHeight: '500px' }}>
              {record?.file_url ? (
                <>
                  <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                    <Text strong>
                      {fileType === 'pdf' && <FilePdfOutlined style={{ marginRight: '8px', color: '#ff4d4f' }} />}
                      {fileType === 'doc' && <FileWordOutlined style={{ marginRight: '8px', color: '#1890ff' }} />}
                      {record.file_name || 'ไฟล์แนบ'}
                    </Text>
                  </div>
                  
                  <div style={{ height: 'calc(100% - 10px)', overflow: 'auto', textAlign: 'center' }}>
                    {fileType === 'pdf' ? (
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                        {/* <FilePdfOutlined style={{ fontSize: '64px', color: '#ff4d4f', marginBottom: '16px' }} />
                        <Text style={{ marginBottom: '16px' }}>ไฟล์ PDF</Text> */}
                        <Button 
                          type="primary" 
                          icon={<DownloadOutlined />} 
                          onClick={handleDownload}
                        >
                          ดาวน์โหลดไฟล์เพื่อดู
                        </Button>
                        <div style={{ marginTop: '16px', width: '100%' }}>
                          <iframe 
                            src={`${record.file_url}#toolbar=0`}
                            style={{ width: '100%', height: '700px', border: 'none' }}
                            title="PDF Preview"
                          />
                        </div>
                      </div>
                    ) : fileType === 'doc' ? (
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                        <FileWordOutlined style={{ fontSize: '64px', color: '#1890ff', marginBottom: '16px' }} />
                        <Text style={{ marginBottom: '16px' }}>ไม่สามารถแสดงตัวอย่างไฟล์ Word ได้</Text>
                        <Button 
                          type="primary" 
                          icon={<DownloadOutlined />} 
                          onClick={handleDownload}
                        >
                          ดาวน์โหลดไฟล์เพื่อดู
                        </Button>
                      </div>
                    ) : (
                      <Empty description="ไม่มีไฟล์แนบ หรือไม่รองรับการแสดงตัวอย่างไฟล์ประเภทนี้" />
                    )}
                  </div>
                </>
              ) : (
                <Empty description="ไม่มีไฟล์แนบ" />
              )}
            </div>
          </div>
        </div>
      )}
    </Show>
  );
};

export default DataIngestionShow; 