import { Create, useForm } from '@refinedev/antd';
import { IResourceComponentsProps } from '@refinedev/core';
import React from 'react';

import { AutoRenderForm } from '@/components/autoRender/form';
import { CustomLayout } from '@/components/customLayout';
import { useModelSchema } from '@/hooks/useModelSchema';

export const ReportServiceCreate: React.FC<IResourceComponentsProps> = () => {
  const { formProps, saveButtonProps } = useForm();
  const { schema, isLoading } = useModelSchema();

  return (
    <CustomLayout>
      <Create saveButtonProps={saveButtonProps} isLoading={isLoading}>
        <AutoRenderForm formProps={formProps} dataSchema={schema} />
      </Create>
    </CustomLayout>
  );
};
