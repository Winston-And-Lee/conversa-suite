import { IRegisterField } from '@/pages/register/register';
import { get, post } from './index';

export const registerRequest = async (payload: IRegisterField) => {
  const url = '/v1/users/register';

  const { data } = await post({ url, body: payload });
  return data;
};

export const loginRequest = async (email: string, password: string) => {
  const url = `/v1/users/login`;
  const payload = {
    email: email,
    password: password
  };

  const { data } = await post({ url, body: payload });
  return data;
};

export const loginReqRequest = async (cid: string) => {
  const url = `/v1/users/login-request`;
  const payload = {
    cid: cid
  };

  const { data } = await post({ url, body: payload });
  return data;
};

interface LoginResponse {
  user: any;
  token: any;
  menu_settings: any;
  // Add response type definition
}

export const loginViaGoogle = async (credentials: string): Promise<LoginResponse> => {
  const url = `/v1/users/login-via-google`;
  const audience = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  const payload = { credentials: credentials, audience: audience };
  const { data } = await post({ url, body: payload });
  return data;
};

export const loginViaMicrosoft = async (credentials: string): Promise<LoginResponse> => {
  const url = `/v1/users/login-via-microsoft`;
  const payload = { credentials: credentials };
  const { data } = await post({ url, body: payload });
  return data;
};

export const getUserInformationRequest = async () => {
  const url = `/v1/users/profile`;

  const { data } = await get({ url });
  if (data.trace_id === 'middlware-002') {
    return {
      authenticated: false,
      user: null
    };
  }
  return { authenticated: true, user: data };
};

export const getUserPermission = async () => {
  const url = '/v1/workspaces/user/permissions';
  const { data } = await get({ url });
  return data;
};

export const getUserWorkspaces = async (headers: Record<string, string> = {}) => {
  const url = `/v1/workspaces/user`;
  const { data } = await get({ url, headers });
  return data;
};

export const getSetActiveWorkspace = async (workspaceSlug: string) => {
  const url = `/v1/workspaces/${workspaceSlug}/activate`;
  const { data } = await get({ url });
  return data;
};

export const getUserProfile = async () => {
  const url = `/v1/users/profile`;
  const { data } = await get({ url });
  return data;
};
