import { DeleteButton, EditButton, ShowButton } from '@refinedev/antd';
import { BaseRecord, IResourceComponentsProps } from '@refinedev/core';
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

export const ReportList: React.FC<IResourceComponentsProps> = () => {
  const { t } = useTranslation('reports');

  const { filterProps, tableProps, setCurrent, setPageSize, tableQueryResult } = useFilterTableV2({
    simples: [
      {
        fields: 'name',
        operator: 'contains',
        multipleInput: false
      },
      {
        fields: 'type',
        operator: 'eq',
        multipleInput: true,
        optionSelect: {
          values: ['dashboard']
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
            key='name'
            dataIndex='name'
            fixed='left'
            title={t('list.name')}
            render={(value, record: any) => {
              return <Link href={`/${ROUTES.REPORTS}/${record.id}`}>{value}</Link>;
            }}
          />

          <Table.Column
            align='center'
            key='tags'
            dataIndex='tags'
            title={t('list.tags')}
            render={value => {
              const returnTags: any = [];
              value?.forEach((element: any) => {
                returnTags.push(<Tag>{element}</Tag>);
              });
              return <>{returnTags}</>;
            }}
          />
          <Table.Column
            key='updated_at'
            dataIndex='updated_at'
            title={t('list.updatedAt')}
            render={value => (
              <Typography.Text>{value ? convertDate(value, 'DD/MM/YYYY, HH:mm:ss', 'th') : '-'}</Typography.Text>
            )}
            sorter
          />
          <Table.Column
            title={t('table.actions')}
            dataIndex='actions'
            fixed='right'
            render={(_, record: BaseRecord) => (
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
