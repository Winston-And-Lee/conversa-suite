import { CustomLayout } from '@/components/customLayout';
import { Show } from '@refinedev/antd';
import { IResourceComponentsProps, useShow } from '@refinedev/core';
import React from 'react';

import { AutoRenderShow } from '@/components/autoRender/show';

export const ReportServiceShow: React.FC<IResourceComponentsProps> = () => {
  const { queryResult } = useShow();
  const { data, isLoading } = queryResult;

  const record = data?.data;

  return (
    <CustomLayout>
      <Show isLoading={isLoading}>
        <AutoRenderShow dataSchema={record?.__schema} data={record} hiddenFields={['id', 'password']} />
      </Show>
    </CustomLayout>
  );
};
