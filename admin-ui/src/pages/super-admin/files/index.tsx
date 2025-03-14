import { DeleteButton } from '@refinedev/antd';
import { useDelete, useNotification } from '@refinedev/core';
import React, { useState, ChangeEvent } from 'react';
import { useTranslation } from 'react-i18next';

import { AutoRenderFilterV2 } from '@/components/autoRender/filterv2';
import { CustomList } from '@/components/customList';
import { PaginationComponent } from '@/components/customPagination';
import { CustomTable } from '@/components/tableComponent';
import { useFilterTableV2 } from '@/hooks/useFilterTablev2';
import { convertDate } from '@/utils';
import { Space, Table, Typography, Tag, Modal, Button, Upload, Form, Input, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import type { RcFile, UploadFile } from 'antd/es/upload';
import { TOKEN_KEY } from '@/api-requests';

const { Link } = Typography;

export const FileList = () => {
  const { t } = useTranslation();
  const { open } = useNotification();
  const { mutate: deleteData } = useDelete();
  const [isUploadModalVisible, setIsUploadModalVisible] = useState(false);
  const [fileList, setFileList] = useState<RcFile[]>([]);
  const [description, setDescription] = useState('');
  const [form] = Form.useForm();

  const { filterProps, tableProps, setCurrent, setPageSize, tableQueryResult } = useFilterTableV2({
    resource: 'files',
    dataProviderName: 'custom',
    initialPageSize: 10,
    sorters: {
      initial: [
        {
          field: 'created_at',
          order: 'desc'
        }
      ]
    },
    filters: {
      permanent: [],
      mode: 'server'
    },
    simples: [
      {
        fields: 'file_name',
        operator: 'contains',
        multipleInput: false,
        nameShow: 'File Name'
      },
      {
        fields: 'file_type',
        operator: 'eq',
        multipleInput: true,
        nameShow: 'File Type',
        optionSelect: {
          values: ['image', 'document', 'audio', 'video', 'other']
        }
      }
    ]
  });

  const handleDelete = (fileName: string) => {
    deleteData(
      {
        resource: 'files',
        id: fileName,
        dataProviderName: 'custom'
      },
      {
        onSuccess: () => {
          open?.({
            type: 'success',
            message: 'File deleted successfully',
            description: 'The file has been removed from the system'
          });
          
          // Immediately update the table data by removing the deleted row
          if (tableQueryResult.data?.data) {
            const updatedData = tableQueryResult.data.data.filter(
              (item: any) => item.file_name !== fileName
            );
            
            // Update the data in place
            tableQueryResult.data.data = updatedData;
            
            // Force a re-render by updating the state
            tableQueryResult.refetch();
          }
        },
        onError: (error: Error) => {
          open?.({
            type: 'error',
            message: 'Error',
            description: error?.message || 'Failed to delete file. Please try again.'
          });
        }
      }
    );
  };

  const showUploadModal = () => {
    setIsUploadModalVisible(true);
  };

  const handleUploadCancel = () => {
    setIsUploadModalVisible(false);
    setFileList([]);
    setDescription('');
    form.resetFields();
  };

  const handleUploadOk = async () => {
    try {
      await form.validateFields();
      
      if (fileList.length === 0) {
        message.error('Please select a file to upload');
        return;
      }

      const formData = new FormData();
      formData.append('file', fileList[0]);
      
      if (description) {
        formData.append('description', description);
      }

      // Get the token from localStorage
      const token = localStorage.getItem(TOKEN_KEY);
      
      if (!token) {
        message.error('Authentication token not found. Please log in again.');
        return;
      }

      const response = await fetch(`${import.meta.env.VITE_APP_API_ENDPOINT}/api/files/upload`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload file');
      }

      message.success('File uploaded successfully');
      setIsUploadModalVisible(false);
      setFileList([]);
      setDescription('');
      form.resetFields();
      tableQueryResult.refetch();
    } catch (error) {
      message.error(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const uploadProps: UploadProps = {
    beforeUpload: (file: RcFile) => {
      setFileList([file]);
      return false;
    },
    fileList: fileList.map((file: RcFile) => ({
      uid: file.uid,
      name: file.name,
      status: 'done',
      url: URL.createObjectURL(file),
    })) as UploadFile[],
    onRemove: () => {
      setFileList([]);
    },
    maxCount: 1,
    capture: undefined,
  };

  const handleDownload = async (fileName: string) => {
    try {
      // Get the token from localStorage
      const token = localStorage.getItem(TOKEN_KEY);
      
      if (!token) {
        message.error('Authentication token not found. Please log in again.');
        return;
      }

      // Use fetch with authorization header
      const response = await fetch(`${import.meta.env.VITE_APP_API_ENDPOINT}/api/files/download/${fileName}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to download file');
      }

      // Get the blob from the response
      const blob = await response.blob();
      
      // Create a URL for the blob
      const url = window.URL.createObjectURL(blob);
      
      // Create a temporary link element
      const link = document.createElement('a');
      link.href = url;
      
      // Extract the actual filename from the path
      const actualFileName = fileName.split('/').pop();
      link.download = actualFileName || 'download';
      
      // Append to the document
      document.body.appendChild(link);
      
      // Trigger the download
      link.click();
      
      // Clean up
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      message.error(`Download failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <CustomList 
        headerButtons={[
          <Button type="primary" icon={<UploadOutlined />} onClick={showUploadModal}>
            Upload File
          </Button>
        ]}
        title="Files"
      >
        <AutoRenderFilterV2 {...filterProps} {...tableQueryResult} />
        <CustomTable size='small' {...tableProps} rowKey='id' pagination={false}>
          <Table.Column
            key='file_name'
            dataIndex='file_name'
            fixed='left'
            title='File Name'
            render={(value) => {
              return <Typography.Text>{value.split('/').pop()}</Typography.Text>;
            }}
          />

          <Table.Column
            key='file_type'
            dataIndex='file_type'
            title='File Type'
            render={value => <Tag color={getFileTypeColor(value)}>{value}</Tag>}
          />

          <Table.Column
            key='description'
            dataIndex='description'
            title='Description'
            render={value => <Typography.Text>{value || '-'}</Typography.Text>}
          />

          <Table.Column
            key='created_at'
            dataIndex='created_at'
            title='Upload Date'
            render={value => (
              <Typography.Text>{value ? convertDate(value, 'DD/MM/YYYY, HH:mm:ss', 'th') : '-'}</Typography.Text>
            )}
            sorter
          />

          <Table.Column
            title='Actions'
            dataIndex='actions'
            fixed='right'
            render={(_, record: any) => (
              <Space>
                <Button 
                  size='small' 
                  type="primary"
                  onClick={() => handleDownload(record.file_name)}
                >
                  Download
                </Button>
                <DeleteButton 
                  hideText 
                  size='small'
                  recordItemId={record.file_name}
                  onClick={() => handleDelete(record.file_name)}
                />
              </Space>
            )}
          />
        </CustomTable>
      </CustomList>
      <PaginationComponent
        totalRecords={tableQueryResult.data?.total}
        setCurrent={setCurrent}
        setPageSize={setPageSize}
      />

      <Modal
        title="Upload File"
        open={isUploadModalVisible}
        onOk={handleUploadOk}
        onCancel={handleUploadCancel}
        okText="Upload"
        cancelText="Cancel"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="file"
            label="File"
            rules={[{ required: true, message: 'Please select a file to upload' }]}
          >
            <Upload {...uploadProps}>
              <Button icon={<UploadOutlined />}>Select File</Button>
            </Upload>
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea 
              rows={4} 
              placeholder="Enter file description (optional)"
              value={description}
              onChange={e => setDescription(e.target.value)}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

// Helper function to get color for file type tag
const getFileTypeColor = (fileType: string): string => {
  const colors: Record<string, string> = {
    image: 'green',
    document: 'blue',
    audio: 'purple',
    video: 'magenta',
    other: 'orange'
  };
  return colors[fileType] || 'default';
};

export default FileList; 