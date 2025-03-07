import { useUserFriendlyName } from '@refinedev/core';
import { Col, Form, Row } from 'antd';
import React from 'react';

import { renderShowField } from './fields';

interface IAutoRenderShowProps {
  dataSchema: any;
  data: any;
  hiddenFields?: string[];
  showFields?: string[];
  customFields?: any;
}

export const AutoRenderShow: React.FC<IAutoRenderShowProps> = ({
  dataSchema,
  data,
  hiddenFields,
  showFields,
  customFields
}) => {
  const getUserFriendlyName = useUserFriendlyName();

  const mainDataSchema = dataSchema?.['main'];

  return (
    <Form layout='vertical'>
      <Row gutter={16}>
        {mainDataSchema?.fields.map((item: any, index: number) => {
          if (showFields && !showFields?.includes(item.name)) {
            return null;
          }

          if (hiddenFields && hiddenFields?.includes(item.name)) {
            return null;
          }

          if (item.action == 'hide') {
            return null;
          }

          return (
            <Col key={index} xs={24} md={12}>
              <Form.Item label={getUserFriendlyName(item.name, 'singular')} name={item.name}>
                {renderShowField(item, data)}
              </Form.Item>
            </Col>
          );
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
