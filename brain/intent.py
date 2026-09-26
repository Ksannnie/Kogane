def detect_intent(user_input):
    """Return the first matching intent and its data in routing priority order."""
    command = user_input.lower().strip()

    # Empty input
    if command == "":
        return "empty", None

    # Quit commands
    if command in ["bye", "exit", "quit", "stop"]:
        return "exit", None

    # Greetings
    if command in ["hello", "hi", "hey", "yo", "sup", "what's up"]:
        return "greeting", None

    # Help commands
    if command in [
        "help",
        "commands",
        "what can you do",
        "what can you do?",
        "what can you respond to",
        "what can you respond to?",
        "abilities",
        "show commands",
    ]:
        return "help", None

    if command in ["search help", "search commands", "website search help"]:
        return "search_help", None

    if command in ["website help", "websites help", "website commands"]:
        return "website_help", None

    if command in ["folder help", "folders help", "folder commands"]:
        return "folder_help", None

    if command in ["project help", "project commands"]:
        return "project_help", None

    if command in ["app help", "apps help", "application help"]:
        return "app_help", None

    if command in ["memory help", "mem help"]:
        return "memory_help", None

    if command in ["mode help", "modes help"]:
        return "mode_help", None

    # Status and mode commands
    if command in ["status", "current status"]:
        return "status", None

    if command in ["mode", "current mode"]:
        return "mode", None

    if command in ["modes", "show modes", "list modes"]:
        return "modes", None

    # App and website lists
    if command in ["apps", "show apps", "list apps", "what can you open"]:
        return "show_apps", None

    if command in ["websites", "show websites", "list websites"]:
        return "show_websites", None

    # Website search (before opening, since queries can contain launch words)
    search_sites = ["google", "youtube", "yt", "github", "git hub"]

    for site in search_sites:
        search_start = f"{site} search "

        if command.startswith(search_start):
            search_query = command.replace(search_start, "", 1).strip()
            return "search_website", (site, search_query)

    if command.startswith("search google for "):
        search_query = command.replace("search google for ", "", 1).strip()
        return "search_website", ("google", search_query)

    if command.startswith("search youtube for "):
        search_query = command.replace("search youtube for ", "", 1).strip()
        return "search_website", ("youtube", search_query)

    if command.startswith("search github for "):
        search_query = command.replace("search github for ", "", 1).strip()
        return "search_website", ("github", search_query)

    # Opening aliases: websites and project shortcuts share open_website.
    open_request_words = ["open", "launch", "start", "pull up"]
    padded_command = f" {command} "

    known_website_phrases = {
        "youtube": "youtube",
        "yt": "yt",
        "github": "github",
        "git hub": "git hub",
        "chatgpt": "chatgpt",
        "chat gpt": "chat gpt",
        "google": "google",
        "canvas": "canvas",
        "odu canvas": "odu canvas",
        "odu": "odu",

        # Project shortcuts
        "kogane repo": "kogane repo",
        "github kogane": "github kogane",
        "my github": "my github",
        "canvas assignments": "canvas assignments",
        "odu email": "odu email",
    }

    known_app_phrases = {
        "google chrome": "chrome",
        "chrome": "chrome",
        "spotify": "spotify",
        "fl studio": "fl studio",
        "fl": "fl studio",
        "roblox studio": "roblox studio",
        "rblx studio": "roblox studio",
        "rbx studio": "roblox studio",
        "roblox": "roblox",
        "rblx": "roblox",
        "rbx": "roblox",
        "vs code": "vscode",
        "vscode": "vscode",
        "visual studio code": "vscode",
    }

    if command == "open":
        return "missing_app", None

    # Natural opening requests take priority over mode changes and memory.
    if any(f" {word} " in padded_command for word in open_request_words):
        # Website opening and project shortcuts: match longer aliases first.
        for website_phrase, website_key in sorted(
            known_website_phrases.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            if f" {website_phrase} " in padded_command:
                return "open_website", website_key

        # App opening: websites keep priority when both kinds of alias appear.
        for app_phrase, app_key in sorted(
            known_app_phrases.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            if f" {app_phrase} " in padded_command:
                return "open_app", app_key

    # Mode changes (after natural opening requests to preserve priority)
    if command.startswith("set mode "):
        mode_name = command.replace("set mode ", "").strip()
        return "set_mode", mode_name

    # Explicit opening: strip filler words, then try folders, websites, and apps.
    if command.startswith("open "):
        target_name = command.replace("open ", "", 1).strip()

        filler_words = ["my ", "the ", "a ", "an "]

        for filler in filler_words:
            if target_name.startswith(filler):
                target_name = target_name.replace(filler, "", 1).strip()

        # Folder opening, including singular download/document aliases
        folder_targets = [
            "desktop",
            "downloads",
            "download",
            "documents",
            "document",
            "kogane",
            "kogane folder",
            "kogane project",
        ]

        if target_name in folder_targets:
            if target_name == "download":
                target_name = "downloads"

            if target_name == "document":
                target_name = "documents"

            return "open_folder", target_name

        # Exact website and app aliases, then the unknown-app fallback
        if target_name in known_website_phrases:
            return "open_website", known_website_phrases[target_name]

        if target_name in known_app_phrases:
            return "open_app", known_app_phrases[target_name]

        return "open_app", target_name

    # Memory commands
    if command == "remember":
        return "missing_memory", None

    if command.startswith("remember that "):
        memory_text = command.replace("remember that ", "", 1).strip()
        return "remember", memory_text

    if command.startswith("remember "):
        memory_text = command.replace("remember ", "", 1).strip()
        return "remember", memory_text

    if command in ["memory", "recall", "show memory", "show memories", "what do you remember"]:
        return "recall_memory", None

    if command in ["memory count", "how many memories", "how many memories do you have"]:
        return "memory_count", None

    if command in ["delete memory", "forget memory"]:
        return "missing_delete_memory", None

    if command.startswith("delete memory "):
        memory_number = command.replace("delete memory ", "", 1).strip()
        return "delete_memory", memory_number

    if command.startswith("forget memory "):
        memory_number = command.replace("forget memory ", "", 1).strip()
        return "delete_memory", memory_number

    if command in ["clear memory", "clear memories", "forget everything"]:
        return "clear_memory", None

    # Folder lists and natural folder opening
    if command in ["folders", "show folders", "list folders"]:
        return "show_folders", None

    known_folder_phrases = {
        "desktop": "desktop",
        "downloads": "downloads",
        "documents": "documents",
        "kogane": "kogane",
        "kogane folder": "kogane folder",
        "kogane project": "kogane project",
    }

    # Preserve the existing phrase match even without an opening verb.
    for folder_phrase, folder_key in sorted(
        known_folder_phrases.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if f" {folder_phrase} " in padded_command:
            return "open_folder", folder_key

    # Question fallback
    question_starters = [
        "what",
        "what's",
        "whats",
        "why",
        "how",
        "when",
        "where",
        "who",
        "can",
        "could",
        "should",
        "would",
        "is",
        "are",
        "do",
        "does",
        "did",
        "explain",
        "tell me",
        "teach me",
    ]

    if command.endswith("?"):
        return "question", user_input

    for starter in question_starters:
        if command.startswith(starter + " ") or command == starter:
            return "question", user_input

    # General conversation: send multi-word input to the AI brain.
    if len(command.split()) >= 2:
        return "question", user_input

    return "unknown", user_input
