import subprocess


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
    "roblox": ["Roblox"],
    "roblox game": ["Roblox"],
    "roblox player": ["Roblox"],

    # Roblox Studio
    "roblox studio": ["RobloxStudio", "Roblox Studio"],
    "studio": ["RobloxStudio", "Roblox Studio"],

    # Music production
     "fl studio": ["FL Studio 2025", "FL Studio", "FL Studio 2024", "FL Studio 21", "FL Studio 20"],
     "fl": ["FL Studio 2025", "FL Studio", "FL Studio 2024", "FL Studio 21", "FL Studio 20"],
}


def get_available_apps():
    return sorted(APP_ALIASES.keys())


def open_app(app_name):
    app_key = app_name.lower().strip()

    if app_key not in APP_ALIASES:
        return False, f"I do not recognize the application '{app_name}', Kevin."

    possible_app_names = APP_ALIASES[app_key]

    for mac_app_name in possible_app_names:
        result = subprocess.run(
            ["open", "-a", mac_app_name],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return True, f"Opening {mac_app_name}."

    return False, f"I tried to open {app_name}, but your Mac could not find it."