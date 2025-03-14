import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useCreate, useNotification } from '@refinedev/core';
import { Form, Input, Button, Select, Upload, message, Space, Typography, Radio } from 'antd';
import { Create } from '@refinedev/antd';
import { UploadOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { RcFile, UploadFile } from 'antd/es/upload/interface';
import { TOKEN_KEY } from '@/api-requests';

import { ROUTES } from '@/constant';

const { TextArea } = Input;
const { Title, Text } = Typography;

interface FileResponse {
  file_url: string;
  file_name: string;
}
export const DataIngestionCreate = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { open } = useNotification();
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [fileUrl, setFileUrl] = useState<string | null>(null);

  const { mutate: createDataIngestion, isLoading: isSubmitting } = useCreate();

  // Handle file upload
  const handleUpload = async (options: {
    file: RcFile;
    onSuccess: (response: any, file: RcFile) => void;
    onError: (error: any) => void;
  }) => {
    const { file, onSuccess, onError } = options;
    
    setUploading(true);
    
    try {
      // Create form data for file upload
      const formData = new FormData();
      formData.append('file', file);
      
      // Call the upload API
      const response = await fetch(`${import.meta.env.VITE_APP_API_ENDPOINT}/api/files/upload`, {
        method: 'POST',
        body: formData,
        headers: {
          // No Content-Type header as it's set automatically for FormData
          Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('File upload failed');
      }
      
      const data: FileResponse = await response.json();
      
      // Store the file URL for later use in form submission
      setFileUrl(data.file_url);
      
      message.success('อัปโหลดไฟล์สำเร็จ');
      onSuccess(data, file);
    } catch (error) {
      console.error('Error uploading file:', error);
      message.error('อัปโหลดไฟล์ล้มเหลว');
      onError(error);
    } finally {
      setUploading(false);
    }
  };

  // Handle form submission
  const onFinish = async (values: {
    title: string;
    specified_text: string;
    data_type: string;
    content?: string;
    reference: string;
    keywords: string[] | string;
  }) => {
    try {
      // Convert keywords from string to array if needed
      let keywords = values.keywords;
      if (typeof keywords === 'string') {
        keywords = keywords.split(',').map((k: string) => k.trim());
      }
      
      // Prepare data for submission
      const dataToSubmit = {
        title: values.title,
        specified_text: values.specified_text,
        data_type: values.data_type,
        content: values.content || '',
        reference: values.reference,
        keywords: keywords,
        file_url: fileUrl,
      };
      
      // Submit data ingestion
      createDataIngestion(
        {
          resource: 'data-ingestion',
          values: dataToSubmit,
          dataProviderName: 'custom',
        },
        {
          onSuccess: () => {
            open?.({
              type: 'success',
              message: 'เพิ่มข้อมูลสำเร็จ',
              description: 'ข้อมูลถูกเพิ่มเข้าระบบเรียบร้อยแล้ว',
            });
            navigate(`/${ROUTES.DATA_INGESTION}`);
          },
          onError: (error: any) => {
            open?.({
              type: 'error',
              message: 'เกิดข้อผิดพลาด',
              description: error?.message || 'ไม่สามารถเพิ่มข้อมูลได้ กรุณาลองใหม่อีกครั้ง',
            });
          },
        }
      );
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  // Handle file list change
  const handleFileChange = (info: any) => {
    let newFileList = [...info.fileList];
    
    // Limit to only one file
    newFileList = newFileList.slice(-1);
    
    // Update status
    newFileList = newFileList.map(file => {
      if (file.response) {
        file.url = file.response.file_url;
      }
      return file;
    });
    
    setFileList(newFileList);
  };

  // Upload props configuration
  const uploadProps = {
    name: 'file',
    customRequest: handleUpload,
    onChange: handleFileChange,
    fileList,
    beforeUpload: (file: RcFile) => {
      const isPDF = file.type === 'application/pdf';
      const isDoc = file.type === 'application/msword' || 
                    file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      
      if (!isPDF && !isDoc) {
        message.error('คุณสามารถอัปโหลดไฟล์ PDF หรือ DOC เท่านั้น!');
        return Upload.LIST_IGNORE;
      }
      
      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('ไฟล์ต้องมีขนาดน้อยกว่า 10MB!');
        return Upload.LIST_IGNORE;
      }
      
      return true;
    },
  };

  return (
    <Create
      title="เพิ่มรายการข้อมูล"
      resource="data-ingestion"
      goBack={<Button icon={<ArrowLeftOutlined />} onClick={() => navigate(`/${ROUTES.DATA_INGESTION}`)}>กลับ</Button>}
      saveButtonProps={{
        onClick: () => form.submit(),
        loading: isSubmitting,
      }}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        autoComplete="off"
      >
        <div style={{ display: 'flex', gap: '24px' }}>
          {/* Left Column */}
          <div style={{ flex: 1 }}>
            <Form.Item
              label={<span style={{ color: '#000' }}>หัวข้อ <span style={{ color: 'red' }}>*</span></span>}
              name="title"
              rules={[{ required: true, message: 'กรุณาระบุหัวข้อ' }]}
            >
              <Input placeholder="ระบุ" />
            </Form.Item>
            
            <div style={{ marginBottom: '24px' }}>
              <div style={{ marginBottom: '8px', color: '#000' }}>ประเภทข้อมูล <span style={{ color: 'red' }}>*</span></div>
              <Form.Item
                name="data_type"
                rules={[{ required: true, message: 'กรุณาเลือกประเภทข้อมูล' }]}
                style={{ marginBottom: 0 }}
              >
                <Radio.Group style={{ width: '100%' }}>
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
              </Form.Item>
            </div>
            
            <Form.Item
              label={<span style={{ color: '#000' }}>อ้างอิง <span style={{ color: 'red' }}>*</span></span>}
              name="reference"
              rules={[{ required: true, message: 'กรุณาระบุแหล่งอ้างอิง' }]}
            >
              <Input placeholder="ระบุ" />   
            </Form.Item>
            
            <Form.Item
              label={<span style={{ color: '#000' }}>ป้อมคีย์เวิร์ด <span style={{ color: 'red' }}>*</span></span>}
              name="keywords"
              rules={[{ required: true, message: 'กรุณาระบุคีย์เวิร์ด' }]}
            >
              <Select
                mode="tags"
                placeholder="เลือก"
                tokenSeparators={[',']}
              />
            </Form.Item>
            
            <Form.Item
              label={<span style={{ color: '#000' }}>ระบุ <span style={{ color: 'red' }}>*</span></span>}
              name="specified_text"
              rules={[{ required: true, message: 'กรุณาระบุข้อความ' }]}
            >
              <TextArea rows={4} placeholder="ระบุ" />
            </Form.Item>
          </div>
          
          {/* Right Column */}
          <div style={{ flex: 1 }}>
            <div style={{ border: '1px solid #f0f0f0', borderRadius: '8px', padding: '24px', height: '100%' }}>
              <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                <Text>วางไฟล์ที่นี่ หรือ</Text>
              </div>
              
              <Form.Item name="file">
                <Upload.Dragger {...uploadProps} style={{ padding: '16px 0' }}>
                  <Button icon={<UploadOutlined />} loading={uploading}>
                    คลิกเพื่ออัพโหลดไฟล์
                  </Button>
                  <div style={{ marginTop: '16px', color: '#888', textAlign: 'center' }}>
                    รองรับไฟล์ PDF, DOC<br />
                    ขนาดไม่เกิน 10MB<br />
                    จำนวน 1 ไฟล์
                  </div>
                </Upload.Dragger>
              </Form.Item>
            </div>
          </div>
        </div>
      </Form>
    </Create>
  );
};

export default DataIngestionCreate;
