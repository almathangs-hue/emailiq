import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { useApplications } from "@/hooks/useApplications";
import type { ApplicationFilters } from "@/types";
import DashboardFilters from "@/components/Dashboard/DashboardFilters";
import ApplicationTable from "@/components/Dashboard/ApplicationTable";
import SyncPanel from "@/components/Dashboard/SyncPanel";
import Button from "@/components/common/Button";

export default function Dashboard() {
  const [searchParams] = useSearchParams();
  const { setToken, logout, user } = useAuthStore();

  // Pick up token from OAuth redirect (?token=...)
  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      setToken(token);
      window.history.replaceState({}, "", "/dashboard");
    }
  }, [searchParams, setToken]);

  const [filters, setFilters] = useState<ApplicationFilters>({
    page: 1,
    page_size: 20,
  });

  const { data, isLoading, isError } = useApplications(filters);

  const totalPages = data?.total_pages ?? 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-brand-500 flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <span className="font-semibold text-gray-900">EmailIQ</span>
          </div>
          <div className="flex items-center gap-3">
            {user && (
              <span className="text-sm text-gray-500 hidden sm:block">{user.email}</span>
            )}
            <Button variant="ghost" onClick={logout} className="text-sm">
              Sign out
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Page header */}
        <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Job Applications</h1>
            {data && (
              <p className="text-sm text-gray-500 mt-0.5">
                {data.total} application{data.total !== 1 ? "s" : ""} tracked
              </p>
            )}
          </div>
          <SyncPanel />
        </div>

        {/* Filters */}
        <div className="mb-5">
          <DashboardFilters filters={filters} onChange={setFilters} />
        </div>

        {/* Table */}
        {isLoading && (
          <div className="text-center py-20 text-gray-400">Loading…</div>
        )}
        {isError && (
          <div className="text-center py-20 text-red-500">
            Failed to load applications. Please refresh.
          </div>
        )}
        {data && <ApplicationTable applications={data.items} />}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4">
            <span className="text-sm text-gray-500">
              Page {filters.page} of {totalPages}
            </span>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                disabled={(filters.page ?? 1) <= 1}
                onClick={() => setFilters((f) => ({ ...f, page: (f.page ?? 1) - 1 }))}
              >
                Previous
              </Button>
              <Button
                variant="secondary"
                disabled={(filters.page ?? 1) >= totalPages}
                onClick={() => setFilters((f) => ({ ...f, page: (f.page ?? 1) + 1 }))}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
