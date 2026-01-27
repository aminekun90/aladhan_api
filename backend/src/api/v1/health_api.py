import os
from datetime import date
from fastapi import APIRouter, Response
from src.core.repository_factory import RepositoryContainer

router = APIRouter()
repos = RepositoryContainer()

@router.get("/health")
def health():
    return Response(content="OK", status_code=200)
@router.get("/today")
def today():
    return Response(content=date.today().strftime("%Y-%m-%d %H:%M:%S"), status_code=200)
@router.get("/version")
def version():
    return Response(content="0.1.0", status_code=200)

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