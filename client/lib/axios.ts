import axios from 'axios';

const TOKEN_STORAGE_KEY = 'auth_token';
const ROLE_STORAGE_KEY = 'auth_role';
const VERIFIED_STORAGE_KEY = 'auth_verified';
const TOKEN_COOKIE_KEY = 'auth_token';
const ONE_WEEK_IN_SECONDS = 60 * 60 * 24 * 7;

const isBrowser = (): boolean => typeof window !== 'undefined';

export const getToken = (): string | null => {
  if (!isBrowser()) {
    return null;
  }

  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
};

export const setToken = (token: string): void => {
  if (!isBrowser()) {
    return;
  }

  window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
  document.cookie = `${TOKEN_COOKIE_KEY}=${encodeURIComponent(token)}; path=/; max-age=${ONE_WEEK_IN_SECONDS}; samesite=lax`;
};

export const removeToken = (): void => {
  if (!isBrowser()) {
    return;
  }

  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  window.localStorage.removeItem(ROLE_STORAGE_KEY);
  window.localStorage.removeItem(VERIFIED_STORAGE_KEY);
  document.cookie = `${TOKEN_COOKIE_KEY}=; path=/; max-age=0; samesite=lax`;
};

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = getToken();

  if (token) {
    config.headers = config.headers ?? {};
    (config.headers as Record<string, string>).Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      if (isBrowser()) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);

export default api;
