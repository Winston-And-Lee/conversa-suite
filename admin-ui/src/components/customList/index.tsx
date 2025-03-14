import { Breadcrumb, List } from '@refinedev/antd';
import { ListProps } from '@refinedev/antd/dist/components/pages/list';
import React, { ReactNode } from 'react';
import styled from 'styled-components';

interface Props extends Omit<ListProps, 'headerButtons'> {
  title?: string;
  children?: ReactNode;
  isShowBreadcrumb?: boolean;
  headerButtons?: React.ReactNode[];
}

export const CustomList: React.FC<Props> = ({ isShowBreadcrumb = true, headerButtons, ...props }) => {
  const { title, children } = props;
  return (
    <StyledDiv>
      <List 
        breadcrumb={isShowBreadcrumb ? <Breadcrumb hideIcons /> : false} 
        title={title} 
        headerButtons={headerButtons}
        {...props}
      >
        {children}
      </List>
    </StyledDiv>
  );
};

const StyledDiv = styled.div`
  padding-left: 24px;
  padding-top: 18px;
  height: 100%;

  & > div {
    height: 100%;

    & > .ant-page-header {
      height: 100%;
    }
  }
`;
