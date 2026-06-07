import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { format } from "date-fns";
import { useApplication, useUpdateApplication, useSubmitFeedback } from "@/hooks/useApplications";
import type { ApplicationStatus } from "@/types";
import StatusBadge from "@/components/common/StatusBadge";
import ConfidenceBar from "@/components/common/ConfidenceBar";
import Button from "@/components/common/Button";

const STATUSES: ApplicationStatus[] = [
  "applied", "screening", "interview", "offer", "rejected", "withdrawn",
];

export default function ApplicationDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: app, isLoading, isError } = useApplication(id ?? "");
  const { mutate: update, isPending: saving } = useUpdateApplication();
  const { mutate: feedback, isPending: feedbackPending } = useSubmitFeedback();

  const [notes, setNotes] = useState<string>("");
  const [notesSynced, setNotesSynced] = useState(false);

  // Sync notes from server on first load
  if (app && !notesSynced) {
    setNotes(app.notes ?? "");
    setNotesSynced(true);
  }

  if (isLoading) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Loading…</div>;
  }
  if (isError || !app) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">Application not found.</p>
          <Button variant="secondary" onClick={() => navigate("/dashboard")}>Back to Dashboard</Button>
        </div>
      </div>
    );
  }

  const handleStatusChange = (status: ApplicationStatus) => {
    update({ id: app.id, body: { status } });
  };

  const handleSaveNotes = () => {
    update({ id: app.id, body: { notes } });
  };

  const handleFeedback = (type: "confirm" | "reject") => {
    feedback(
      { id: app.id, feedback: type },
      { onSuccess: () => type === "reject" && navigate("/dashboard") }
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 h-14 flex items-center gap-3">
          <button
            onClick={() => navigate("/dashboard")}
            className="text-gray-400 hover:text-gray-700 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span className="text-sm text-gray-500">Applications</span>
          <span className="text-gray-300">/</span>
          <span className="text-sm font-medium text-gray-800 truncate">{app.company_name}</span>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">

        {/* Header card */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{app.company_name}</h1>
              <p className="text-gray-500 mt-0.5">{app.role_title ?? "Role not detected"}</p>
            </div>
            <ConfidenceBar score={app.confidence_score} />
          </div>

          <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm text-gray-500">
            <span>Applied <strong className="text-gray-700">{format(new Date(app.applied_at), "MMM d, yyyy")}</strong></span>
            <span>Last activity <strong className="text-gray-700">{format(new Date(app.last_activity_at), "MMM d, yyyy")}</strong></span>
          </div>

          {/* Email info */}
          <div className="mt-4 bg-gray-50 rounded-xl p-4 text-sm">
            <p className="text-gray-400 text-xs uppercase tracking-wide mb-1.5">Detected from email</p>
            <p className="font-medium text-gray-700 truncate">{app.subject}</p>
            <p className="text-gray-400 text-xs mt-0.5">{app.sender_email}</p>
          </div>
        </div>

        {/* Status */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Status</h2>
          <div className="flex flex-wrap gap-2">
            {STATUSES.map((s) => (
              <button
                key={s}
                onClick={() => handleStatusChange(s)}
                className={`transition-all ${
                  app.status === s
                    ? "ring-2 ring-brand-500 ring-offset-1 scale-105"
                    : "opacity-60 hover:opacity-100"
                }`}
              >
                <StatusBadge status={s} />
              </button>
            ))}
          </div>
          {app.status_overridden && (
            <p className="text-xs text-gray-400 mt-2">Manually updated</p>
          )}
        </div>

        {/* Notes */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Notes</h2>
          <textarea
            rows={4}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add notes, contacts, follow-up reminders…"
            className="w-full text-sm border border-gray-200 rounded-xl p-3 resize-none
              focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
          />
          <div className="mt-3 flex justify-end">
            <Button loading={saving} onClick={handleSaveNotes}>
              Save notes
            </Button>
          </div>
        </div>

        {/* Feedback */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-1">Detection feedback</h2>
          <p className="text-xs text-gray-400 mb-4">
            Help improve accuracy. Confirming keeps this in your tracker; rejecting removes it.
          </p>
          <div className="flex gap-3">
            <Button
              variant="secondary"
              loading={feedbackPending}
              onClick={() => handleFeedback("confirm")}
            >
              Correct — keep it
            </Button>
            <Button
              variant="danger"
              loading={feedbackPending}
              onClick={() => handleFeedback("reject")}
            >
              Not a job application
            </Button>
          </div>
        </div>

      </main>
    </div>
  );
}
