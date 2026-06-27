import { approveUpdate, getUpdateStatus } from "@/features/about/api/apiUpdate";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

/** Polls Keel (via the backend) for a pending OTA update and approves it. */
export function useUpdateStatus({ enabled }: { enabled: boolean }) {
    const queryClient = useQueryClient();

    const statusQuery = useQuery({
        queryKey: ["updateStatus"],
        queryFn: getUpdateStatus,
        enabled,
        refetchInterval: 30_000,
    });

    const approveMutation = useMutation({
        mutationFn: approveUpdate,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["updateStatus"] }),
    });

    return {
        status: statusQuery.data,
        isLoading: statusQuery.isLoading,
        approve: approveMutation.mutate,
        isApproving: approveMutation.isPending,
        isApproved: approveMutation.isSuccess,
    };
}
