import api from '@/lib/axios';
import type { Internship } from '@/services/internship.service';

export type AdminUser = {
  id: number;
  name: string;
  email: string;
  role: 'student' | 'company' | 'admin';
  is_verified: boolean;
  created_at: string;
};

export type AdminSectorDistributionPoint = {
  sector: string;
  count: number;
};

export type AdminMonthlyStatPoint = {
  month: string;
  users: number;
  applications: number;
};

export type AdminAnalyticsOverview = {
  total_users: number;
  total_students: number;
  total_companies: number;
  total_internships: number;
  total_applications: number;
  success_rate: number;
  monthly_stats: AdminMonthlyStatPoint[];
  sector_distribution: AdminSectorDistributionPoint[];
};

export type AdminCompanyDetail = {
  company: AdminUser;
  internships: Internship[];
};

const adminService = {
  getUsers: async (): Promise<AdminUser[]> => {
    const response = await api.get<AdminUser[]>('/admin/users');
    return response.data;
  },

  approveUser: async (userId: number): Promise<AdminUser> => {
    const response = await api.patch<AdminUser>(`/admin/users/${userId}/approve`);
    return response.data;
  },

  deleteUser: async (userId: number): Promise<void> => {
    await api.delete(`/admin/users/${userId}`);
  },

  getCompanies: async (): Promise<AdminUser[]> => {
    const response = await api.get<AdminUser[]>('/admin/companies');
    return response.data;
  },

  getCompanyDetail: async (companyId: number): Promise<AdminCompanyDetail> => {
    const response = await api.get<AdminCompanyDetail>(`/admin/company/${companyId}`);
    return response.data;
  },

  getInternships: async (): Promise<Internship[]> => {
    const response = await api.get<Internship[]>('/admin/internships');
    return response.data;
  },

  deleteInternship: async (internshipId: number): Promise<void> => {
    await api.delete(`/admin/internships/${internshipId}`);
  },

  getAnalyticsOverview: async (): Promise<AdminAnalyticsOverview> => {
    const response = await api.get<AdminAnalyticsOverview>('/admin/analytics/overview');
    return response.data;
  },
};

export default adminService;
