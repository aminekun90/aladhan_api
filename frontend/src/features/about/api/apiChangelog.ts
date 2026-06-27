import api from "@/api/apiConfig";
import { CONFIG } from "@/const";
import { Changelog } from "@/features/about/types/changelog";

const EMPTY: Changelog = { generatedAt: "", currentVersion: "", versions: [], roadmap: [] };

export async function getChangelog(): Promise<Changelog> {
    const changelog = await api.get<Changelog>(CONFIG.getChangelog, {
        headers: { "Content-Type": "application/json" },
    });
    return changelog ?? EMPTY;
}

export async function getBackendVersion(): Promise<string> {
    const version = await api.get<string>(CONFIG.getBackendVersion, { headers: {} });
    return typeof version === "string" ? version.trim() : "";
}
