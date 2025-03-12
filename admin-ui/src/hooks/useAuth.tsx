import { useState, useEffect } from 'react';
import { TOKEN_KEY } from '@/api-requests';

/**
 * Hook for handling authentication-related functionality
 */
export const useAuth = () => {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  
  useEffect(() => {
    // On component mount, try to get the token from localStorage
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      setAccessToken(token);
    }
  }, []);
  
  /**
   * Get the current access token
   * @returns The access token
   */
  const getAccessToken = async (): Promise<string> => {
    // If we already have a token, return it
    if (accessToken) {
      return accessToken;
    }
    
    // Otherwise, try to get it from localStorage
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      setAccessToken(token);
      return token;
    }
    
    // If no token is found, throw an error
    throw new Error('No access token found');
  };
  
  /**
   * Set the access token
   * @param token The access token to set
   */
  const setToken = (token: string) => {
    localStorage.setItem(TOKEN_KEY, token);
    setAccessToken(token);
  };
  
  /**
   * Clear the access token
   */
  const clearToken = () => {
    localStorage.removeItem(TOKEN_KEY);
    setAccessToken(null);
  };
  
  return {
    accessToken,
    getAccessToken,
    setToken,
    clearToken,
  };
}; 