import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { applicationsApi } from "@/api/applications";
import type { ApplicationFilters, ApplicationUpdate, FeedbackType } from "@/types";

export const APPLICATION_KEYS = {
  all: ["applications"] as const,
  list: (filters: ApplicationFilters) => ["applications", "list", filters] as const,
  detail: (id: string) => ["applications", "detail", id] as const,
};

export function useApplications(filters: ApplicationFilters = {}) {
  return useQuery({
    queryKey: APPLICATION_KEYS.list(filters),
    queryFn: () => applicationsApi.list(filters),
  });
}

export function useApplication(id: string) {
  return useQuery({
    queryKey: APPLICATION_KEYS.detail(id),
    queryFn: () => applicationsApi.getById(id),
    enabled: !!id,
  });
}

export function useUpdateApplication() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: ApplicationUpdate }) =>
      applicationsApi.update(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: APPLICATION_KEYS.all });
    },
  });
}

export function useDeleteApplication() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => applicationsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: APPLICATION_KEYS.all });
    },
  });
}

export function useSubmitFeedback() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, feedback }: { id: string; feedback: FeedbackType }) =>
      applicationsApi.submitFeedback(id, feedback),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: APPLICATION_KEYS.all });
    },
  });
}
