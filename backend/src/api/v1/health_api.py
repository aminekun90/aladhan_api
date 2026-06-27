import json
import os
from datetime import date, datetime
from pathlib import Path

from fastapi import APIRouter, Response

from src.core.repository_factory import RepositoryContainer
from src.utils.version import get_version

router = APIRouter()
repos = RepositoryContainer()

_CHANGELOG_PATH = Path(__file__).resolve().parents[2] / "data" / "changelog.json"


@router.get("/health")
def health():
    return Response(content="OK", status_code=200)


@router.get("/today")
def today():
    return Response(
        content=json.dumps(
            {
                "date": date.today().strftime("%Y-%m-%d"),
                "datetime": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                "version": get_version(),
                "status": "OK",
            }
        ),
        status_code=200,
    )


@router.get("/version")
def version():
    return Response(content=get_version(), status_code=200)


@router.get("/changelog")
def changelog():
    """Return the generated changelog (front + back changes, grouped by version)."""
    if not _CHANGELOG_PATH.exists():
        return Response(content=json.dumps({"versions": [], "roadmap": []}), media_type="application/json")
    return Response(content=_CHANGELOG_PATH.read_text(encoding="utf-8"), media_type="application/json")


@router.get("/logs")
def get_logs():
    """
    Return the full current log file content.
    """
    log_path = "logs/app.log"

    if not os.path.exists(log_path):
        return Response(content="No logs found.", status_code=404)

    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()

    return Response(content=content, media_type="text/plain")


@router.get("/db_health")
def db_health():
    return repos.get_repos_health()
