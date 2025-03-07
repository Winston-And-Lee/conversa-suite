import { useTranslate, useUserFriendlyName } from '@refinedev/core';
import React from 'react';
// import { Show, NumberField, TagField, TextField, MarkdownField } from "@refinedev/antd";
import { Col, Form, Row } from 'antd';

import { convertValidatorStringToObject, renderFormField } from './fields';
interface AutoRenderFormProps {
  dataSchema: any;
  formProps: any;
  data?: any;
  hiddenFields?: string[];
  customFields?: any;
}

export const AutoRenderForm: React.FC<AutoRenderFormProps> = ({
  dataSchema,
  formProps,
  data,
  hiddenFields,
  customFields
}) => {
  const translate = useTranslate();
  const getUserFriendlyName = useUserFriendlyName();

  const mainDataSchema = dataSchema?.['main'];

  const renderFormFields: any[] = [];
  // get record fields
  const mainSchemaRecordFieldsMap: any = {};
  const mainForeignKeyFields: string[] = [];

  // Find Record file
  mainDataSchema?.fields.map((item: any, index: number) => {
    if (item.type == 'record') {
      mainSchemaRecordFieldsMap[item.name] = item.fields;
      mainForeignKeyFields.push(item.foreignKey);
    }
  });

  // Prepare form fields
  mainDataSchema?.fields.map((item: any, index: number) => {
    if (hiddenFields && hiddenFields?.includes(item.name)) {
      return null;
    }
    // viewonly , createonly, all
    if (
      !mainForeignKeyFields?.includes(item.name) &&
      (item.action == 'all' ||
        item.action == 'secret' ||
        item.action == 'hide' ||
        (item.action == 'viewonly' && data) ||
        (item.action == 'createonly' && !data))
    ) {
      item.validators = item.validation && convertValidatorStringToObject(item.validation);
      item.inputName = [item.name];

      if (item.type == 'record') {
        item.inputName = [item.foreignKey];
      }

      renderFormFields.push(item);
    }
  });

  return (
    <Form {...formProps} layout='vertical'>
      <Row gutter={16}>
        {renderFormFields.map((item: any, index: number) => {
          if (customFields && customFields[item.name]) {
            return null;
          } else {
            const inputItemProps: any = {};
            if (item.type == 'boolean') {
              inputItemProps.valuePropName = 'checked';
            }
            return (
              <Col key={index} xs={24} md={12}>
                <Form.Item
                  label={getUserFriendlyName(item.name, 'singular')}
                  name={item.inputName}
                  rules={[
                    {
                      required: item.validators?.required
                    }
                  ]}
                  {...inputItemProps}
                >
                  {renderFormField(item, data)}
                </Form.Item>
              </Col>
            );
          }
        })}
        {customFields &&
          Object.keys(customFields).map((key, index) => {
            return (
              <Col key={index} xs={24} md={12}>
                {customFields[key]}
              </Col>
            );
          })}
      </Row>
    </Form>
  );
};
