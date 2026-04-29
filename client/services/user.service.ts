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
};

export type ResumeUploadResponse = {
  filename: string;
  content_type: string;
  size_bytes: number;
  uploaded_at: string;
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
};

export default userService;
