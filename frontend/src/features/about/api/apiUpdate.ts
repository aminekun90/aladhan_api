import api from "@/api/apiConfig";
import { CONFIG } from "@/const";

export interface UpdateStatus {
    pending: boolean;
    currentVersion: string;
    newVersion: string;
    votesReceived: number;
    votesRequired: number;
}

export interface ApproveResult {
    approved: boolean;
    newVersion: string;
}

const NO_UPDATE: UpdateStatus = { pending: false, currentVersion: "", newVersion: "", votesReceived: 0, votesRequired: 1 };

export async function getUpdateStatus(): Promise<UpdateStatus> {
    const status = await api.get<UpdateStatus>(CONFIG.getUpdateStatus, {
        headers: { "Content-Type": "application/json" },
    });
    return status ?? NO_UPDATE;
}

export async function approveUpdate(): Promise<ApproveResult> {
    const result = await api.post<ApproveResult>(CONFIG.approveUpdate, {}, {
        headers: { "Content-Type": "application/json" },
    });
    return result ?? { approved: false, newVersion: "" };
}
