import api from '@/lib/axios';

export type UserProfile = {
  id: number;
  name: string;
  email: string;
  role: 'student' | 'company' | 'admin';
  is_verified: boolean;
  phone: string | null;
  location: string | null;
  education: string | null;
  college_name: string | null;
  branch: string | null;
  graduation_year: number | null;
  skills: string[];
  resume_url?: string | null;
  company_description?: string | null;
  website?: string | null;
  industry?: string | null;
  company_size?: string | null;
  established_year?: number | null;
  created_at: string;
};

export type UpdateProfilePayload = {
  name?: string;
  phone?: string | null;
  location?: string | null;
  education?: string | null;
  college_name?: string | null;
  branch?: string | null;
  graduation_year?: number | null;
  skills?: string[];
  company_description?: string | null;
  website?: string | null;
  industry?: string | null;
  company_size?: string | null;
  established_year?: number | null;
};

export type ResumeUploadResponse = {
  resume_url: string;
};

const userService = {
  getProfile: async (): Promise<UserProfile> => {
    const response = await api.get<UserProfile>('/users/profile');
    return response.data;
  },

  updateProfile: async (payload: UpdateProfilePayload): Promise<UserProfile> => {
    const response = await api.put<UserProfile>('/users/profile', payload);
    return response.data;
  },

  uploadResume: async (file: File): Promise<ResumeUploadResponse> => {
    const formData = new FormData();
    formData.append('resume', file);

    const response = await api.post<ResumeUploadResponse>('/users/upload-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  deleteAccount: async (password: string, confirmation: string): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>('/users/me', {
      data: { password, confirmation },
    });
    return response.data;
  },
};

export default userService;
