import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { syncApi } from "@/api/sync";
import { APPLICATION_KEYS } from "@/hooks/useApplications";
import Button from "@/components/common/Button";
import type { SyncResponse } from "@/types";

export default function SyncPanel() {
  const queryClient = useQueryClient();
  const [lastResult, setLastResult] = useState<SyncResponse | null>(null);

  const { mutate, isPending } = useMutation({
    mutationFn: () => syncApi.trigger(),
    onSuccess: (data) => {
      setLastResult(data);
      queryClient.invalidateQueries({ queryKey: APPLICATION_KEYS.all });
    },
  });

  return (
    <div className="flex items-center gap-4">
      {lastResult && (
        <span className="text-xs text-gray-400">
          Last sync: +{lastResult.new_applications_found} new application
          {lastResult.new_applications_found !== 1 ? "s" : ""}
        </span>
      )}
      <Button variant="secondary" loading={isPending} onClick={() => mutate()}>
        {isPending ? "Syncing…" : "Sync now"}
      </Button>
    </div>
  );
}
