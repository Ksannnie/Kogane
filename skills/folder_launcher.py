import subprocess
from pathlib import Path


HOME = Path.home()

FOLDER_ALIASES = {
    "desktop": HOME / "Desktop",
    "downloads": HOME / "Downloads",
    "documents": HOME / "Documents",

    "kogane": HOME / "Documents" / "KOGANE",
    "kogane folder": HOME / "Documents" / "KOGANE",
    "kogane project": HOME / "Documents" / "KOGANE",
}


def get_available_folders():
    return sorted(FOLDER_ALIASES.keys())


def open_folder(folder_name):
    folder_key = folder_name.lower().strip()

    if folder_key not in FOLDER_ALIASES:
        return False, f"I do not recognize the folder '{folder_name}'."

    folder_path = FOLDER_ALIASES[folder_key]

    if not folder_path.exists():
        return False, f"I found the folder shortcut, but the path does not exist: {folder_path}"

    result = subprocess.run(
        ["open", str(folder_path)],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return True, f"Opening {folder_key}."

    return False, f"I tried to open {folder_key}, but macOS had trouble with it."