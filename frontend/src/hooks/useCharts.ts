import { useMutation } from '@tanstack/react-query';
import { chartsService, ChartGenerationRequest } from '../services/chartsService';

// Generate execution accuracy chart
export const useGenerateExecutionAccuracyChart = () => {
  return useMutation({
    mutationFn: (options?: ChartGenerationRequest) => 
      chartsService.generateExecutionAccuracyChart(options),
  });
};

// Generate component matching chart
export const useGenerateComponentMatchingChart = () => {
  return useMutation({
    mutationFn: (options?: ChartGenerationRequest) => 
      chartsService.generateComponentMatchingChart(options),
  });
};

// Generate time distribution chart
export const useGenerateTimeDistributionChart = () => {
  return useMutation({
    mutationFn: (options?: ChartGenerationRequest) => 
      chartsService.generateTimeDistributionChart(options),
  });
};