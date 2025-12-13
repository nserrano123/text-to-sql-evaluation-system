import { useQuery } from '@tanstack/react-query';
import { metricsService } from '../services';

// Query keys for cache management
export const metricsKeys = {
  all: ['metrics'] as const,
  executionAccuracy: () => [...metricsKeys.all, 'executionAccuracy'] as const,
  timeToAnswer: () => [...metricsKeys.all, 'timeToAnswer'] as const,
  componentMatching: () => [...metricsKeys.all, 'componentMatching'] as const,
  summary: () => [...metricsKeys.all, 'summary'] as const,
};

// Get execution accuracy metrics
export const useExecutionAccuracyMetrics = () => {
  return useQuery({
    queryKey: metricsKeys.executionAccuracy(),
    queryFn: metricsService.getExecutionAccuracy,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2,
  });
};

// Get time to answer metrics
export const useTimeToAnswerMetrics = () => {
  return useQuery({
    queryKey: metricsKeys.timeToAnswer(),
    queryFn: metricsService.getTimeToAnswer,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2,
  });
};

// Get component matching metrics
export const useComponentMatchingMetrics = () => {
  return useQuery({
    queryKey: metricsKeys.componentMatching(),
    queryFn: metricsService.getComponentMatching,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2,
  });
};

// Get metrics summary
export const useMetricsSummary = () => {
  return useQuery({
    queryKey: metricsKeys.summary(),
    queryFn: metricsService.getSummary,
    staleTime: 1 * 60 * 1000, // 1 minute
    retry: 2,
  });
};