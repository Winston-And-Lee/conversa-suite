import { Button, Flex, Form, Typography } from 'antd';
import * as SolarIconSet from 'solar-icon-set';
import { styled } from 'styled-components';

export const CustomStyledForm = styled(Form)(() => ({
  '.ant-form-item': {
    marginBottom: 16
  }
}));

interface BackButtonProps {
  onClick: () => void;
}

export const BackButton = ({ onClick }: BackButtonProps) => {
  return (
    <Button type='text' onClick={onClick}>
      <Flex vertical={false} align='center'>
        <SolarIconSet.ArrowLeft color={'var(--light_primary_02)'} size={14} iconStyle='Outline' />
        <Typography.Text style={{ marginLeft: 8 }}>Back</Typography.Text>
      </Flex>
    </Button>
  );
};
