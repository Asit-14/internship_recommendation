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
};

export default authService;
