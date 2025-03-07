import { resendOtpRequest, verifyOtpRequest } from '@/api-requests/otp';
import { Button, Flex, Input, notification, Typography } from 'antd';
import { useCallback, useEffect, useState } from 'react';
import { IRegisterField } from '../register';
import { BackButton } from './layout';

import { ROUTES } from '@/constant';
import { useNotification } from '@refinedev/core';
import { useTranslation } from 'react-i18next';
import { useNavigate, useSearchParams } from 'react-router-dom';

const RESEND_OTP_SEC = 30;

interface IOtpBoxProps {
  onBack: () => void;
  onFinish: () => void;
  userInfo: IRegisterField;
  referenceToken: string;
}

export const OtpBox = ({ userInfo, referenceToken, onFinish, onBack }: IOtpBoxProps) => {
  const navigate = useNavigate();
  const { t } = useTranslation('register');

  const { close, open } = useNotification();
  const [api, contextHolder] = notification.useNotification();

  const [searchParams, setSearchParams] = useSearchParams();
  const referenceTokenParam = searchParams.get('reference_token') ?? '';
  const codeParam = searchParams.get('code') ?? '';

  // resend otp interval
  const [currentOtpInterval, setCurrentOtpInterval] = useState<number>(0);
  const [otp, setOtp] = useState<string>('');
  const [currentReferenceToken, setCurrentReferenceToken] = useState<string>(referenceToken);
  const [hasVerifyRun, setHasVerifyRun] = useState<boolean>(false);

  useEffect(() => {
    if (referenceTokenParam && codeParam) {
      setHasVerifyRun(true);

      const handler = setTimeout(() => {
        setSearchParams({});
        verifyOtp(referenceTokenParam, codeParam);
      }, 500);

      return () => {
        clearTimeout(handler);
      };
    }
  }, [referenceTokenParam, codeParam, hasVerifyRun]);

  const handleOtpChange = (value: string) => {
    setOtp(value);
  };

  const handleClickResend = useCallback(async () => {
    if (currentOtpInterval > 0) return;
    try {
      // resend otp
      let domain = window.location.hostname;
      let port = window.location.port;
      if (port) {
        domain = domain.concat(`:${port}`);
      }
      const request = {
        email: userInfo.email,
        domain: domain
      };

      const response = await resendOtpRequest(request);
      if (response) {
        const referenceToken = response.reference_token;
        setCurrentReferenceToken(referenceToken);
        setOtp('');
      }
    } catch (_error) {
      const error = _error as Error;

      api['error']({
        message: 'Resend OTP Failed',
        description: error.message
      });

      return;
    }

    const interval = setInterval(() => {
      setCurrentOtpInterval(prev => {
        if (prev === 0) {
          return RESEND_OTP_SEC;
        } else if (prev === 1) {
          clearInterval(interval);
          return prev - 1;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [currentOtpInterval, currentReferenceToken]);

  const verifyOtp = async (token: string, otpNumber: string) => {
    try {
      const user = await verifyOtpRequest(token, otpNumber);
      if (!user) {
        api['error']({
          message: 'Validate OTP Failed'
        });
        return;
      }
    } catch (_error) {
      // TODO: handle error case here
      api['error']({
        message: 'Validate OTP Failed',
        description: false
      });

      if (hasVerifyRun) {
        navigate(`/${ROUTES.WELCOME_LOGIN_REGISTER}`);
      }
      return;
    }

    onFinish();
  };

  const handleVerifyOtp = async () => {
    if (!otp) {
      api['error']({
        message: 'Validate OTP Failed',
        description: 'Please enter OTP code correctly'
      });
      return;
    }

    verifyOtp(currentReferenceToken, otp);
  };

  return (
    <>
      {contextHolder}
      <Flex vertical={false} justify='start' style={{ width: '100%' }}>
        <BackButton onClick={onBack} />
      </Flex>
      {currentReferenceToken ? (
        <>
          <Flex vertical={true} gap={16} align='center'>
            <Typography.Title level={2}>{t('otp.title')}</Typography.Title>
            <Typography.Title level={4} style={{ marginTop: 0 }}>
              {t('otp.subtitle')}
            </Typography.Title>
            <div>
              <Typography.Text>
                {t('pages.register.otp.reference')} (<b>{currentReferenceToken}</b>)
              </Typography.Text>
            </div>
          </Flex>

          <div style={{ width: 340 }}>
            <Input.OTP value={otp} length={6} onChange={handleOtpChange} style={{ width: '100%' }} />
          </div>

          <Flex vertical={true} gap={16} align='center' style={{ width: '100%' }}>
            <Button type='text'>
              <Typography.Link style={{ color: 'var(--light_primary_02)' }} onClick={handleClickResend}>
                Resend {currentOtpInterval ? `(${currentOtpInterval}s)` : ''}
              </Typography.Link>
            </Button>
            <Button type='primary' htmlType='submit' style={{ width: '100%' }} onClick={handleVerifyOtp}>
              {t('pages.register.otp.buttons.confirm')}
            </Button>
          </Flex>
        </>
      ) : (
        <>
          <Flex vertical={true} gap={16} align='center'>
            <Typography.Title level={2}>{t('otp.title')}</Typography.Title>
          </Flex>

          <Flex vertical={true} gap={16} align='center' style={{ width: '100%' }}>
            <Button type='primary' htmlType='submit' style={{ width: '100%' }} onClick={handleClickResend}>
              {t('pages.register.otp.buttons.send')}
            </Button>
          </Flex>
        </>
      )}
    </>
  );
};
