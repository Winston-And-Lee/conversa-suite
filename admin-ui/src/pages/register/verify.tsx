import { USER_KEY, USER_VERIFY_TEMP } from '@/api-requests';
import { getUserProfile } from '@/api-requests/auth';
import { ROUTES } from '@/constant';
import { AuthenticateTemplate } from '@/layouts/authenticate';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { OtpBox } from './components/otpBox';

export const VerifyPage = () => {
  const navigate = useNavigate();

  const userInfoStr = localStorage.getItem(USER_KEY) ?? '';
  const [referenceToken, setReferenceToken] = useState('');

  const userLocalStorage = localStorage.getItem(USER_VERIFY_TEMP);
  const userVeriftTemp = userLocalStorage ? JSON.parse(userLocalStorage) : null;

  const userInfo = userInfoStr ? JSON.parse(userInfoStr) : null;

  return (
    <AuthenticateTemplate decoratedImage='/assets/lottiefiles/login.json'>
      {userInfo || userVeriftTemp ? (
        <OtpBox
          userInfo={userInfo}
          referenceToken={referenceToken}
          onBack={() => {
            window.history.back();
          }}
          onFinish={async () => {
            if (!userInfo && userVeriftTemp) {
              navigate(`/${ROUTES.WELCOME_LOGIN_REGISTER}?verified`);
              localStorage.removeItem(USER_VERIFY_TEMP);
              return;
            }

            if (userInfo) {
              const userProfile = await getUserProfile();
              localStorage.setItem(USER_KEY, JSON.stringify(userProfile));
              navigate(`/${ROUTES.WELCOME_LOGIN_REGISTER}?verified`);

              if (userProfile.user_status === 401) return;

              if (!userProfile.workspace) {
                navigate(`/${ROUTES.WELCOME_WORKSPACE}`);
              } else {
                navigate(`/`);
              }
            }
          }}
        />
      ) : null}
    </AuthenticateTemplate>
  );
};
