import { SOURCE_AUTH } from '@/constant/authConfig';
import { useLogin } from '@refinedev/core';
import { Spin } from 'antd';
import { useEffect, useRef, useState } from 'react';

export const GoogleButton = (): JSX.Element => {
  const divRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  const { mutate: login } = useLogin();

  function onClickGoogleButton() {
    setLoading(true);
  }

  useEffect(() => {
    if (typeof window === 'undefined' || !window.google || !divRef.current) {
      return;
    }

    const handleFocus = () => setLoading(false);

    window.addEventListener('focus', handleFocus);

    try {
      window.google.accounts.id.initialize({
        ux_mode: 'popup',
        client_id: GOOGLE_CLIENT_ID,
        use_fedcm_for_prompt: false,
        cancel_on_tap_outside: false,
        callback: async (res: CredentialResponse) => {
          try {
            login({ credentials: res.credential, source: SOURCE_AUTH.GOOGLE });
          } catch (error) {
            // Handle error
          } finally {
            setLoading(false);
          }
        }
      });

      window.google.accounts.id.renderButton(divRef.current, {
        theme: 'outline',
        size: 'medium',
        type: 'standard',
        width: '200px',
        locale: 'th',
        click_listener: onClickGoogleButton
      });

      window.google.accounts.id.prompt();
    } catch (error) {
      // Error initializing Google Sign-In
    }

    return () => {
      // remove event focus.
      window.removeEventListener('focus', handleFocus);

      // remove one tap prompt.
      window.google?.accounts.id.cancel();
    };
  }, [GOOGLE_CLIENT_ID, window.google, divRef.current]);

  return (
    <>
      <div ref={divRef} id='login-with-google-button' />
      <Spin spinning={loading} fullscreen />
    </>
  );
};
