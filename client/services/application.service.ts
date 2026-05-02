import api from '@/lib/axios';

export type ApplicationStatus =
  | 'APPLIED'
  | 'UNDER_REVIEW'
  | 'SHORTLISTED'
  | 'SELECTED'
  | 'IN_PROGRESS'
  | 'REJECTED'
  | 'COMPLETED';

export type Application = {
  id: number;
  user_id: number;
  internship_id: number;
  internship_title?: string | null;
  company_name?: string | null;
  status: ApplicationStatus;
  resume_url?: string | null;
  applied_at: string;
  updated_at: string;
};

export type ApplicantProfile = {
  id: number;
  name: string;
  email: string;
  phone?: string | null;
  location?: string | null;
  education?: string | null;
  college_name?: string | null;
  branch?: string | null;
  graduation_year?: number | null;
  skills: string[];
  resume_url?: string | null;
};

export type ApplicantSummary = {
  application_id: number;
  internship_id: number;
  status: ApplicationStatus;
  applied_at: string;
  resume_url?: string | null;
  student: ApplicantProfile;
};

export type ApplicationDetail = {
  id: number;
  internship_id: number;
  status: ApplicationStatus;
  applied_at: string;
  updated_at: string;
  resume_url?: string | null;
  internship_title?: string | null;
  company_name?: string | null;
  student: ApplicantProfile;
};

const applicationService = {
  applyToInternship: async (internship_id: number): Promise<Application> => {
    const response = await api.post<Application>('/applications/', {
      internship_id,
    });
    return response.data;
  },

  getMyApplications: async (): Promise<Application[]> => {
    const response = await api.get<Application[]>('/applications/my');
    return response.data;
  },

  getById: async (id: number): Promise<ApplicationDetail> => {
    const response = await api.get<ApplicationDetail>(`/applications/${id}`);
    return response.data;
  },

  getApplicantsByInternship: async (internshipId: number): Promise<ApplicantSummary[]> => {
    const response = await api.get<ApplicantSummary[]>(
      `/company/internships/${internshipId}/applicants`,
    );
    return response.data;
  },

  updateStatus: async (applicationId: number, status: ApplicationStatus): Promise<Application> => {
    const response = await api.patch<Application>(`/applications/${applicationId}/status`, {
      status,
    });
    return response.data;
  },
};

export default applicationService;
