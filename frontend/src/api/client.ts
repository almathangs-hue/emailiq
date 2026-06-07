import axios from "axios";
import { useAuthStore } from "@/store/authStore";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
});

// Attach JWT token to every request
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to login on 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

export default apiClient;
