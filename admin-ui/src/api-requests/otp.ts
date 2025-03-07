import { IUserInfo } from '@/interfaces/user';
import { post } from '.';

const defaultUrl = import.meta.env.VITE_APP_API_ENDPOINT;

interface ResendOtpRequest {
  email: string;
  domain: string;
}

export const verifyOtpRequest = async (reference_token: string, otp: string): Promise<IUserInfo> => {
  const url = `/v1/users/verify`;
  const payload = {
    reference_token: reference_token,
    code: otp
  };

  const { data } = await post({ url, body: payload });
  return data;
};

export const resendOtpRequest = async (request: ResendOtpRequest) => {
  const url = `/v1/users/verification-request`;
  const payload = request;

  const { data } = await post({ url, body: payload });
  return data;
};
