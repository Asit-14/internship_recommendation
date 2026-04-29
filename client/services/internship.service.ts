import api from '@/lib/axios';

export type Internship = {
  id: number;
  title: string;
  description: string;
  company_name: string;
  location: string;
  skills_required: string[];
  sector: string;
  created_by?: number | null;
  duration: number;
  stipend: number;
  is_active: boolean;
  created_at: string;
  skill_match_score?: number | null;
};

export type InternshipFilters = {
  location?: string;
  skills?: string[];
  sector?: string;
  stipend_min?: number;
  stipend_max?: number;
  duration_min?: number;
  duration_max?: number;
  user_skills?: string[];
};

export type CreateInternshipPayload = {
  title: string;
  description: string;
  skills_required: string[];
  location: string;
  duration: number;
  stipend: number;
  is_active?: boolean;
};

const internshipService = {
  getAll: async (filters?: InternshipFilters): Promise<Internship[]> => {
    const response = await api.get<Internship[]>('/internships/', {
      params: filters,
    });
    return response.data;
  },

  getById: async (id: number): Promise<Internship> => {
    const response = await api.get<Internship>(`/internships/${id}`);
    return response.data;
  },

  create: async (payload: CreateInternshipPayload): Promise<Internship> => {
    const response = await api.post<Internship>('/internships/', payload);
    return response.data;
  },

  getCompanyInternships: async (): Promise<Internship[]> => {
    const response = await api.get<Internship[]>('/company/internships');
    return response.data;
  },

  update: async (id: number, payload: Partial<CreateInternshipPayload>): Promise<Internship> => {
    const response = await api.put<Internship>(`/internships/${id}`, payload);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/internships/${id}`);
  },
};

export default internshipService;
