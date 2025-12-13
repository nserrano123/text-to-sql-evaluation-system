import api from './api';
import { MetricsSummary } from '../types';

export interface ExecutionAccuracyMetrics {
  executionAccuracy: number;
  totalEvaluations: number;
  correctEvaluations: number;
}

export interface TimeToAnswerMetrics {
  averageTimeToAnswer: number;
  totalEvaluations: number;
  minTime: number;
  maxTime: number;
}

export interface ComponentMatchingMetrics {
  componentScores: {
    select: number;
    where: number;
    groupBy: number;
    orderBy: number;
    keywords: number;
  };
  totalEvaluations: number;
}

export const metricsService = {
  // Get execution accuracy metrics
  getExecutionAccuracy: async (): Promise<ExecutionAccuracyMetrics> => {
    const response = await api.get('/api/metrics/execution-accuracy');
    return response.data;
  },

  // Get time to answer metrics
  getTimeToAnswer: async (): Promise<TimeToAnswerMetrics> => {
    const response = await api.get('/api/metrics/time-to-answer');
    return response.data;
  },

  // Get component matching metrics
  getComponentMatching: async (): Promise<ComponentMatchingMetrics> => {
    const response = await api.get('/api/metrics/component-matching');
    return response.data;
  },

  // Get summary of all metrics
  getSummary: async (): Promise<MetricsSummary> => {
    const response = await api.get('/api/metrics/summary');
    return response.data;
  },
};