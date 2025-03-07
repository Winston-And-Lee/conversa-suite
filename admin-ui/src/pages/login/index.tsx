import { AuthenticateTemplate } from '@/layouts/authenticate';
import { useLogin } from '@refinedev/core';
import { Alert, Button, Flex, Input, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { CustomStyledForm } from './layout';

import { GoogleButton, LanguageSwitcher } from '@/components/login_register';
import { MicrosoftButton } from '@/components/login_register/MicrosoftButton';
import { ROUTES } from '@/constant';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTheme } from 'styled-components';

interface FieldType {
  email: string;
  password: string;
}

export const LoginPage = () => {
  const theme = useTheme();
  const { mutate: login } = useLogin();
  const { t } = useTranslation('login');

  const [searchParams, setSearchParams] = useSearchParams();
  const [isVerified, setIsVerfied] = useState<boolean>();
  const handleLogin = (values: FieldType) => {
    login({ email: values.email, password: values.password });
  };

  useEffect(() => {
    setIsVerfied(searchParams.has('verified'));
    setSearchParams({}, { replace: true });
  }, []);

  return (
    <div style={{ position: 'relative' }}>
      <LanguageSwitcher />
      <AuthenticateTemplate decoratedImage='/assets/lottiefiles/login.json'>
        <Typography.Title level={2}>{t('welcomeBack')}</Typography.Title>
        {isVerified && <Alert message={t('emailVerified')} type='success' showIcon style={{ width: '100%' }} />}
        <Flex vertical={false} gap={4} align='center'>
          <Typography.Title level={4} style={{ color: theme.colors.primary_02 }}>
            {t('signin')}
          </Typography.Title>
          <Typography.Title level={4} style={{ margin: 0 }}>
            {t('signInToAccount')}
          </Typography.Title>
        </Flex>

      <GoogleButton />
      <MicrosoftButton />

        <div style={{ width: '100%' }}>
          <CustomStyledForm autoComplete='off' layout='vertical' onFinish={values => handleLogin(values as FieldType)}>
            <CustomStyledForm.Item<FieldType>
              label={t('fields.email')}
              name='email'
              rules={[{ required: true, message: t('errors.emailRequired') }]}
            >
              <Input placeholder={t('placeholders.email')} />
            </CustomStyledForm.Item>
            <CustomStyledForm.Item<FieldType>
              label={t('fields.password')}
              name='password'
              rules={[{ required: true, message: t('errors.passwordRequired') }]}
            >
              <Input.Password placeholder={t('placeholders.password')} />
            </CustomStyledForm.Item>
            <CustomStyledForm.Item style={{ marginBottom: 0 }}>
              <Button type='primary' htmlType='submit' style={{ width: '100%' }}>
                {t('signin')}
              </Button>
            </CustomStyledForm.Item>
          </CustomStyledForm>
        </div>
        <Flex vertical={false} gap={8}>
          <Typography.Text>{t('buttons.noAccount')}</Typography.Text>
          <Typography.Link href={ROUTES.REGISTER} style={{ color: theme.colors.primary_02 }}>
            {t('signup')}
          </Typography.Link>
        </Flex>
      </AuthenticateTemplate>
    </div>
  );
};
