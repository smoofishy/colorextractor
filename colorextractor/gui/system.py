import subprocess
import sys
from pathlib import Path


def reveal_in_file_manager(path):
    """Open the OS file manager with the given file selected/highlighted."""
    resolved = str(Path(path).resolve())
    if sys.platform == "darwin":
        subprocess.run(["open", "-R", resolved], check=False)
    elif sys.platform.startswith("win"):
        subprocess.run(["explorer", "/select,", resolved], check=False)
    else:
        subprocess.run(["xdg-open", str(Path(resolved).parent)], check=False)
