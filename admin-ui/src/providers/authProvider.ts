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
  // getUserPermission,
  // getUserWorkspaces,
  loginRequest,
  loginViaGoogle,
  loginViaMicrosoft,
  registerRequest,
  logoutUser,
  IUserLoginResponse,
  IUserRegisterRequest
} from '@/api-requests/auth';
import { SOURCE_AUTH } from '@/constant/authConfig';
import { ROUTES } from '@/constant/routes';
import { IRegisterField } from '@/pages/register/register';

// Type for the auth user
interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_verified: boolean;
  user_status?: number;
  workspace?: any;
}

// Define our own authProvider interface to avoid relying on imported types
interface AuthBindings {
  register: (params: IRegisterField) => Promise<any>;
  login: (params: { email?: string; password?: string; credentials?: string; source?: string }) => Promise<any>;
  logout: () => Promise<any>;
  check: () => Promise<any>;
  getPermissions: () => Promise<any>;
  getIdentity: () => Promise<any>;
  onError: (error: any) => Promise<any>;
}

export const authProvider: AuthBindings = {
  register: async (payload: IRegisterField) => {
    try {
      // Convert IRegisterField to IUserRegisterRequest
      const registerData: IUserRegisterRequest = {
        email: payload.email,
        password: payload.password,
        first_name: payload.first_name,
        last_name: payload.last_name
      };
      
      const data = await registerRequest(registerData);
      if (!data) {
        return createErrorResponse('Register Error', 'Invalid registration data');
      }
      
      // Store auth data in localStorage
      setLoginLocalStorage(data);
      
      // Check if user needs verification
      if (data.user.is_verified === false || (data.user as any).user_status === 401) {
        return { success: true, redirectTo: '/' + ROUTES.VERIFY_ACCOUNT + '?stage=otp' };
      }
      
      return { success: true, data };
    } catch (error) {
      console.error('Registration error:', error);
      return createErrorResponse('RegisterError', 'Registration failed. Please try again.');
    }
  },
  
  login: async ({ email, password, credentials, source }: { 
    email?: string; 
    password?: string; 
    credentials?: string; 
    source?: string 
  }) => {
    try {
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
      
      return createErrorResponse('LoginError', 'Invalid login credentials');
    } catch (error) {
      console.error('Login error:', error);
      return createErrorResponse('LoginError', 'Login failed. Please try again.');
    }
  },
  
  logout: async () => {
    try {
      const refreshTokenValue = localStorage.getItem(TOKEN_REFRESH_KEY);
      
      if (refreshTokenValue) {
        // Call the API to invalidate the refresh token
        await logoutUser(refreshTokenValue);
      }
      
      // Clear all auth-related data from localStorage
      clearLocalStorage();
      
      return { success: true, redirectTo: `/${ROUTES.WELCOME_LOGIN_REGISTER}` };
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear localStorage and redirect even if API call fails
      clearLocalStorage();
      return { success: true, redirectTo: `/${ROUTES.WELCOME_LOGIN_REGISTER}` };
    }
  },
  
  check: async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    const userInfoStr = localStorage.getItem(USER_KEY);

    if (token && userInfoStr) {
      // try {
        const userInfo = JSON.parse(userInfoStr) as User;
        
        // Check if user needs verification
        // if (userInfo.user_status === 401) {
        //   return { authenticated: false, redirectTo: '/' + ROUTES.VERIFY_ACCOUNT + '?stage=otp' };
        // }
        
        // Check if user needs to select workspace
        // if (!userInfo.workspace) {
        //   return { authenticated: false, redirectTo: '/' + ROUTES.WELCOME_WORKSPACE };
        // }
        
        return { authenticated: true };
      // } catch (error) {
      //   console.error('Error parsing user info:', error);
      //   return { authenticated: false, redirectTo: `/${ROUTES.WELCOME_LOGIN_REGISTER}` };
      // }
    }
    
    return { authenticated: false, redirectTo: `/${ROUTES.WELCOME_LOGIN_REGISTER}` };
  },
  
  getPermissions: async () => {
    try {
      // return await getUserPermission();
    } catch (error) {
      console.error('Error getting permissions:', error);
      return [];
    }
  },
  
  getIdentity: async () => {
    try {
      const { authenticated, user } = await getUserInformationRequest();
      
      if (authenticated && user) {
        setUserLocalStorage(user);
        return {
          id: user.id,
          name: `${user.first_name} ${user.last_name}`,
          workspace: user.workspace,
          avatar: user.avatar || 'https://i.pravatar.cc/300'
        };
      } else {
        clearLocalStorage();
        return null;
      }
    } catch (error) {
      console.error('Error getting user identity:', error);
      clearLocalStorage();
      return null;
    }
  },
  
  onError: async (error: any) => {
    console.error('Auth error:', error);
    return { error };
  }
};

