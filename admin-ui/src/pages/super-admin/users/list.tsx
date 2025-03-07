import { AutoRenderFilterV2 } from '@/components/autoRender/filterv2';
import { CustomList } from '@/components/customList';
import { PaginationComponent } from '@/components/customPagination';
import { CustomTable } from '@/components/tableComponent';
import { useFilterTableV2 } from '@/hooks/useFilterTablev2';
import { UserStatus } from '@/pages/super-admin/users/components/userStatus';
import { convertDate } from '@/utils';
import { ShowButton, TextField } from '@refinedev/antd';
import { BaseRecord, IResourceComponentsProps, useTranslate } from '@refinedev/core';
import { Space, Table, Typography } from 'antd';
import React from 'react';

export const UserList: React.FC<IResourceComponentsProps> = () => {
  const translate = useTranslate();

  const { filterProps, tableProps, setCurrent, setPageSize, tableQueryResult } = useFilterTableV2({
    simples: [
      {
        fields: 'first_name',
        operator: 'contains',
        multipleInput: false
      },
      {
        fields: 'last_name',
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
            key='first_name'
            dataIndex='first_name'
            title='First Name'
            render={value => <TextField value={value} />}
          />
          <Table.Column
            key='last_name'
            dataIndex='last_name'
            title='Last Name'
            render={value => <TextField value={value} />}
          />
          <Table.Column
            key='birth_date'
            dataIndex='birth_date'
            title='Birth Date'
            render={value => <Typography.Text>{value ? convertDate(value, 'DD/MM/YYYY', 'th') : '-'}</Typography.Text>}
          />
          <Table.Column
            key='user_status'
            dataIndex='user_status'
            title='Status'
            render={value => <UserStatus status={value} />}
          />
          <Table.Column key='email' dataIndex='email' title='Email' render={value => <TextField value={value} />} />
          <Table.Column key='mobile' dataIndex='mobile' title='Mobile' render={value => <TextField value={value} />} />
          <Table.Column
            key='created_at'
            dataIndex='created_at'
            title='Created Date'
            render={value => (
              <Typography.Text>{value ? convertDate(value, 'DD/MM/YYYY, HH:mm:ss', 'th') : '-'}</Typography.Text>
            )}
          />
          <Table.Column
            key='updated_at'
            dataIndex='updated_at'
            title='Updated Date'
            render={value => (
              <Typography.Text>{value ? convertDate(value, 'DD/MM/YYYY, HH:mm:ss', 'th') : '-'}</Typography.Text>
            )}
          />
          <Table.Column
            title={translate('table.actions')}
            dataIndex='actions'
            render={(_, record: BaseRecord) => (
              <Space>
                <ShowButton hideText size='small' recordItemId={record.id} />
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
