"""Single source of truth for the backend version.

Resolves the installed package version first, falling back to parsing
``pyproject.toml`` so the value stays correct in editable/dev runs.
"""

import tomllib
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

_PACKAGE_NAME = "adhan-api"
_PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


@lru_cache(maxsize=1)
def get_version() -> str:
    try:
        return version(_PACKAGE_NAME)
    except PackageNotFoundError:
        pass

    try:
        with _PYPROJECT.open("rb") as fh:
            return tomllib.load(fh)["project"]["version"]
    except (OSError, KeyError, tomllib.TOMLDecodeError):
        return "0.0.0"
