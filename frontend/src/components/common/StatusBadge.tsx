import type { ApplicationStatus } from "@/types";

const CONFIG: Record<ApplicationStatus, { label: string; className: string }> = {
  applied:    { label: "Applied",    className: "bg-blue-100 text-blue-700" },
  screening:  { label: "Screening",  className: "bg-yellow-100 text-yellow-700" },
  interview:  { label: "Interview",  className: "bg-purple-100 text-purple-700" },
  offer:      { label: "Offer",      className: "bg-green-100 text-green-700" },
  rejected:   { label: "Rejected",   className: "bg-red-100 text-red-600" },
  withdrawn:  { label: "Withdrawn",  className: "bg-gray-100 text-gray-500" },
};

export default function StatusBadge({ status }: { status: ApplicationStatus }) {
  const { label, className } = CONFIG[status];
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}>
      {label}
    </span>
  );
}
