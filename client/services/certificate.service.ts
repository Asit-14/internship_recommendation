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

  download: async (certificateId: number): Promise<{ blob: Blob; filename: string }> => {
    const response = await api.get<Blob>(`/certificate/${certificateId}`, {
      responseType: 'blob',
    });

    const contentDisposition = response.headers['content-disposition'] as string | undefined;
    let filename = `certificate_${certificateId}.pdf`;

    if (contentDisposition) {
      const match = /filename="?([^";]+)"?/i.exec(contentDisposition);
      if (match?.[1]) {
        filename = match[1];
      }
    }

    return { blob: response.data, filename };
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
