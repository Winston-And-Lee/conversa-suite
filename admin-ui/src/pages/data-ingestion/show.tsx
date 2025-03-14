import { Show } from '@refinedev/antd';
import { useShow } from '@refinedev/core';
import React from 'react';
import { useTranslation } from 'react-i18next';

import { convertDate } from '@/utils';
import { Descriptions, Space, Tag, Typography } from 'antd';

export const DataIngestionShow = () => {
  const { t } = useTranslation();
  const { queryResult } = useShow();
  const { data, isLoading } = queryResult;
  const record = data?.data;

  return (
    <Show isLoading={isLoading} title="ข้อมูลกฎหมาย">
      <Descriptions bordered column={1}>
        <Descriptions.Item label="หัวข้อ">{record?.title}</Descriptions.Item>
        <Descriptions.Item label="ประเภทข้อมูล">{record?.data_type}</Descriptions.Item>
        <Descriptions.Item label="ระบุ">{record?.specified_text}</Descriptions.Item>
        <Descriptions.Item label="เนื้อหา">{record?.content}</Descriptions.Item>
        <Descriptions.Item label="อ้างอิง">{record?.reference}</Descriptions.Item>
        <Descriptions.Item label="คีย์เวิร์ด">
          <Space wrap>
            {record?.keywords?.map((keyword: string) => (
              <Tag key={keyword}>{keyword}</Tag>
            ))}
          </Space>
        </Descriptions.Item>
        {record?.webpage_url && (
          <Descriptions.Item label="URL เว็บไซต์">
            <Typography.Link href={record.webpage_url} target="_blank">
              {record.webpage_url}
            </Typography.Link>
          </Descriptions.Item>
        )}
        {record?.file_url && (
          <Descriptions.Item label="ไฟล์">
            <Typography.Link href={record.file_url} target="_blank">
              {record.file_name || record.file_url}
            </Typography.Link>
          </Descriptions.Item>
        )}
        <Descriptions.Item label="วันที่สร้าง">
          {record?.created_at ? convertDate(record.created_at, 'DD/MM/YYYY, HH:mm:ss', 'th') : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="วันที่แก้ไข">
          {record?.updated_at ? convertDate(record.updated_at, 'DD/MM/YYYY, HH:mm:ss', 'th') : '-'}
        </Descriptions.Item>
      </Descriptions>
    </Show>
  );
};

export default DataIngestionShow; 