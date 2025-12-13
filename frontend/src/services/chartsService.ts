import api from './api';

export interface ChartGenerationRequest {
  width?: number;
  height?: number;
  dpi?: number;
}

export const chartsService = {
  // Generate execution accuracy chart
  generateExecutionAccuracyChart: async (options?: ChartGenerationRequest): Promise<Blob> => {
    const response = await api.post('/api/charts/execution-accuracy', options || {}, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Generate component matching chart
  generateComponentMatchingChart: async (options?: ChartGenerationRequest): Promise<Blob> => {
    const response = await api.post('/api/charts/component-matching', options || {}, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Generate time distribution histogram
  generateTimeDistributionChart: async (options?: ChartGenerationRequest): Promise<Blob> => {
    const response = await api.post('/api/charts/time-distribution', options || {}, {
      responseType: 'blob',
    });
    return response.data;
  },
};