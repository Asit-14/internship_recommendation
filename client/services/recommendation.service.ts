import api from '@/lib/axios';

export type RecommendationPreferences = {
  preferred_sectors?: string[];
  preferred_companies?: string[];
  minimum_stipend?: number;
  maximum_duration_weeks?: number;
  remote_only?: boolean;
};

export type RecommendationPayload = {
  skills?: string[];
  resume_text?: string;
  education?: string;
  location?: string;
  preferences?: RecommendationPreferences;
  top_k?: number;
};

export type ScoreBreakdown = {
  skill_match: number;
  location_match: number;
  education_match: number;
  preference_match: number;
  total_score: number;
};

export type Recommendation = {
  internship_id: number;
  title: string;
  company_name: string;
  location: string;
  sector: string;
  match_score: number;
  score_breakdown?: ScoreBreakdown;
  explanation: string;
  matched_skills: string[];
  skill_gap?: string[];
  missing_skills?: string[];
};

export type RecommendationResponse = {
  normalized_user_skills: string[];
  evaluated_internships_count: number;
  recommendations: Recommendation[];
};

const recommendationService = {
  getRecommendations: async (data: RecommendationPayload): Promise<RecommendationResponse> => {
    const response = await api.post<RecommendationResponse>('/recommendations/', data);
    return response.data;
  },
  analyzeResume: async (file: File): Promise<Recommendation[]> => {
    const formData = new FormData();
    formData.append('resume', file);

    const response = await api.post<Recommendation[]>('/resume/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },
};

export default recommendationService;
