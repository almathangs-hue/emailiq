import apiClient from "./client";
import type {
  Application,
  ApplicationFilters,
  ApplicationUpdate,
  FeedbackType,
  PaginatedApplications,
} from "@/types";

export const applicationsApi = {
  list: async (filters: ApplicationFilters = {}): Promise<PaginatedApplications> => {
    const { data } = await apiClient.get("/api/v1/applications", { params: filters });
    return data;
  },

  getById: async (id: string): Promise<Application> => {
    const { data } = await apiClient.get(`/api/v1/applications/${id}`);
    return data;
  },

  update: async (id: string, body: ApplicationUpdate): Promise<Application> => {
    const { data } = await apiClient.patch(`/api/v1/applications/${id}`, body);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/applications/${id}`);
  },

  submitFeedback: async (id: string, feedback: FeedbackType): Promise<void> => {
    await apiClient.post(`/api/v1/applications/${id}/feedback`, { feedback });
  },
};
