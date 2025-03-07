import { Flex } from 'antd';
import { styled } from 'styled-components';

export const Container = styled(Flex)(() => ({
  position: 'fixed',
  flexDirection: 'row',
  width: '100dvw',
  height: '100dvh'
}));

export const BlueBg = styled('div')(({ theme }) => ({
  position: 'absolute',
  backgroundColor: theme.colors.primary_02,
  width: '50%',
  height: '100%'
}));

export const WhiteBg = styled('div')(() => ({
  position: 'absolute',
  left: '50%',
  backgroundColor: 'white',
  width: '50%',
  height: '100%',
  maxWidth: 400,
  flex: 1
}));

export const MainFormBox = styled(Flex)(({ theme }) => ({
  gap: 16,
  flexDirection: 'column',
  borderRadius: 8,
  backgroundColor: theme.colors.neutral_12,
  padding: '40px 16px',
  minWidth: 400,
  justifyContent: 'center',
  alignItems: 'center',
  boxShadow: '0px 0px 10px 5px rgba(0, 0, 0, 0.15)'
}));

export const ContentContainer = styled(Flex)(() => ({
  flexDirection: 'row',
  justifyContent: 'space-between',
  alignItems: 'center',
  zIndex: 10,
  height: '100%',

  width: '100%',
  maxWidth: 'min(1920px, 100%)',
  gap: 60,
  margin: '0 auto'
}));

export const TemplateIcon = styled('img')(() => ({
  position: 'absolute',
  width: 50,
  height: 50,
  left: 32,
  top: 32
}));
