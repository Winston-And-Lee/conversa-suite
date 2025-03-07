import { Show } from '@refinedev/antd';
import { IResourceComponentsProps, useShow } from '@refinedev/core';
import React from 'react';

import { AutoRenderShow } from '@/components/autoRender/show';
import { CustomLayout } from '@/components/customLayout';

export const UserShow: React.FC<IResourceComponentsProps> = () => {
  const { queryResult } = useShow();
  const { data, isLoading } = queryResult;

  // const dataSchema = data?.schema;
  const record = data?.data;

  return (
    <CustomLayout>
      <Show isLoading={isLoading}>
        <AutoRenderShow dataSchema={record?.__schema} data={record} hiddenFields={['id', 'user_status']} />
      </Show>
    </CustomLayout>
  );
};
