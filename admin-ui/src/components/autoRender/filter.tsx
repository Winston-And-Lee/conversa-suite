import { ClearOutlined, MinusOutlined, PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { useSelect } from '@refinedev/antd';
import { useTranslate, useUserFriendlyName } from '@refinedev/core';
import type { SelectProps } from 'antd';
import { Button, Card, Col, DatePicker, Form, Input, Row, Select } from 'antd';
import type { FormInstance } from 'antd/es/form';
import React, { useState } from 'react';

import { IAutoRenderFilterProps, IFilterInputSetting, IFilterItemSetting } from '@/interfaces';

const { RangePicker } = DatePicker;

export const filterSettingMapper = (filterSettings: IFilterInputSetting[]) => {
  const filterSettingsMap: any = {};
  filterSettings.forEach((obj: any) => {
    const filterInputNames: string[] = [];
    obj.fields.forEach((field: any) => {
      filterInputNames.push(field);
    });
    filterSettingsMap[filterInputNames.join(',')] = obj;
  });
  return filterSettingsMap;
};

export const FilterItem: React.FC<IFilterItemSetting> = ({
  fields,
  operator,
  nameShow,
  multipleInput,
  optionSelect,
  fieldType
}) => {
  type Langauges = {
    langKey: string;
    value: string;
  };
  let filterInputNames: string[] = [];
  let filterInputNamesV1: string[] = [];
  let filterInputShowNames: string[] = [];
  let filterInputShowNamesV1: Langauges[] = [];
  let langObject: Langauges = {
    langKey: '',
    value: ''
  };
  const getUserFriendlyName = useUserFriendlyName();
  // Name ----------------------------
  fields.forEach(field => {
    filterInputNames.push(field);
    filterInputNamesV1.push(field);
    if (multipleInput) {
      langObject.langKey = field;
      langObject.value = getUserFriendlyName(field, 'plural');

      filterInputShowNames.push(getUserFriendlyName(field, 'plural'));

      filterInputShowNamesV1.push(langObject);
    } else {
      langObject.langKey = field;
      langObject.value = getUserFriendlyName(field, 'singular');

      filterInputShowNames.push(getUserFriendlyName(field, 'singular'));

      filterInputShowNamesV1.push(langObject);
    }
  });

  let elementInput, fieldNameShow;
  if (nameShow) {
    fieldNameShow = nameShow;
  } else {
    fieldNameShow = filterInputShowNames.join(', ');
  }
  const fieldName = filterInputNames.join(',');

  if (!fieldName) {
    return null;
  }
  // ----------------------------

  // Option ----------------------------
  if (optionSelect?.resource || multipleInput) {
    const options: SelectProps['options'] = [];

    optionSelect?.values?.forEach(item => {
      if (item.label) {
        options.push(item);
      } else {
        options.push({ label: item, value: item });
      }
    });
    let selectProps: object = {
      style: { width: '100%' },
      placeholder: `${fieldNameShow}`,
      options: options
    };

    if (optionSelect?.resource) {
      const { selectProps: selectPropResource } = useSelect({
        resource: optionSelect?.resource,
        optionLabel: optionSelect.optionLabel as any,
        optionValue: optionSelect.optionValue as any
      });
      selectProps = { ...selectProps, ...selectPropResource };
    }

    if (multipleInput) {
      selectProps = { ...selectProps, mode: 'multiple', placeholder: `${fieldNameShow} (Multiple)` };

      if (options.length == 0) {
        selectProps = { ...selectProps, mode: 'tags' };
      }
    }

    return (
      <Form.Item name={fieldName} noStyle>
        <Select {...selectProps} />
      </Form.Item>
    );
  }

  if (operator == 'between') {
    if (fieldType == 'datetime') {
      return (
        <Form.Item name={fieldName} label={filterInputShowNames[0]} style={{ marginBottom: 0 }}>
          <RangePicker showTime={true} style={{ width: '100%' }} />
        </Form.Item>
      );
    }
  }

  if (!elementInput) {
    elementInput = (
      <Input style={{ width: '100%' }} name={filterInputShowNames[0]} placeholder={filterInputShowNames[0]} />
    );
  }
  return (
    <Form.Item name={fieldName} noStyle>
      {elementInput}
    </Form.Item>
  );
};

export const AutoRenderFilter: React.FC<IAutoRenderFilterProps> = ({
  searchFormProps,
  filters,
  dataSchema,
  simple,
  advances,
  removeBox
}) => {
  const translate = useTranslate();

  const formRef = React.useRef<FormInstance>(null);
  const [isShowAdvance, setIsShowAdvance] = useState<boolean>(false);

  const mainDataSchema = dataSchema?.['main'];
  const fieldNames = mainDataSchema?.fields.map((item: any) => item.name);
  let fieldSchemaMap: any = {};
  mainDataSchema?.fields.forEach((obj: any) => {
    fieldSchemaMap[obj.name] = obj;
  });

  let filterSettings: IFilterInputSetting[] = [];
  if (advances) {
    filterSettings = [...advances];
  }
  if (simple) {
    filterSettings.push(simple);
  }

  const onReset = () => {
    formRef.current?.resetFields();
  };

  const onAdvance = () => {
    setIsShowAdvance(!isShowAdvance);
  };

  const filterItem = (filterSetting: IFilterInputSetting) => {
    let fields: string[] = [];
    filterSetting.fields.forEach(field => {
      const fieldSplited = field.split('.');
      if (fieldNames?.includes(fieldSplited[0])) {
        fields.push(field);
      }
    });
    if (fields.length == 0) {
      return null;
    }
    const fieldSplited = fields[0].split('.');

    return (
      <FilterItem
        operator={filterSetting.operator}
        // nameShow={"filterSetting.nameShow"}
        // nameShow={translate("orders.titles.custom")}
        nameShow={filterSetting.nameShow}
        multipleInput={filterSetting.multipleInput}
        optionSelect={filterSetting.optionSelect}
        fields={fields}
        fieldType={fieldSchemaMap[fieldSplited[0]].type}
      />
    );
  };

  let advanceStyle = { marginTop: 16, display: 'none' };
  if (isShowAdvance) {
    advanceStyle = { ...advanceStyle, display: '' };
  }

  const FormElement = (
    <Form ref={formRef} {...searchFormProps}>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={24}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '8px'
            }}
          >
            {simple && filterItem(simple)}
            <Button htmlType='submit' type='primary'>
              <SearchOutlined /> {translate('buttons.search')}
            </Button>
            <Button onClick={onReset}>
              <ClearOutlined /> {translate('buttons.reset')}
            </Button>
            {advances && advances.length > 0 && (
              <Button onClick={onAdvance}>
                {isShowAdvance ? (
                  <>
                    <MinusOutlined /> {translate('buttons.hideAdvance')}
                  </>
                ) : (
                  <>
                    <PlusOutlined /> {translate('buttons.advance')}
                  </>
                )}{' '}
              </Button>
            )}
          </div>
        </Col>
      </Row>
      <Row gutter={[16, 16]} style={advanceStyle}>
        {advances?.map((item, index) => {
          const inputElement = filterItem(item);
          if (inputElement) {
            return (
              <Col xs={24} sm={12} md={12} key={index}>
                {inputElement}
              </Col>
            );
          }
          return null;
        })}
      </Row>
    </Form>
  );

  return <>{removeBox ? <>{FormElement}</> : <Card style={{ marginBottom: 10 }}>{FormElement}</Card>}</>;
};
