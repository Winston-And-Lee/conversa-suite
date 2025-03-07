import { ROUTES } from '@/constant';
import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

export const TOKEN_KEY = 'conversa-suite-auth';
export const TOKEN_REFRESH_KEY = 'conversa-suite-refresh';
export const USER_KEY = 'conversa-suite-user';
export const USER_PERMISSION = 'khaojai-user-permission';
export const USER_WORKSPACES_KEY = 'conversa-suite-user-workspaces';
export const USER_MENU_SETTING_KEY = 'conversa-suite-menu-setting';
export const USER_VERIFY_TEMP = 'user-verify-temp';
export const USER_ICON_TEMP = 'user-icon-temp';

const defaultUrl = import.meta.env.VITE_APP_API_ENDPOINT;

interface RequestConfig {
  method: 'get' | 'post' | 'delete' | 'head' | 'options' | 'put' | 'patch';
  url: string;
  headers?: Record<string, string>;
  body?: any;
}

interface ResponseData {
  data: any;
  status: number;
  headers: Record<string, string>;
}

export const request = async ({ method, url, headers, body }: RequestConfig): Promise<ResponseData | any> => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    headers = {
      ...headers,
      Authorization: `Bearer ${token}`
    };
  }

  const config: AxiosRequestConfig = {
    method: method,
    url: url,
    headers: headers,
    data: body
  };

  return axios(config)
    .then((response: AxiosResponse) => {
      return {
        data: response['data'],
        status: response['status'],
        headers: response['headers']
      };
    })
    .catch((error: AxiosError) => {
      if (error.response) {
        const trace_id = (error.response?.data as any)?.trace_id;
        const currentPath = window.location.pathname;
        if (
          error.response.status === 401 &&
          trace_id == 'middlware-002' &&
          currentPath !== `/${ROUTES.LOGIN_WITH_OTP}`
        ) {
          localStorage.removeItem(TOKEN_KEY);
          window.location.reload();
        }
        throw {
          data: error.response.data,
          status: error.response.status,
          headers: error.response.headers
        };
      }
      throw error;
    });
};

export const post = async ({ url, headers, body }: Omit<RequestConfig, 'method'>): Promise<ResponseData> => {
  const config = {
    method: 'post' as const, // 'as const' to ensure type is exactly "post"
    url: defaultUrl + url,
    headers: headers,
    body: body
  };

  return request(config);
};

export const put = async ({ url, headers, body }: Omit<RequestConfig, 'method'>): Promise<ResponseData> => {
  const config = {
    method: 'put' as const, // 'as const' to ensure type is exactly "post"
    url: defaultUrl + url,
    headers: headers,
    body: body
  };

  return request(config);
};

export const patch = async ({ url, headers, body }: Omit<RequestConfig, 'method'>): Promise<ResponseData> => {
  const config = {
    method: 'patch' as const, // 'as const' to ensure type is exactly "post"
    url: defaultUrl + url,
    headers: headers,
    body: body
  };

  return request(config);
};

export const get = async ({ url, headers }: Omit<RequestConfig, 'method' | 'body'>): Promise<ResponseData> => {
  const config = {
    method: 'get' as const, // 'as const' to ensure type is exactly "get"
    url: defaultUrl + url,
    headers: headers
  };

  return request(config);
};

export const deleteRequest = async ({ url, headers, body }: Omit<RequestConfig, 'method'>): Promise<ResponseData> => {
  const config = {
    method: 'delete' as const, //
    url: defaultUrl + url,
    headers: headers,
    body: body
  };

  return request(config);
};
