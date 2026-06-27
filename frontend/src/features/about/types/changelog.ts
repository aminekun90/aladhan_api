export type ChangeType = "feat" | "fix" | "refactor" | "perf";
export type Component = "frontend" | "backend";
export type RoadmapStatus = "planned" | "in-progress" | "idea" | "done";

export interface ChangelogEntry {
    type: ChangeType;
    scope: string | null;
    component: Component;
    summary: string;
}

export interface ChangelogVersion {
    version: string;
    date: string;
    changes: ChangelogEntry[];
}

export interface RoadmapItem {
    id: string;
    /** i18n key (e.g. "roadmap.auth"). */
    title: string;
    status: RoadmapStatus;
}

export interface Changelog {
    generatedAt: string;
    currentVersion: string;
    versions: ChangelogVersion[];
    roadmap: RoadmapItem[];
}
