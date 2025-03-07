import { LeftOutlined } from '@ant-design/icons';
import { Breadcrumb, BreadcrumbProps, Create, PageHeaderProps } from '@refinedev/antd';
import { CardProps } from 'antd';
import React from 'react';

import styled from 'styled-components';

type ActionButtonRenderer<TExtraProps extends {} = Record<keyof any, unknown>> =
  | ((context: { defaultButtons: React.ReactNode } & TExtraProps) => React.ReactNode)
  | React.ReactNode;

const CustomCreateStyled = styled.div`
  & > * > .ant-page-header > .ant-page-header-heading {
    padding: 0 16px;
  }

  &
    > *
    > .ant-page-header
    > .ant-page-header-content
    > .ant-spin-nested-loading
    > .ant-spin-container
    > .ant-card
    > .ant-card-actions {
    display: none;
  }

  &.open-footer
    > *
    > .ant-page-header
    > .ant-page-header-content
    > .ant-spin-nested-loading
    > .ant-spin-container
    > .ant-card
    > .ant-card-actions {
    display: none;
  }

  & > * > .ant-page-header > .ant-page-header-content {
    padding: 0;
  }

  &
    > *
    > .ant-page-header
    > .ant-page-header-content
    > .ant-spin-nested-loading
    > .ant-spin-container
    > .ant-card
    > .ant-card-body {
    padding: 16px;
  }

  .ant-page-header-heading-left {
    display: flex;
    width: 100%;
  }

  .ant-page-header-heading-sub-title {
    flex: 1;
  }
`;

interface CustomCreate {
  children: React.ReactNode;
  title?: string;
  contentProps?: CardProps;
  breadcrumb?: React.FC<BreadcrumbProps>;
  openFooterAction?: boolean;
  openHeaderAction?: boolean;
  isLoading?: boolean;
  headerProps?: PageHeaderProps;
  headerButtons?: ActionButtonRenderer;
}

export const CustomCreate: React.FC<CustomCreate> = ({
  children,
  title,
  openFooterAction = true,
  openHeaderAction = true,
  isLoading = false,
  ...props
}: CustomCreate) => {
  return (
    <CustomCreateStyled className={`${openFooterAction ? 'open-footer' : ''}`}>
      <Create
        {...(title ? { title: title } : {})}
        isLoading={isLoading ?? false}
        wrapperProps={{
          style: {
            backgroundColor: '#F2F4F7'
          }
        }}
        goBack={<LeftOutlined />}
        breadcrumb={
          <div
            style={{
              padding: '16px 24px',
              marginBottom: '16px',
              backgroundColor: '#fff'
            }}
          >
            {props.breadcrumb ? <props.breadcrumb /> : <Breadcrumb hideIcons />}
          </div>
        }
        contentProps={{
          style: {
            backgroundColor: '#F2F4F7'
          },
          ...props.contentProps
        }}
        headerProps={props.headerProps}
        headerButtons={openHeaderAction ? props.headerButtons : () => null}
      >
        {children}
      </Create>
    </CustomCreateStyled>
  );
};
