import { useLogin } from '@refinedev/core';
import { Spin } from 'antd';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { LOGIN_REQUEST, SOURCE_AUTH } from '@/constant/authConfig';
import { useMsal } from '@azure/msal-react';
import { Button } from 'antd';

export const MicrosoftButton = (): JSX.Element => {
  const [loading, setLoading] = useState<boolean>(false);
  const { instance } = useMsal();
  const { mutate: login } = useLogin();
  const { t } = useTranslation();

  const handleLoginMicrosoft = async () => {
    setLoading(true);
    try {
      const res = await instance.loginPopup(LOGIN_REQUEST);
      if (res?.accessToken) {
        login({ credentials: res.accessToken, source: SOURCE_AUTH.MICROSOFT });
      }
    } catch (error) {
      // Error handling for Microsoft login
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const handleFocus = () => setLoading(false);
    window.addEventListener('focus', handleFocus);

    return () => {
      // remove event focus.
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  return (
    <>
      <Button
        className='custom-microsoft-button'
        type='default'
        style={{ width: 200, fontSize: 14, height: 32, borderRadius: 4, fontWeight: 500, opacity: 0.9 }}
        icon={
          <img
            src='/images/login/ms-pictogram.svg'
            alt='Microsoft Login'
            style={{ width: 15, height: 15, position: 'absolute', left: 10, top: 8 }}
          />
        }
        onClick={handleLoginMicrosoft}
      >
        <span style={{ marginTop: 2, marginLeft: 28 }}>{t('buttons.loginWithMicrosoft')}</span>
      </Button>
      <Spin spinning={loading} fullscreen />
    </>
  );
};
