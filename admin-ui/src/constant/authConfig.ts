
export const MSAL_CONFIG = {
  auth: {
    clientId: import.meta.env.VITE_MICROSOFT_CLIENT_ID,
    authority: import.meta.env.VITE_MICROSOFT_AUTHORITY,
    redirectUri: import.meta.env.VITE_MICROSOFT_REDIRECT_URI,
  }
};

export const LOGIN_REQUEST = {
  scopes: ["openid", "profile", "user.read"],
};

export const SOURCE_AUTH = Object.freeze({
  EMAIL: 'EMAIL',
  GOOGLE: 'GOOGLE',
  MICROSOFT: 'MICROSOFT',
});
