import { IRegisterField } from '@/pages/register/register';
import { get, post } from './index';

export interface IUserRegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface IUserLoginRequest {
  email: string;
  password: string;
}

export interface IUserVerifyRequest {
  email: string;
  code: string;
}

export interface IUserLoginResponse {
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    is_active: boolean;
    is_verified: boolean;
    created_at: string;
    updated_at: string;
  };
  token: {
    access: string;
    refresh: string;
    token_type: string;
  };
}

export interface IVerifyResponse {
  success: boolean;
  message: string;
}

export interface IVerificationRequest {
  email: string;
}

// Register a new user
export const registerRequest = async (payload: IUserRegisterRequest): Promise<IUserLoginResponse> => {
  const url = '/users/register';
  const { data } = await post({ url, body: payload });
  return data;
};

// Login with email and password
export const loginRequest = async (email: string, password: string): Promise<IUserLoginResponse> => {
  const url = `/users/login`;
  const payload = {
    email,
    password
  };

  const { data } = await post({ url, body: payload });
  return data;
};

// Request email verification code
export const requestVerification = async (email: string): Promise<IVerifyResponse> => {
  const url = `/users/request-verification`;
  const payload = {
    email
  };

  const { data } = await post({ url, body: payload });
  return data;
};

// Verify user with code
export const verifyUser = async (email: string, code: string): Promise<IVerifyResponse> => {
  const url = `/users/verify`;
  const payload = {
    email,
    code
  };

  const { data } = await post({ url, body: payload });
  return data;
};

// Logout user
export const logoutUser = async (refreshToken: string): Promise<{ success: boolean }> => {
  const url = `/users/logout`;
  const headers = {
    'x-refresh-token': refreshToken
  };

  const { data } = await post({ url, headers });
  return { success: true };
};

// Get current user profile
export const getUserProfile = async () => {
  const url = `/users/me`;
  const { data } = await get({ url });
  return data;
};

// Refresh token
export const refreshToken = async (refreshToken: string): Promise<IUserLoginResponse> => {
  const url = `/users/refresh`;
  const payload = {
    refresh_token: refreshToken
  };

  const { data } = await post({ url, body: payload });
  return data;
};

export const loginViaGoogle = async (token: string, profile: any): Promise<IUserLoginResponse> => {
  const url = `/users/login/google`;
  const payload = { 
    token,
    profile
  };
  const { data } = await post({ url, body: payload });
  return data;
};

export const loginViaMicrosoft = async (token: string, profile: any): Promise<IUserLoginResponse> => {
  const url = `/users/login/microsoft`;
  const payload = { 
    token,
    profile
  };
  const { data } = await post({ url, body: payload });
  return data;
};

// Below are existing methods that might be used elsewhere in the app
// They're kept but may need to be updated to match the new API structure

export const loginReqRequest = async (cid: string) => {
  const url = `/v1/users/login-request`;
  const payload = {
    cid: cid
  };

  const { data } = await post({ url, body: payload });
  return data;
};

export const getUserInformationRequest = async () => {
  const url = `/users/me`;

  const { data } = await get({ url });
  if (data.trace_id === 'middlware-002') {
    return {
      authenticated: false,
      user: null
    };
  }
  return { authenticated: true, user: data };
};

// export const getUserPermission = async () => {
//   const url = '/v1/workspaces/user/permissions';
//   const { data } = await get({ url });
//   return data;
// };

// export const getUserWorkspaces = async (headers: Record<string, string> = {}) => {
//   const url = `/v1/workspaces/user`;
//   const { data } = await get({ url, headers });
//   return data;
// };

// export const getSetActiveWorkspace = async (workspaceSlug: string) => {
//   const url = `/v1/workspaces/${workspaceSlug}/activate`;
//   const { data } = await get({ url });
//   return data;
// };
