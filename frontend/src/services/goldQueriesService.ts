import api from './api';
import { GoldQuery } from '../types';

export const goldQueriesService = {
  // Get all gold queries
  getAll: async (): Promise<GoldQuery[]> => {
    const response = await api.get('/api/gold-queries');
    return response.data;
  },

  // Get gold query by ID
  getById: async (id: string): Promise<GoldQuery> => {
    const response = await api.get(`/api/gold-queries/${id}`);
    return response.data;
  },

  // Create new gold query
  create: async (goldQuery: Omit<GoldQuery, 'id' | 'createdAt'>): Promise<GoldQuery> => {
    const response = await api.post('/api/gold-queries', goldQuery);
    return response.data;
  },

  // Get pending queries (not yet evaluated)
  getPending: async (): Promise<GoldQuery[]> => {
    const response = await api.get('/api/gold-queries/pending');
    return response.data;
  },
};