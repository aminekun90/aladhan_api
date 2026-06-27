#!/usr/bin/env python3
"""Generate src/data/changelog.json from the git history.

Buckets conventional commits (feat/fix/refactor/perf) by version, using release
commits (``bump version to X``, ``version X``, ``release X``) as boundaries.
Each change is tagged ``frontend`` or ``backend`` from its commit scope so the
About dialog can show "what's new" per side.

The curated ``roadmap`` array is preserved across regenerations — edit it by
hand in the output file; this script never overwrites it.

Run from the backend/ directory at release time and commit the result:
    uv run python scripts/gen_changelog.py
"""

import json
import re
import subprocess
import tomllib
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
OUTPUT = BACKEND_DIR / "src" / "data" / "changelog.json"

KEPT_TYPES = {"feat", "fix", "refactor", "perf"}
FRONTEND_SCOPES = {"frontend", "front", "ui", "web"}

RELEASE_RE = re.compile(r"(?:bump version to|^version|^release|^chore\(release\))\D*(\d+\.\d+\.\d+)", re.I)
CONVENTIONAL_RE = re.compile(r"^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?!?:\s*(?P<summary>.+)$")

DEFAULT_ROADMAP = [
    {"id": "dns-resilience", "title": "about.roadmap.dnsResilience", "status": "planned"},
    {"id": "auth", "title": "about.roadmap.auth", "status": "planned"},
    {"id": "notifications", "title": "about.roadmap.notifications", "status": "idea"},
]


def backend_version() -> str:
    with (BACKEND_DIR / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)["project"]["version"]


def git_log() -> list[dict]:
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "log", "--pretty=%H%x1f%s%x1f%cI"],
        capture_output=True, text=True, check=True,
    ).stdout
    commits = []
    for line in out.splitlines():
        if not line.strip():
            continue
        sha, subject, iso = line.split("\x1f")
        commits.append({"sha": sha, "subject": subject, "date": iso[:10]})
    return commits


def component_for(scope: str | None) -> str:
    return "frontend" if scope and scope.lower() in FRONTEND_SCOPES else "backend"


def build_versions(commits: list[dict], current_version: str) -> list[dict]:
    sections: dict[str, dict] = {}
    order: list[str] = []
    current = current_version
    current_date = commits[0]["date"] if commits else datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for commit in commits:
        release = RELEASE_RE.search(commit["subject"])
        if release:
            current = release.group(1)
            current_date = commit["date"]
            continue
        match = CONVENTIONAL_RE.match(commit["subject"])
        if not match or match.group("type").lower() not in KEPT_TYPES:
            continue
        scope = match.group("scope")
        section = sections.get(current)
        if section is None:
            section = {"version": current, "date": current_date, "changes": []}
            sections[current] = section
            order.append(current)
        section["changes"].append({
            "type": match.group("type").lower(),
            "scope": scope,
            "component": component_for(scope),
            "summary": match.group("summary").strip(),
        })

    return [sections[v] for v in order if sections[v]["changes"]]


def load_roadmap() -> list[dict]:
    if OUTPUT.exists():
        try:
            existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
            if existing.get("roadmap"):
                return existing["roadmap"]
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_ROADMAP


def main() -> None:
    version = backend_version()
    data = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "currentVersion": version,
        "versions": build_versions(git_log(), version),
        "roadmap": load_roadmap(),
    }
    OUTPUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} — {len(data['versions'])} versions")


if __name__ == "__main__":
    main()
