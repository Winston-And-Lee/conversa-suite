import { Padding } from '@/components/padding';
import { formatPhoneNumber } from '@/utils';
import { Flex, Form, FormInstance, Input, Typography } from 'antd';
import { useEffect } from 'react';
import { OtpButtonWithTimer } from '.';

export interface IEnterOtpForm<T> {
  title: string;
  formRef: FormInstance<T>;
  mobilePhone: string;
  referenceToken: string;
  onTimerFinish?: () => void;
  onRequestNewOtp?: () => void;
  onSubmitOtp: (values: T) => void;
  onCancel: () => void;
}

export interface LoginWithOtpFieldType {
  reference_token: string;
  code: string;
}

export const EnterOtpForm = (props: IEnterOtpForm<LoginWithOtpFieldType>) => {
  useEffect(() => {
    if (props.formRef) {
      props.formRef.setFieldsValue({
        reference_token: props.referenceToken
      });
    }
  }, [props.mobilePhone, props.referenceToken, props.formRef]);
  return (
    <>
      <Flex
        style={{
          flexDirection: 'column',
          width: '100%'
        }}
        align='left'
      >
        <Padding vertical={8}>
          <Typography.Title
            level={3}
            style={{
              fontSize: '24px',
              fontWeight: 500,
              lineHeight: '32px',
              textAlign: 'left'
            }}
          >
            {props.title}
          </Typography.Title>
        </Padding>
        <Padding vertical={8}>
          <Typography.Text
            style={{
              fontSize: '14px',
              lineHeight: '24px',
              textAlign: 'left'
            }}
          >
            ระบบได้ส่งส่งรหัส OTP ไปยังเบอร์โทรศัพท์{' '}
            <strong>{props.mobilePhone && formatPhoneNumber(props.mobilePhone)}</strong> <br />
            หากไม่ได้รับสามารถกดขอรหัสใหม่
          </Typography.Text>
        </Padding>
        <Padding vertical={8}>
          <OtpButtonWithTimer
            count={10}
            onStartTimer={() => {
              if (props.onRequestNewOtp) {
                props.onRequestNewOtp();
              }
            }}
            onFinished={() => {
              if (props.onTimerFinish) {
                props.onTimerFinish();
              }
            }}
          />
        </Padding>
        <Padding vertical={8}>
          <Typography.Text
            style={{
              fontSize: '14px',
              lineHeight: '24px',
              textAlign: 'left'
            }}
          >
            รหัสอ้างอิง <strong>{props.referenceToken}</strong>
          </Typography.Text>
        </Padding>
        <Form
          form={props.formRef}
          autoComplete='off'
          layout='vertical'
          onFinish={value => {
            props.onSubmitOtp(value);
          }}
        >
          <Form.Item<LoginWithOtpFieldType>
            label='รหัส OTP ที่ได้รับ (โปรดระบุภายในเวลา 5 นาที)'
            name='code'
            rules={[{ required: true, message: 'กรุณากรอก OTP' }]}
          >
            <Input placeholder='กรอกหัส OTP' />
          </Form.Item>
          <Form.Item<LoginWithOtpFieldType> style={{ display: 'none' }} name='reference_token'>
            <Input placeholder='กรอกหัส OTP' />
          </Form.Item>
        </Form>
      </Flex>
    </>
  );
};
