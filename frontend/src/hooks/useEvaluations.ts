import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { evaluationsService, CreateEvaluationRequest, UpdateEvaluationRequest } from '../services/evaluationsService';
import { goldQueriesKeys } from './useGoldQueries';

// Query keys for cache management
export const evaluationsKeys = {
  all: ['evaluations'] as const,
  lists: () => [...evaluationsKeys.all, 'list'] as const,
  list: (filters: string) => [...evaluationsKeys.lists(), { filters }] as const,
  details: () => [...evaluationsKeys.all, 'detail'] as const,
  detail: (id: string) => [...evaluationsKeys.details(), id] as const,
};

// Get all evaluations
export const useEvaluations = () => {
  return useQuery({
    queryKey: evaluationsKeys.lists(),
    queryFn: evaluationsService.getAll,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

// Get evaluation by ID
export const useEvaluation = (id: string) => {
  return useQuery({
    queryKey: evaluationsKeys.detail(id),
    queryFn: () => evaluationsService.getById(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Create evaluation mutation
export const useCreateEvaluation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (evaluation: CreateEvaluationRequest) => evaluationsService.create(evaluation),
    onSuccess: () => {
      // Invalidate evaluations and pending queries
      queryClient.invalidateQueries({ queryKey: evaluationsKeys.all });
      queryClient.invalidateQueries({ queryKey: goldQueriesKeys.pending() });
      // Also invalidate metrics since they depend on evaluations
      queryClient.invalidateQueries({ queryKey: ['metrics'] });
    },
  });
};

// Update evaluation mutation
export const useUpdateEvaluation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, evaluation }: { id: string; evaluation: UpdateEvaluationRequest }) =>
      evaluationsService.update(id, evaluation),
    onSuccess: (_, { id }) => {
      // Invalidate specific evaluation and lists
      queryClient.invalidateQueries({ queryKey: evaluationsKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: evaluationsKeys.lists() });
      // Also invalidate metrics
      queryClient.invalidateQueries({ queryKey: ['metrics'] });
    },
  });
};

// Delete evaluation mutation
export const useDeleteEvaluation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => evaluationsService.delete(id),
    onSuccess: () => {
      // Invalidate evaluations and pending queries
      queryClient.invalidateQueries({ queryKey: evaluationsKeys.all });
      queryClient.invalidateQueries({ queryKey: goldQueriesKeys.pending() });
      // Also invalidate metrics
      queryClient.invalidateQueries({ queryKey: ['metrics'] });
    },
  });
};