import { Breadcrumb, List, ListProps } from '@refinedev/antd';
import { ReactNode } from 'react';
import styled from 'styled-components';

interface Props extends ListProps {
  title?: string;
  children?: ReactNode;
  isShowBreadcrumb?: boolean;
}

export const CustomList: React.FC<Props> = ({ isShowBreadcrumb = true, ...props }) => {
  const { title, children } = props;
  return (
    <StyledDiv>
      <List breadcrumb={isShowBreadcrumb ? <Breadcrumb hideIcons /> : false} title={title} {...props}>
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
