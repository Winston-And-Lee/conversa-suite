import { Button, ButtonProps, Flex } from 'antd';
import { ReactNode } from 'react';

interface ISquareButtonProps extends ButtonProps {
  onClick?: any;
  children?: ReactNode;
}

export const SquareButtonWithIcon: React.FC<ISquareButtonProps> = props => {
  const { children, onClick } = props;
  return (
    <Button style={{ boxShadow: 'none' }} onClick={onClick} {...props}>
      <Flex justify='center' align='center' gap={8}>
        {children}
      </Flex>
    </Button>
  );
};
