import sys
from pathlib import Path


def base_dir() -> Path:
    """Directory to resolve config/data paths against.

    When running as a PyInstaller executable this is the folder containing
    the .exe (not the temporary extraction folder), so a collaborator can
    keep their own .env and data/ next to the executable. In development it
    is the project root.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resolve(path: str) -> Path:
    """Resolve a possibly-relative path against base_dir()."""
    p = Path(path)
    return p if p.is_absolute() else base_dir() / p
