import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000';

// Create axios instance with default config
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for better error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response Error:', error.response.data);
      return Promise.reject(error);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Request Error:', error.request);
      return Promise.reject(new Error('No response from server. Please check if the backend is running.'));
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error:', error.message);
      return Promise.reject(error);
    }
  }
);

export interface SkillMatch {
  job_description_skills: string[];
  resume_skills: string[];
  matching_skills: string[];
  missing_skills: string[];
  extra_skills: string[];
  match_percentage: number;
}

export interface MatchResult {
  resume_id: string;
  rank: number;
  similarity_score: number;
  explanation: {
    cosine_similarity: number;
    euclidean_similarity: number;
    explanation: string;
  };
  skill_match: SkillMatch;
}

export interface MatchResponse {
  message: string;
  similarity_metric: string;
  top_k: number;
  similarity_threshold: number;
  ranking_summary: {
    total_matches: number;
    average_score: number;
    score_distribution: {
      high: number;
      medium: number;
      low: number;
    };
    top_ranked: Array<{
      rank: number;
      resume_id: string;
      score: number;
    }>;
  };
  job_description: {
    statistics: {
      word_count: number;
      unique_words: number;
      avg_word_length: number;
      keyword_density: number;
    };
    skills: string[];
  };
  matches: MatchResult[];
  resumes: {
    count: number;
    statistics: Array<{
      word_count: number;
      unique_words: number;
      avg_word_length: number;
      keyword_density: number;
    }>;
  };
}

export const api = {
  async checkHealth(): Promise<{ status: string; message: string }> {
    const response = await axiosInstance.get('/api/health');
    return response.data;
  },

  async matchResumes(
    jobDescription: File,
    resumes: File[],
    similarityMetric: 'cosine' | 'euclidean' | 'combined' = 'cosine',
    topK: number = 5,
    similarityThreshold: number = 0.3
  ): Promise<MatchResponse> {
    const formData = new FormData();
    formData.append('job_description', jobDescription);
    resumes.forEach((resume) => {
      formData.append('resumes', resume);
    });
    formData.append('similarity_metric', similarityMetric);
    formData.append('top_k', topK.toString());
    formData.append('similarity_threshold', similarityThreshold.toString());

    const response = await axiosInstance.post('/api/match', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },
}; 