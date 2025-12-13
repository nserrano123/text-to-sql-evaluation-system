import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { goldQueriesService } from '../services';

// Query keys for cache management
export const goldQueriesKeys = {
  all: ['goldQueries'] as const,
  lists: () => [...goldQueriesKeys.all, 'list'] as const,
  list: (filters: string) => [...goldQueriesKeys.lists(), { filters }] as const,
  details: () => [...goldQueriesKeys.all, 'detail'] as const,
  detail: (id: string) => [...goldQueriesKeys.details(), id] as const,
  pending: () => [...goldQueriesKeys.all, 'pending'] as const,
};

// Get all gold queries
export const useGoldQueries = () => {
  return useQuery({
    queryKey: goldQueriesKeys.lists(),
    queryFn: goldQueriesService.getAll,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Get gold query by ID
export const useGoldQuery = (id: string) => {
  return useQuery({
    queryKey: goldQueriesKeys.detail(id),
    queryFn: () => goldQueriesService.getById(id),
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Get pending gold queries
export const usePendingGoldQueries = () => {
  return useQuery({
    queryKey: goldQueriesKeys.pending(),
    queryFn: goldQueriesService.getPending,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};

// Create gold query mutation
export const useCreateGoldQuery = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: goldQueriesService.create,
    onSuccess: () => {
      // Invalidate and refetch gold queries
      queryClient.invalidateQueries({ queryKey: goldQueriesKeys.all });
    },
  });
};