import { ROUTES } from '@/constant';
import { AuthenticateTemplate } from '@/layouts/authenticate';
import { useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
// import { CreateWorkspaceBox } from './components/createWorkspace';
import { InformationBox } from './components/informationBox';
import { OtpBox } from './components/otpBox';

type ValidStage = 'information' | 'otp' | 'create-workspace';

const getValidatedStageParam = (stage: string | null): ValidStage => {
  const validStages: ValidStage[] = ['information', 'otp', 'create-workspace'];
  if (!stage) return validStages[0];

  const isValid = validStages.includes(stage as ValidStage);
  return isValid ? (stage as ValidStage) : validStages[0];
};

export interface IRegisterField {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  password_confirm: string;
  domain: string;
}

export const SignupPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const stageParam = getValidatedStageParam(searchParams.get('stage'));
  const referenceToken = searchParams.get('reference_token') ?? '';

  /**
   * Access token is used for some requests that require authentication
   * - get user workspace
   * - create workspace
   */
  // const [referenceToken, setReferenceToken] = useState<string | undefined>()

  const navigate = useNavigate();

  const [userInfo, setUserInfo] = useState<IRegisterField | undefined>();
  const renderContent = useMemo(() => {
    if (stageParam === 'otp' && userInfo) {
      return (
        <OtpBox
          userInfo={userInfo}
          referenceToken={referenceToken}
          onBack={() => {
            setSearchParams({ stage: 'information' });
          }}
          onFinish={() => {
            navigate(`/${ROUTES.WELCOME_LOGIN_REGISTER}?verified`);
          }}
        />
      );
    } else if (stageParam === 'information' || !userInfo || !referenceToken) {
      return (
        <InformationBox
          onFinish={(user_info: IRegisterField, reference_token: string) => {
            setSearchParams({ stage: 'otp', reference_token: reference_token });
            setUserInfo(user_info);
          }}
        />
      );
    } else {
      return null;
    }
  }, [stageParam, userInfo, referenceToken, setSearchParams]);

  return <AuthenticateTemplate decoratedImage='/assets/lottiefiles/login.json'>{renderContent}</AuthenticateTemplate>;
};
