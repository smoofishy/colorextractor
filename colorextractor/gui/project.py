from dataclasses import dataclass
from pathlib import Path


@dataclass
class Project:
    """A previously opened image plus its (possibly user-renamed) title."""

    path: str
    title: str

    @classmethod
    def from_path(cls, path):
        return cls(path=path, title=Path(path).stem)
