import subprocess
from pathlib import Path


APP_ALIASES = {
    # Browsers
    "chrome": ["Google Chrome"],
    "google chrome": ["Google Chrome"],

    # Music
    "spotify": ["Spotify"],

    # Coding
    "vscode": ["Visual Studio Code"],
    "vs code": ["Visual Studio Code"],
    "code": ["Visual Studio Code"],

    # Roblox game / player
    "roblox": ["/Applications/Roblox.app", "Roblox"],
    "roblox game": ["/Applications/Roblox.app", "Roblox"],
    "roblox player": ["/Applications/Roblox.app", "Roblox"],

    # Roblox Studio
    "roblox studio": ["/Applications/RobloxStudio.app", "RobloxStudio", "Roblox Studio"],
    "rblx studio": ["/Applications/RobloxStudio.app", "RobloxStudio", "Roblox Studio"],
    "rbx studio": ["/Applications/RobloxStudio.app", "RobloxStudio", "Roblox Studio"],
    "studio": ["/Applications/RobloxStudio.app", "RobloxStudio", "Roblox Studio"],

    # Music production
    "fl studio": ["FL Studio 2025", "FL Studio", "FL Studio 2024", "FL Studio 21", "FL Studio 20"],
    "fl": ["FL Studio 2025", "FL Studio", "FL Studio 2024", "FL Studio 21", "FL Studio 20"],
}


def get_available_apps():
    return sorted(APP_ALIASES.keys())


def open_app(app_name):
    app_key = app_name.lower().strip()

    if app_key not in APP_ALIASES:
        return False, f"I do not recognize the application '{app_name}'."

    possible_app_names = APP_ALIASES[app_key]

    for mac_app_name in possible_app_names:
        # If this is an exact app path, open the path directly.
        if mac_app_name.startswith("/"):
            app_path = Path(mac_app_name)

            if app_path.exists():
                result = subprocess.run(
                    ["open", str(app_path)],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    return True, f"Opening {app_path.stem}."

        # Otherwise, try opening by application name.
        else:
            result = subprocess.run(
                ["open", "-a", mac_app_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return True, f"Opening {mac_app_name}."

    return False, f"I tried to open {app_name}, but your Mac could not find it."