import json
import os
import sys
from pathlib import Path

from .project import Project

APP_NAME = "Color Extractor"


def _config_dir() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / APP_NAME


def _recent_file() -> Path:
    return _config_dir() / "recent_projects.json"


def load_recent_projects():
    """Load previously opened projects, skipping any whose file no longer exists."""
    try:
        data = json.loads(_recent_file().read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []

    projects = []
    for entry in data:
        try:
            project = Project(path=entry["path"], title=entry["title"])
        except (KeyError, TypeError):
            continue
        if Path(project.path).exists():
            projects.append(project)
    return projects


def save_recent_projects(projects):
    config_dir = _config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    data = [{"path": p.path, "title": p.title} for p in projects]

    recent_file = _recent_file()
    tmp_path = recent_file.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(data, indent=2))
    tmp_path.replace(recent_file)
