import { useRegister } from '@refinedev/core';
import { Button, Divider, Flex, Form, Input, Typography } from 'antd';
import { IRegisterField } from '../register';
import { CustomStyledForm } from './layout';

import { USER_VERIFY_TEMP } from '@/api-requests';
import { GoogleButton } from '@/components/login_register';
import { MicrosoftButton } from '@/components/login_register/MicrosoftButton';
import { ROUTES } from '@/constant';
import { UserOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

interface Props {
  onFinish: (user_info: IRegisterField, reference_token: string) => void;
}

export const InformationBox = ({ onFinish }: Props) => {
  const [form] = Form.useForm();
  const { mutate: register } = useRegister<IRegisterField>();
  const { t } = useTranslation('register');

  const handleSignup = (values: IRegisterField) => {
    if (values.password !== values.password_confirm) {
      setInvalidMatchPassword();
      return;
    }

    let domain = window.location.hostname;
    let port = window.location.port;
    if (port) {
      domain = domain.concat(`:${port}`);
    }
    const userInfo = {
      first_name: values.first_name,
      last_name: values.last_name,
      email: values.email,
      password: values.password,
      password_confirm: values.password_confirm,
      domain: domain
    };

    register(userInfo, {
      onSuccess: async data => {
        if (data.success && data.data) {
          const { reference_token } = data.data;
          await localStorage.setItem(
            USER_VERIFY_TEMP,
            JSON.stringify({ email: values.email, userKey: values.password, domain: domain })
          );
          onFinish(userInfo, reference_token);
        } else {
          console.log(data.error);
        }
      }
    });
  };

  const setInvalidMatchPassword = () => {
    form.setFields([
      {
        name: 'password',
        errors: [t('pages.register.information.errors.passwordNotMatch')]
      },
      {
        name: 'password_confirm',
        errors: [t('pages.register.information.errors.passwordNotMatch')]
      }
    ]);
  };

  return (
    <>
      <Typography.Title level={2}>{t('information.title')}</Typography.Title>

      <GoogleButton />
      <MicrosoftButton />

      <Divider plain>{t('information.divider')}</Divider>
      
      <div style={{ width: '100%' }}>
        <CustomStyledForm
          form={form}
          autoComplete='off'
          layout='vertical'
          onFinish={values => handleSignup(values as IRegisterField)}
        >
          <CustomStyledForm.Item<IRegisterField>
            label={t('information.fields.firstName')}
            name='first_name'
            rules={[{ required: true, message: t('information.errors.firstNameRequired') }]}
          >
            <Input placeholder={t('information.placeholders.firstName')} />
          </CustomStyledForm.Item>
          <CustomStyledForm.Item<IRegisterField>
            label='Last Name'
            name='last_name'
            rules={[{ required: true, message: 'Please input your last name' }]}
          >
            <Input placeholder='Last Name' />
          </CustomStyledForm.Item>
          <CustomStyledForm.Item<IRegisterField>
            label='อีเมลล์'
            name='email'
            rules={[{ required: true, message: 'Please input your email' }]}
          >
            <Input placeholder='example@gmail.com' suffix={<UserOutlined />} />
          </CustomStyledForm.Item>
          <CustomStyledForm.Item<IRegisterField>
            label='รหัสผ่าน'
            name='password'
            rules={[{ required: true, message: 'Please input your password' }]}
          >
            <Input.Password placeholder='Password' />
          </CustomStyledForm.Item>
          <CustomStyledForm.Item<IRegisterField>
            label='ยืนยันรหัสผ่าน'
            name='password_confirm'
            rules={[{ required: true, message: 'Please input your password' }]}
          >
            <Input.Password placeholder='Confirm Password' />
          </CustomStyledForm.Item>
          <CustomStyledForm.Item style={{ marginBottom: 0 }}>
            <Button type='primary' htmlType='submit' style={{ width: '100%' }}>
              Sign Up
            </Button>
          </CustomStyledForm.Item>
        </CustomStyledForm>

        {/* <Flex justify="end" style={{ width: "100%" }}>
        <Typography.Text style={{ color: "var(--light_primary_02)" }}>
          Forget Password ?
        </Typography.Text>
      </Flex> */}
      </div>

      <Flex vertical={false} gap={8}>
        <Typography.Text>{t('information.haveAccount')}</Typography.Text>
        <Typography.Link href={ROUTES.WELCOME_LOGIN_REGISTER} style={{ color: 'var(--light_primary_02)' }}>
          {t('information.signin')}
        </Typography.Link>
      </Flex>
    </>
  );
};
