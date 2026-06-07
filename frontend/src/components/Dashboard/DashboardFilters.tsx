import type { ApplicationFilters, ApplicationStatus } from "@/types";

const STATUSES: { value: ApplicationStatus; label: string }[] = [
  { value: "applied",   label: "Applied" },
  { value: "screening", label: "Screening" },
  { value: "interview", label: "Interview" },
  { value: "offer",     label: "Offer" },
  { value: "rejected",  label: "Rejected" },
  { value: "withdrawn", label: "Withdrawn" },
];

interface Props {
  filters: ApplicationFilters;
  onChange: (filters: ApplicationFilters) => void;
}

export default function DashboardFilters({ filters, onChange }: Props) {
  const set = (patch: Partial<ApplicationFilters>) =>
    onChange({ ...filters, ...patch, page: 1 });

  return (
    <div className="flex flex-wrap gap-3 items-center">
      {/* Search */}
      <div className="relative">
        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
          fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
        </svg>
        <input
          type="text"
          placeholder="Search company or role…"
          value={filters.search ?? ""}
          onChange={(e) => set({ search: e.target.value || undefined })}
          className="pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg w-56
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
        />
      </div>

      {/* Status */}
      <select
        value={filters.status ?? ""}
        onChange={(e) => set({ status: (e.target.value as ApplicationStatus) || undefined })}
        className="py-2 px-3 text-sm border border-gray-200 rounded-lg
          focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white"
      >
        <option value="">All statuses</option>
        {STATUSES.map((s) => (
          <option key={s.value} value={s.value}>{s.label}</option>
        ))}
      </select>

      {/* Date range */}
      <input
        type="date"
        value={filters.start_date ?? ""}
        onChange={(e) => set({ start_date: e.target.value || undefined })}
        className="py-2 px-3 text-sm border border-gray-200 rounded-lg
          focus:outline-none focus:ring-2 focus:ring-brand-500"
      />
      <span className="text-gray-400 text-sm">to</span>
      <input
        type="date"
        value={filters.end_date ?? ""}
        onChange={(e) => set({ end_date: e.target.value || undefined })}
        className="py-2 px-3 text-sm border border-gray-200 rounded-lg
          focus:outline-none focus:ring-2 focus:ring-brand-500"
      />

      {/* Clear */}
      {(filters.search || filters.status || filters.start_date || filters.end_date) && (
        <button
          onClick={() => onChange({ page: 1, page_size: filters.page_size })}
          className="text-sm text-gray-400 hover:text-gray-600 underline"
        >
          Clear
        </button>
      )}
    </div>
  );
}
