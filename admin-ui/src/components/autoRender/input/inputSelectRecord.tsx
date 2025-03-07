import { useSelect } from '@refinedev/antd';
import { useUserFriendlyName } from '@refinedev/core';
import React from 'react';

import { IInputSelectionForeignKeyProps } from '@/interfaces';
import { Select } from 'antd';

export const InputSelectRecord: React.FC<IInputSelectionForeignKeyProps> = ({ item, value, onChange }) => {
  const getUserFriendlyName = useUserFriendlyName();

  let selectProps: object = {
    style: { width: '100%' },
    placeholder: `Select ${getUserFriendlyName(item.name, 'singular')}`,
    onChange: onChange,
    value: value
  };

  const { selectProps: selectPropResource } = useSelect({
    resource: item?.model,
    optionLabel: 'record_name',
    optionValue: item.references as any,
    defaultValue: value,
    hasPagination: true
  });

  selectProps = { ...selectProps, ...selectPropResource };

  return <Select {...selectProps} />;
};