const handleEmailLogin = async (email: string, password: string) => {
  try {
    localStorage.removeItem(USER_VERIFY_TEMP);
    const data = await loginRequest(email, password);

    if (!data) {
      return createErrorResponse('Login Error', 'Invalid email or password');
    }

    setLoginLocalStorage(data);

    // Check if user needs verification
    if ((data.user as any).user_status === 401) {
      return { success: true, redirectTo: '/' + ROUTES.VERIFY_ACCOUNT + '?stage=otp' };
    }

    // Get user workspaces
    // const workspaces = await getUserWorkspaces();
    // if (workspaces.length === 0) {
    //   return { success: true, redirectTo: '/' + ROUTES.WELCOME_WORKSPACE };
    // }
    
    // localStorage.setItem(USER_WORKSPACES_KEY, JSON.stringify(workspaces));

    return { success: true, redirectTo: '/' };
  } catch (error) {
    console.error('Email login error:', error);
    return createErrorResponse('Login Error', 'Login failed. Please try again.');
  }
};

const handleOAuthLogin = async (credentials: string, loginFunction: Function, errorMessage: string) => {
  try {
    localStorage.removeItem(USER_VERIFY_TEMP);
    const data = await loginFunction(credentials, null);

    if (!data) {
      return createErrorResponse('Login Error', errorMessage);
    }

    setLoginLocalStorage(data);

    // Check if user needs verification
    if ((data.user as any).user_status === 401) {
      return { success: true, redirectTo: '/' + ROUTES.VERIFY_ACCOUNT + '?stage=otp' };
    }

    // // Get user workspaces
    // const workspaces = await getUserWorkspaces();
    // if (workspaces.length === 0) {
    //   return { success: true, redirectTo: '/' + ROUTES.WELCOME_WORKSPACE };
    // }
    
    // localStorage.setItem(USER_WORKSPACES_KEY, JSON.stringify(workspaces));

    return { success: true, redirectTo: '/' };
  } catch (error) {
    console.error('OAuth login error:', error);
    return createErrorResponse('Login Error', errorMessage);
  }
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
  localStorage.removeItem(USER_WORKSPACES_KEY);
  localStorage.removeItem(USER_ICON_TEMP);
};

const setLoginLocalStorage = (data: IUserLoginResponse) => {
  localStorage.setItem(TOKEN_KEY, data.token.access);
  localStorage.setItem(TOKEN_REFRESH_KEY, data.token.refresh);
  
  // // Handle menu settings if available
  // if ((data as any).menu_settings) {
  //   localStorage.setItem(USER_MENU_SETTING_KEY, JSON.stringify((data as any).menu_settings));
  // }
  
  // // Handle permissions if available
  // if ((data as any).permissions) {
  //   localStorage.setItem(USER_PERMISSION, JSON.stringify((data as any).permissions));
  // }
  
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));
};

const setUserLocalStorage = (user: any) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  
  if (user.workspace) {
    const userIcon = {
      logo: user.workspace.logo,
      favicon: user.workspace.logo_favicon
    };
    localStorage.setItem(USER_ICON_TEMP, JSON.stringify(userIcon));
  }
};
