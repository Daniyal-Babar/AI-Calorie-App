import React, { createContext, useState, useEffect, useCallback } from 'react';
import { getAuthToken, setAuthToken } from '../api/client';
import { getMeApi, loginApi, registerApi, logoutApi, updateProfileApi } from '../api/auth';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const token = getAuthToken();
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const data = await getMeApi();
      setUser(data.user);
    } catch (err) {
      console.warn('Session expired or invalid:', err.message);
      setAuthToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = async (credentials) => {
    const data = await loginApi(credentials);
    setUser(data.user);
    return data;
  };

  const register = async (userData) => {
    const data = await registerApi(userData);
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    await logoutApi();
    setUser(null);
  };

  const updateProfile = async (profileData) => {
    const data = await updateProfileApi(profileData);
    setUser(data.user);
    return data;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        loading,
        login,
        register,
        logout,
        refreshUser,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
