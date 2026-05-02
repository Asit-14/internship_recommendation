import api from '@/lib/axios';

export type Certificate = {
  id: number;
  user_id: number;
  internship_id: number;
  certificate_id: string;
  certificate_url: string;
  issued_at: string;
};

const certificateService = {
  generate: async (applicationId: number): Promise<Certificate> => {
    const response = await api.post<Certificate>('/certificate/generate', {
      application_id: applicationId,
    });
    return response.data;
  },

  getMyCertificates: async (): Promise<Certificate[]> => {
    const response = await api.get<Certificate[]>('/certificate/my');
    return response.data;
  },



  verify: async (certificateId: string): Promise<Certificate> => {
    const response = await api.get<Certificate>(`/certificate/verify/${certificateId}`);
    return response.data;
  },

  generateMissing: async (applicationId: number): Promise<Certificate> => {
    const response = await api.post<Certificate>(`/certificate/${applicationId}/generate-missing`);
    return response.data;
  },
};

export default certificateService;
