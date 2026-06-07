import apiClient from "./client";
import type { SyncRequest, SyncResponse } from "@/types";

export const syncApi = {
  trigger: async (body: SyncRequest = {}): Promise<SyncResponse> => {
    const { data } = await apiClient.post("/api/v1/sync", body);
    return data;
  },
};
