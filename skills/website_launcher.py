import webbrowser


WEBSITE_ALIASES = {
    "youtube": "https://www.youtube.com",
    "yt": "https://www.youtube.com",

    "github": "https://github.com",
    "git hub": "https://github.com",

    "chatgpt": "https://chatgpt.com",
    "chat gpt": "https://chatgpt.com",

    "google": "https://www.google.com",

    "canvas": "https://canvas.odu.edu",
    "odu canvas": "https://canvas.odu.edu",

    "odu": "https://www.odu.edu",
}


def get_available_websites():
    return sorted(WEBSITE_ALIASES.keys())


def open_website(site_name):
    site_key = site_name.lower().strip()

    if site_key not in WEBSITE_ALIASES:
        return False, f"I do not recognize the website '{site_name}'."

    website_url = WEBSITE_ALIASES[site_key]
    webbrowser.open(website_url)

    return True, f"Opening {site_key}."