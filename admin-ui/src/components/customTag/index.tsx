import { Tag, TagProps } from 'antd';
import { ReactNode } from 'react';
import styled from 'styled-components';

interface Props extends TagProps {
  children?: ReactNode;
  size?: 'small' | 'medium' | 'large';
}

export const CustomTag: React.FC<Props> = props => {
  const { size, children } = props;
  return (
    <StyledTag size={size} {...props}>
      {children}
    </StyledTag>
  );
};

const StyledTag = styled(Tag)<{ size?: string }>`
  font-size: ${({ size }) => {
    switch (size) {
      case 'small':
        return '14px';
      case 'large':
        return '16px';
      default:
        return '14px';
    }
  }};
  padding: ${({ size }) => {
    switch (size) {
      case 'small':
        return '0 8px';
      case 'large':
        return '5px 8px';
      default:
        return '4px 8px';
    }
  }};
  minheight: ${({ size }) => {
    switch (size) {
      case 'small':
        return '16px';
      case 'large':
        return '32px';
      default:
        return '24px';
    }
  }};
`;
