import {
  TOKEN_KEY,
  TOKEN_REFRESH_KEY,
  USER_ICON_TEMP,
  USER_KEY,
  USER_MENU_SETTING_KEY,
  USER_PERMISSION,
  USER_VERIFY_TEMP,
  USER_WORKSPACES_KEY
} from '@/api-requests';
import {
  getUserInformationRequest,
  getUserPermission,
  getUserWorkspaces,
  loginRequest,
  loginViaGoogle,
  loginViaMicrosoft,
  registerRequest
} from '@/api-requests/auth';
import { SOURCE_AUTH } from '@/constant/authConfig';
import { ROUTES } from '@/constant/routes';
import { IRegisterField } from '@/pages/register/register';
import { AuthBindings } from '@refinedev/core';

export const authProvider: AuthBindings = {
  register: async (payload: IRegisterField) => {
    try {
      const data = await registerRequest(payload);
      if (!data) {
        return createErrorResponse('Register Error', 'Invalid username or password');
      }
      return { success: true, data };
    } catch (error) {
      return createErrorResponse('RegisterError', 'Invalid username or password');
    }
  },
  login: async ({ email, password, credentials, source }) => {
    if (credentials) {
      if (source === SOURCE_AUTH.GOOGLE) {
        return handleOAuthLogin(credentials, loginViaGoogle, 'Invalid Google credentials');
      } else if (source === SOURCE_AUTH.MICROSOFT) {
        return handleOAuthLogin(credentials, loginViaMicrosoft, 'Invalid Microsoft credentials');
      }
    }
    if (email && password) {
      return handleEmailLogin(email, password);
    }
    return createErrorResponse('LoginError', 'Invalid code or reference_token');
  },
  logout: async () => {
    clearLocalStorage();
    return { success: true, redirectTo: `/${ROUTES.WELCOME_LOGIN_REGISTER}` };
  },
  check: async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    const userInfoStr = localStorage.getItem(USER_KEY);

    if (token && userInfoStr) {
      const userInfo = JSON.parse(userInfoStr);
      if (userInfo && userInfo['user_status'] == 401) {
        return { authenticated: false, redirectTo: '/' + ROUTES.VERIFY_ACCOUNT + '?stage=otp' };
      }
      if (userInfo && !userInfo['workspace']) {
        return { authenticated: false, redirectTo: '/' + ROUTES.WELCOME_WORKSPACE };
      }
      return { authenticated: true };
    }
    return { authenticated: false, redirectTo: `/${ROUTES.WELCOME_LOGIN_REGISTER}` };
  },
  getPermissions: async () => {
    return await getUserPermission();
  },
  getIdentity: async () => {
    const { authenticated, user } = await getUserInformationRequest();
    if (authenticated) {
      setUserLocalStorage(user);
      return {
        id: user.id,
        name: `${user.first_name} ${user.last_name}`,
        workspace: user.workspace,
        avatar: 'https://i.pravatar.cc/300'
      };
    } else {
      clearLocalStorage();
      return null;
    }
  },
  onError: async (error) => {
    console.error(error);
    return { error };
  }
};

const handleEmailLogin = async (email: string, password: string) => {
  localStorage.removeItem(USER_VERIFY_TEMP);
  const data = await loginRequest(email, password);

  if (!data) {
    return createErrorResponse('Login Error', 'Invalid email or password');
  }

  setLoginLocalStorage(data);

  if (data['user']['user_status'] == 401) {
    return { success: true, redirectTo: '/' + ROUTES.VERIFY_ACCOUNT + '?stage=otp' };
  }

  const workspaces = await getUserWorkspaces();
  if (workspaces.length == 0) {
    return { success: true, redirectTo: '/' + ROUTES.WELCOME_WORKSPACE };
  }
  localStorage.setItem(USER_WORKSPACES_KEY, JSON.stringify(workspaces));

  return { success: true, redirectTo: '/' };
};

const handleOAuthLogin = async (credentials: string, loginFunction: Function, errorMessage: string) => {
  localStorage.removeItem(USER_VERIFY_TEMP);
  const data = await loginFunction(credentials);

  if (!data) {
    return createErrorResponse('Login Error', errorMessage);
  }

  setLoginLocalStorage(data);

  if (data.user && data.user?.user_status === 401) {
    return { success: true, redirectTo: '/' + ROUTES.VERIFY_ACCOUNT + '?stage=otp' };
  }

  const workspaces = await getUserWorkspaces();
  if (workspaces.length == 0) {
    return { success: true, redirectTo: '/' + ROUTES.WELCOME_WORKSPACE };
  }
  localStorage.setItem(USER_WORKSPACES_KEY, JSON.stringify(workspaces));

  return { success: true, redirectTo: '/' };
};

const createErrorResponse = (name: string, message: string) => ({
  success: false,
  error: { name, message }
});

const clearLocalStorage = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(USER_PERMISSION);
  localStorage.removeItem(USER_MENU_SETTING_KEY);
};

const setLoginLocalStorage = (data: any) => {
  localStorage.setItem(TOKEN_KEY, data['token']['access']);
  localStorage.setItem(TOKEN_REFRESH_KEY, data['token']['refresh']);
  if (data['menu_settings']) {
    localStorage.setItem(USER_MENU_SETTING_KEY, JSON.stringify(data['menu_settings']));
  }
  if (data['permissions']) {
    localStorage.setItem(USER_PERMISSION, JSON.stringify(data['permissions']));
  }
  localStorage.setItem(USER_KEY, JSON.stringify(data['user']));
};

const setUserLocalStorage = (user: any) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  const userIcon = {
    logo: user.workspace.logo,
    favicon: user.workspace.logo_favicon
  };
  localStorage.setItem(USER_ICON_TEMP, JSON.stringify(userIcon));
};
