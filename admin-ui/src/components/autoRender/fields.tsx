import { CheckOutlined, CloseOutlined, CopyOutlined } from '@ant-design/icons';
import { TextField } from '@refinedev/antd';
import { Input, InputNumber, message, Switch, Tooltip, Typography } from 'antd';

import { convertDate, getType } from '@/utils';
import { InputSelectRecord } from './input/inputSelectRecord';

type ParsedValidatorObject = {
  [key: string]: boolean | number | string;
};

export const convertValidatorStringToObject = (str: string): ParsedValidatorObject => {
  const obj: ParsedValidatorObject = {};
  const parts = str.split(',');

  for (let part of parts) {
    if (part.includes('=')) {
      const [key, value] = part.split('=');
      obj[key] = parseInt(value, 10);
    } else {
      obj[part] = true;
    }
  }
  return obj;
};

export const renderFormField = (item: any, data: any) => {
  let inputProps: any = {};

  if (item.action == 'viewonly') {
    return <>{renderShowField(item, data)}</>;
  }

  const validators = item.validation && convertValidatorStringToObject(item.validation);

  if (item.type == 'record') {
    return <InputSelectRecord item={item} value={''} />;
  }

  if (item.type === 'boolean') {
    return <Switch checkedChildren={<CheckOutlined />} unCheckedChildren={<CloseOutlined />} />;
  }

  if (validators?.min) {
    inputProps.min = validators.min;
  }
  if (validators?.max) {
    inputProps.maxLength = validators.max;
  } else if (item.type == 'string') {
    inputProps.maxLength = 255;
  }
  if (item.action == 'secret') {
    return <Input.Password {...inputProps} />;
  }

  if (item.type == 'int') {
    return <InputNumber {...inputProps} style={{ width: '100%' }} />;
  }

  if (item.type == 'decimal') {
    return <InputNumber {...inputProps} style={{ width: '100%' }} />;
  }

  return <Input {...inputProps} showCount={true} />;
};

export const renderShowField = (item: any, data: any) => {
  let value = data?.[item.name];
  const typeOfValue = getType(value);
  let FieldElement;

  if (!value) {
    value = '-';
  }

  if (typeOfValue === 'object') {
    FieldElement = <div>{JSON.stringify(value)}</div>;
  } else if (typeOfValue === 'array') {
    FieldElement = <div>{value.join(', ')}</div>;
  } else if (typeOfValue === 'boolean') {
    return (
      <Typography>
        <Switch
          checkedChildren={<CheckOutlined />}
          unCheckedChildren={<CloseOutlined />}
          checked={data?.[item.name]}
          disabled
        />
      </Typography>
    );
  } else {
    if (item.type === 'datetime') {
      FieldElement = (
        <Typography.Text>{value ? convertDate(value, 'DD/MM/YYYY, HH:mm:ss', 'th') : '-'}</Typography.Text>
      );
    } else {
      // For other types (like string, number)
      FieldElement = <TextField value={value} />;
    }
  }
  return (
    <Typography>
      <pre style={{ margin: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>{FieldElement}</span>
        <Tooltip title='Copy to Clipboard'>
          <CopyOutlined
            onClick={() => {
              navigator.clipboard.writeText(value);
              message.success('Copied to clipboard');
            }}
            style={{ marginLeft: 8, cursor: 'pointer' }}
          />
        </Tooltip>
      </pre>
    </Typography>
  );
};
