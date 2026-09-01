import webbrowser
from urllib.parse import quote_plus


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


SEARCH_URLS = {
    "google": "https://www.google.com/search?q=",
    "youtube": "https://www.youtube.com/results?search_query=",
    "yt": "https://www.youtube.com/results?search_query=",
    "github": "https://github.com/search?q=",
    "git hub": "https://github.com/search?q=",
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


def search_website(site_name, search_query):
    site_key = site_name.lower().strip()
    query = search_query.strip()

    if site_key not in SEARCH_URLS:
        return False, f"I cannot search '{site_name}' yet."

    if query == "":
        return False, "You gave me a search command, but nothing to search for."

    search_url = SEARCH_URLS[site_key] + quote_plus(query)
    webbrowser.open(search_url)

    return True, f"Searching {site_key} for {query}."