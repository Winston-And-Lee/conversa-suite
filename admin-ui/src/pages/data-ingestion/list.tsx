import { DeleteButton, EditButton, ShowButton } from '@refinedev/antd';
import React from 'react';
import { useTranslation } from 'react-i18next';

import { AutoRenderFilterV2 } from '@/components/autoRender/filterv2';
import { CustomList } from '@/components/customList';
import { PaginationComponent } from '@/components/customPagination';
import { CustomTable } from '@/components/tableComponent';
import { ROUTES } from '@/constant';
import { useFilterTableV2 } from '@/hooks/useFilterTablev2';
import { convertDate } from '@/utils';
import { Space, Table, Tag, Typography } from 'antd';

const { Link } = Typography;

export const DataIngestionList = () => {
  const { t } = useTranslation();

  const { filterProps, tableProps, setCurrent, setPageSize, tableQueryResult } = useFilterTableV2({
    resource: 'data-ingestion',
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
      permanent: []
    },
    simples: [
      {
        fields: 'title',
        operator: 'contains',
        multipleInput: false
      },
      {
        fields: 'data_type',
        operator: 'eq',
        multipleInput: true,
        optionSelect: {
          values: ['ตัวบทกฎหมาย', 'FAQ', 'FICTION']
        }
      }
    ]
  });

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <CustomList>
        <AutoRenderFilterV2 {...filterProps} {...tableQueryResult} />
        <CustomTable size='small' {...(tableProps as any)} rowKey='id' pagination={false}>
          <Table.Column
            key='title'
            dataIndex='title'
            fixed='left'
            title='หัวข้อ'
            render={(value, record: any) => {
              return <Link href={`/${ROUTES.DATA_INGESTION}/${record.id}`}>{value}</Link>;
            }}
          />

          <Table.Column
            key='data_type'
            dataIndex='data_type'
            title='ประเภทข้อมูล'
            render={value => <Typography.Text>{value || '-'}</Typography.Text>}
          />

          <Table.Column
            align='center'
            key='keywords'
            dataIndex='keywords'
            title='คีย์เวิร์ด'
            render={value => {
              const returnTags: any = [];
              value?.forEach((element: any) => {
                returnTags.push(<Tag key={element}>{element}</Tag>);
              });
              return <>{returnTags}</>;
            }}
          />

          <Table.Column
            key='created_at'
            dataIndex='created_at'
            title='วันที่สร้าง'
            render={value => (
              <Typography.Text>{value ? convertDate(value, 'DD/MM/YYYY, HH:mm:ss', 'th') : '-'}</Typography.Text>
            )}
            sorter
          />

          <Table.Column
            title='การกระทำ'
            dataIndex='actions'
            fixed='right'
            render={(_, record: any) => (
              <Space>
                <ShowButton hideText size='small' recordItemId={record.id} />
                <EditButton hideText size='small' recordItemId={record.id} />
                <DeleteButton hideText size='small' recordItemId={record.id} />
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
    </div>
  );
};

export default DataIngestionList; 