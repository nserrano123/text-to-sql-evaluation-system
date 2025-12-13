import api from './api';
import { Evaluation, ExecutionAccuracy, TimeToAnswer, ComponentMatching } from '../types';

export interface CreateEvaluationRequest {
  gold_query_id: string;
  generated_sql: string;
  execution_accuracy: Omit<ExecutionAccuracy, 'id' | 'evaluationId' | 'createdAt'>;
  time_to_answer: Omit<TimeToAnswer, 'id' | 'evaluationId' | 'createdAt'>;
  component_matching: Omit<ComponentMatching, 'id' | 'evaluationId' | 'createdAt'>;
}

export interface UpdateEvaluationRequest {
  generated_sql?: string;
  execution_accuracy?: Partial<Omit<ExecutionAccuracy, 'id' | 'evaluationId' | 'createdAt'>>;
  time_to_answer?: Partial<Omit<TimeToAnswer, 'id' | 'evaluationId' | 'createdAt'>>;
  component_matching?: Partial<Omit<ComponentMatching, 'id' | 'evaluationId' | 'createdAt'>>;
}

export const evaluationsService = {
  // Get all evaluations
  getAll: async (): Promise<Evaluation[]> => {
    const response = await api.get('/api/evaluations');
    return response.data;
  },

  // Get evaluation by ID
  getById: async (id: string): Promise<Evaluation> => {
    const response = await api.get(`/api/evaluations/${id}`);
    return response.data;
  },

  // Create new evaluation
  create: async (evaluation: CreateEvaluationRequest): Promise<Evaluation> => {
    const response = await api.post('/api/evaluations', evaluation);
    return response.data;
  },

  // Update evaluation
  update: async (id: string, evaluation: UpdateEvaluationRequest): Promise<Evaluation> => {
    const response = await api.put(`/api/evaluations/${id}`, evaluation);
    return response.data;
  },

  // Delete evaluation
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/evaluations/${id}`);
  },
};