import subprocess


APPS = {
    "chrome": "Google Chrome",
    "spotify": "Spotify",
    "vscode": "Visual Studio Code",
    "code": "Visual Studio Code",
    "fl studio": "FL Studio",
    "roblox": "Roblox Studio",
    "roblox studio": "Roblox Studio",
}


def get_available_apps():
    return APPS


def open_app(app_key):
    if app_key not in APPS:
        return False, f"I do not know how to open '{app_key}' yet."

    app_name = APPS[app_key]

    try:
        subprocess.run(["open", "-a", app_name], check=True)
        return True, f"Opening {app_name}."
    except subprocess.CalledProcessError:
        return False, f"I tried to open {app_name}, but your Mac could not find it."