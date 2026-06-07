export type ApplicationStatus =
  | "applied"
  | "screening"
  | "interview"
  | "offer"
  | "rejected"
  | "withdrawn";

export interface Application {
  id: string;
  company_name: string;
  role_title: string | null;
  status: ApplicationStatus;
  status_overridden: boolean;
  applied_at: string;
  last_activity_at: string;
  notes: string | null;
  confidence_score: number;
  sender_email: string;
  subject: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedApplications {
  items: Application[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  picture: string | null;
}

export interface SyncRequest {
  start_date?: string;
  end_date?: string;
}

export interface SyncResponse {
  new_emails_scanned: number;
  new_applications_found: number;
  skipped_duplicates: number;
}

export interface ApplicationUpdate {
  status?: ApplicationStatus;
  notes?: string;
  company_name?: string;
  role_title?: string;
}

export type FeedbackType = "confirm" | "reject";

export interface ApplicationFilters {
  status?: ApplicationStatus;
  start_date?: string;
  end_date?: string;
  search?: string;
  page?: number;
  page_size?: number;
}
