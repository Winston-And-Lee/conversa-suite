import { EditButton, ShowButton } from '@refinedev/antd';
import { BaseRecord, IResourceComponentsProps, useTranslate } from '@refinedev/core';
import React from 'react';

import { Space, Table, Typography } from 'antd';

import { AutoRenderFilterV2 } from '@/components/autoRender/filterv2';
import { CustomList } from '@/components/customList';
import { PaginationComponent } from '@/components/customPagination';
import { CustomTable } from '@/components/tableComponent';
import { ROUTES } from '@/constant';
import { useFilterTableV2 } from '@/hooks/useFilterTablev2';
import { convertDate } from '@/utils';

const { Link } = Typography;

export const ReportServiceList: React.FC<IResourceComponentsProps> = () => {
  const translate = useTranslate();
  const { filterProps, tableProps, setCurrent, setPageSize, tableQueryResult } = useFilterTableV2({
    simples: [
      {
        fields: 'name',
        operator: 'contains',
        multipleInput: false
      }
    ]
  });

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <CustomList>
        <AutoRenderFilterV2 {...filterProps} {...tableQueryResult} />
        <CustomTable size='small' {...(tableProps as any)} rowKey='id' pagination={false}>
          <Table.Column
            key='id'
            dataIndex='id'
            title={translate('table.id')}
            render={(value, _) => (
              <Link target='_blank' href={value}>
                {value}
              </Link>
            )}
          />
          <Table.Column
            key='name'
            dataIndex='name'
            fixed='left'
            title={translate('table.name')}
            render={(value, record: any) => {
              return <Link href={`/${ROUTES.ADMIN_REPORT_SERVICE}/${record.id}`}>{value}</Link>;
            }}
          />
          <Table.Column
            key='url'
            dataIndex='url'
            title={translate('table.service')}
            render={(value, _) => (
              <Link target='_blank' href={value}>
                {value}
              </Link>
            )}
          />
          <Table.Column
            key='created_at'
            dataIndex='created_at'
            title={translate('table.createdAt')}
            render={value => (
              <Typography.Text>{value ? convertDate(value, 'DD/MM/YYYY, HH:mm:ss', 'th') : '-'}</Typography.Text>
            )}
            sorter
          />

          <Table.Column
            key='updated_at'
            dataIndex='updated_at'
            title={'Updated At'}
            render={value => (
              <Typography.Text>{value ? convertDate(value, 'DD/MM/YYYY, HH:mm:ss', 'th') : '-'}</Typography.Text>
            )}
            sorter
          />
          <Table.Column
            title={translate('table.actions')}
            dataIndex='actions'
            fixed='right'
            render={(_, record: BaseRecord) => (
              <Space>
                <ShowButton hideText size='small' recordItemId={record.id} />
                <EditButton hideText size='small' recordItemId={record.id} />
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
