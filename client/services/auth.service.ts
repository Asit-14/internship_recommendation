import api from '@/lib/axios';

export type LoginPayload = {
  email: string;
  password: string;
};

export type UserResponse = {
  id: number;
  name: string;
  email: string;
  role: 'student' | 'company' | 'admin';
  is_verified: boolean;
  created_at: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserResponse;
};

export type SignupPayload = {
  name: string;
  email: string;
  password: string;
};

export type CompanySignupPayload = {
  company_name: string;
  email: string;
  password: string;
};

export type SendOTPPayload = {
  email: string;
};

export type VerifyOTPPayload = {
  email: string;
  otp: string;
};

export type ResetPasswordPayload = {
  email: string;
  otp: string;
  new_password: string;
};

export type LoginWithOTPPayload = {
  email: string;
  otp: string;
};

const authService = {
  login: async (payload: LoginPayload): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', payload);
    return response.data;
  },

  signup: async (payload: SignupPayload): Promise<UserResponse> => {
    const response = await api.post<UserResponse>('/auth/signup', payload);
    return response.data;
  },

  registerCompany: async (payload: CompanySignupPayload): Promise<UserResponse> => {
    const response = await api.post<UserResponse>('/auth/register-company', payload);
    return response.data;
  },

  sendOTP: async (payload: SendOTPPayload): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/auth/send-otp', payload);
    return response.data;
  },

  verifyOTP: async (payload: VerifyOTPPayload): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/auth/verify-otp', payload);
    return response.data;
  },

  resetPassword: async (payload: ResetPasswordPayload): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/auth/reset-password', payload);
    return response.data;
  },

  loginWithOTP: async (payload: LoginWithOTPPayload): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login-otp', payload);
    return response.data;
  },
};

export default authService;
