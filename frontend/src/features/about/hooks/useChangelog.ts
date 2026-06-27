import { LAST_SEEN_VERSION_KEY } from "@/const";
import { getBackendVersion, getChangelog } from "@/features/about/api/apiChangelog";
import { useQuery } from "@tanstack/react-query";
import { useCallback, useMemo, useState } from "react";
import frontendPackage from "../../../../package.json";

/** Compare two semver strings. Returns >0 if a is newer than b. */
function compareVersions(a: string, b: string): number {
    const pa = a.split(".").map(Number);
    const pb = b.split(".").map(Number);
    for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
        const diff = (pa[i] ?? 0) - (pb[i] ?? 0);
        if (diff !== 0) return diff;
    }
    return 0;
}

function readLastSeen(): string | null {
    return globalThis.localStorage?.getItem(LAST_SEEN_VERSION_KEY) ?? null;
}

export function useChangelog() {
    const changelogQuery = useQuery({ queryKey: ["changelog"], queryFn: getChangelog });
    const backendVersionQuery = useQuery({ queryKey: ["backendVersion"], queryFn: getBackendVersion });

    const [lastSeen, setLastSeen] = useState<string | null>(readLastSeen);

    const changelog = changelogQuery.data;
    const latestVersion = changelog?.versions[0]?.version ?? changelog?.currentVersion ?? "";

    const hasUnseen = useMemo(() => {
        if (!latestVersion) return false;
        if (!lastSeen) return true;
        return compareVersions(latestVersion, lastSeen) > 0;
    }, [latestVersion, lastSeen]);

    const isUnseen = useCallback(
        (version: string) => !lastSeen || compareVersions(version, lastSeen) > 0,
        [lastSeen],
    );

    const markSeen = useCallback(() => {
        if (!latestVersion) return;
        globalThis.localStorage?.setItem(LAST_SEEN_VERSION_KEY, latestVersion);
        setLastSeen(latestVersion);
    }, [latestVersion]);

    return {
        changelog,
        isLoading: changelogQuery.isLoading,
        isError: changelogQuery.isError,
        frontendVersion: frontendPackage.version,
        backendVersion: backendVersionQuery.data ?? "",
        latestVersion,
        hasUnseen,
        isUnseen,
        markSeen,
    };
}
