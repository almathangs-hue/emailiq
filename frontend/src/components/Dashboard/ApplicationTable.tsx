import { useNavigate } from "react-router-dom";
import { format } from "date-fns";
import type { Application } from "@/types";
import StatusBadge from "@/components/common/StatusBadge";
import ConfidenceBar from "@/components/common/ConfidenceBar";

interface Props {
  applications: Application[];
}

export default function ApplicationTable({ applications }: Props) {
  const navigate = useNavigate();

  if (applications.length === 0) {
    return (
      <div className="text-center py-20 text-gray-400">
        <p className="text-lg font-medium text-gray-500">No applications found</p>
        <p className="text-sm mt-1">Try syncing your Gmail or adjusting your filters.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-100">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
            <th className="px-4 py-3">Company</th>
            <th className="px-4 py-3">Role</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Applied</th>
            <th className="px-4 py-3">Last Activity</th>
            <th className="px-4 py-3">Score</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-50">
          {applications.map((app) => (
            <tr
              key={app.id}
              onClick={() => navigate(`/applications/${app.id}`)}
              className="bg-white hover:bg-brand-50 cursor-pointer transition-colors"
            >
              <td className="px-4 py-3.5 font-medium text-gray-900">{app.company_name}</td>
              <td className="px-4 py-3.5 text-gray-600">{app.role_title ?? "—"}</td>
              <td className="px-4 py-3.5">
                <StatusBadge status={app.status} />
                {app.status_overridden && (
                  <span className="ml-1.5 text-xs text-gray-400">edited</span>
                )}
              </td>
              <td className="px-4 py-3.5 text-gray-500">
                {format(new Date(app.applied_at), "MMM d, yyyy")}
              </td>
              <td className="px-4 py-3.5 text-gray-500">
                {format(new Date(app.last_activity_at), "MMM d, yyyy")}
              </td>
              <td className="px-4 py-3.5">
                <ConfidenceBar score={app.confidence_score} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
