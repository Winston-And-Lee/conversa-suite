import { Button, ButtonProps, Flex, Select } from "antd";
import { ReactNode } from "react";
import styled from "styled-components";

interface SquareButtonProps extends ButtonProps {
  onClick?: any;
  children?: ReactNode;
}

export const SquareButtonWithIcon: React.FC<SquareButtonProps> = (props) => {
  const { children, onClick } = props;
  return (
    <Button onClick={onClick} {...props}>
      <Flex justify="center" align="center" gap={8}>
        {children}
      </Flex>
    </Button>
  );
};

export const SearchInput = styled(Select)`
  .ant-select-selector {
    margin-right: 8px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0; 
  }
`;

export const SearchDropdownSelect = styled(Select)`
  .ant-select-selector {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
  }
`;
