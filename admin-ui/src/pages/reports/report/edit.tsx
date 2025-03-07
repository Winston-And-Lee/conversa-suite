import { Edit, useForm } from '@refinedev/antd';
import { IResourceComponentsProps } from '@refinedev/core';

import { AutoRenderForm } from '@/components/autoRender/form';
import { CustomLayout } from '@/components/customLayout';

export const ReportEdit: React.FC<IResourceComponentsProps> = () => {
  const { formProps, saveButtonProps, queryResult } = useForm();
  const sellersData = queryResult?.data?.data;

  return (
    <CustomLayout>
      <Edit saveButtonProps={saveButtonProps}>
        <AutoRenderForm
          formProps={formProps}
          dataSchema={sellersData?.__schema}
          data={sellersData}
          hiddenFields={['id']}
        />
      </Edit>
    </CustomLayout>
  );
};
