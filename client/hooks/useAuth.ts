'use client';

import { useRouter } from 'next/navigation';
import { useCallback } from 'react';

import { getToken, removeToken, setToken } from '@/lib/axios';
import authService from '@/services/auth.service';
import { showInfo } from '@/lib/toast';

const ROLE_STORAGE_KEY = 'auth_role';
const VERIFIED_STORAGE_KEY = 'auth_verified';

export type AuthRole = 'admin' | 'student' | 'company';

type LoginArgs = {
  email: string;
  password: string;
};

type LoginResult = {
  token: string;
  role: AuthRole | null;
  isVerified: boolean | null;
};

const isBrowser = (): boolean => typeof window !== 'undefined';

const normalizeRole = (value: unknown): AuthRole | null => {
  if (value === 'admin' || value === 'student' || value === 'company') {
    return value;
  }

  return null;
};

const normalizeVerified = (value: unknown): boolean | null => {
  if (value === true || value === false) {
    return value;
  }

  if (value === 'true') {
    return true;
  }

  if (value === 'false') {
    return false;
  }

  return null;
};

const decodeTokenPayload = (token: string): Record<string, unknown> | null => {
  try {
    const payload = token.split('.')[1];
    if (!payload) {
      return null;
    }

    const normalizedPayload = payload.replace(/-/g, '+').replace(/_/g, '/');
    const paddedPayload = normalizedPayload.padEnd(
      Math.ceil(normalizedPayload.length / 4) * 4,
      '=',
    );
    const decodedPayload = atob(paddedPayload);

    return JSON.parse(decodedPayload) as Record<string, unknown>;
  } catch {
    return null;
  }
};

const storeRole = (role: AuthRole | null): void => {
  if (!isBrowser()) {
    return;
  }

  if (role) {
    window.localStorage.setItem(ROLE_STORAGE_KEY, role);
    return;
  }

  window.localStorage.removeItem(ROLE_STORAGE_KEY);
};

const storeVerification = (isVerified: boolean | null): void => {
  if (!isBrowser()) {
    return;
  }

  if (isVerified === null) {
    window.localStorage.removeItem(VERIFIED_STORAGE_KEY);
    return;
  }

  window.localStorage.setItem(VERIFIED_STORAGE_KEY, String(isVerified));
};

const getStoredRole = (): AuthRole | null => {
  if (!isBrowser()) {
    return null;
  }

  return normalizeRole(window.localStorage.getItem(ROLE_STORAGE_KEY));
};

const getStoredVerification = (): boolean | null => {
  if (!isBrowser()) {
    return null;
  }

  return normalizeVerified(window.localStorage.getItem(VERIFIED_STORAGE_KEY));
};

const resolveAuthState = (token: string | null) => {
  if (!token) {
    return { role: null, isVerified: null };
  }

  const payload = decodeTokenPayload(token);
  const roleFromToken = normalizeRole(payload?.role);
  const verifiedFromToken = normalizeVerified(payload?.is_verified);

  const role = roleFromToken ?? getStoredRole();
  const isVerified = verifiedFromToken ?? getStoredVerification();

  if (role) {
    storeRole(role);
  }

  if (isVerified !== null) {
    storeVerification(isVerified);
  }

  return { role, isVerified };
};

export const useAuth = () => {
  const router = useRouter();
  const token = getToken();
  const isAuthenticated = Boolean(token);
  const { role, isVerified } = resolveAuthState(token);

  const login = useCallback(async ({ email, password }: LoginArgs): Promise<LoginResult> => {
    const data = await authService.login({ email, password });

    const token = data.access_token;
    if (!token) {
      throw new Error('Login response does not include an access token');
    }

    setToken(token);

    const roleFromResponse = normalizeRole(data.user?.role);
    const roleFromToken = normalizeRole(decodeTokenPayload(token)?.role);
    const resolvedRole = roleFromResponse ?? roleFromToken;
    const verifiedFromResponse = normalizeVerified(data.user?.is_verified);
    const verifiedFromToken = normalizeVerified(decodeTokenPayload(token)?.is_verified);
    const resolvedVerified = verifiedFromResponse ?? verifiedFromToken;

    storeRole(resolvedRole);
    storeVerification(resolvedVerified);

    return {
      token,
      role: resolvedRole,
      isVerified: resolvedVerified,
    };
  }, []);

  const loginWithOTP = useCallback(
    async ({ email, otp }: { email: string; otp: string }): Promise<LoginResult> => {
      const data = await authService.loginWithOTP({ email, otp });

      const token = data.access_token;
      if (!token) {
        throw new Error('Login response does not include an access token');
      }

      setToken(token);

      const roleFromResponse = normalizeRole(data.user?.role);
      const roleFromToken = normalizeRole(decodeTokenPayload(token)?.role);
      const resolvedRole = roleFromResponse ?? roleFromToken;
      const verifiedFromResponse = normalizeVerified(data.user?.is_verified);
      const verifiedFromToken = normalizeVerified(decodeTokenPayload(token)?.is_verified);
      const resolvedVerified = verifiedFromResponse ?? verifiedFromToken;

      storeRole(resolvedRole);
      storeVerification(resolvedVerified);

      return {
        token,
        role: resolvedRole,
        isVerified: resolvedVerified,
      };
    },
    [],
  );

  const logout = useCallback((): void => {
    removeToken();
    storeRole(null);
    showInfo('Logged out successfully');
    router.replace('/login');
    router.refresh();
  }, [router]);

  return {
    isAuthenticated,
    role,
    isVerified,
    login,
    loginWithOTP,
    logout,
  };
};
