def detect_intent(user_input):
    command = user_input.lower().strip()

    if command == "":
        return "empty", None

    if command in ["bye", "exit", "quit", "stop"]:
        return "exit", None
    
    if command in ["hello", "hi", "hey", "yo", "sup", "what's up"]:
       return "greeting", None

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

    if command in ["app help", "apps help", "application help"]:
        return "app_help", None

    if command in ["memory help", "mem help"]:
        return "memory_help", None

    if command in ["mode help", "modes help"]:
        return "mode_help", None

    if command in ["app help", "apps help", "application help"]:
        return "app_help", None

    if command in ["memory help", "mem help"]:
        return "memory_help", None

    if command in ["mode help", "modes help"]:
        return "mode_help", None

    if command in ["status", "current status"]:
        return "status", None

    if command in ["mode", "current mode"]:
        return "mode", None

    if command in ["modes", "show modes", "list modes"]:
        return "modes", None

    if command in ["apps", "show apps", "list apps", "what can you open"]:
        return "show_apps", None

    if command in ["websites", "show websites", "list websites"]:
        return "show_websites", None

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

    if any(f" {word} " in padded_command for word in open_request_words):
        # Check websites first so "open youtube" does not get treated like an app.
        for website_phrase, website_key in sorted(
            known_website_phrases.items(),
            key=lambda item: len(item[0]),
            reverse=True
        ):
            if f" {website_phrase} " in padded_command:
                return "open_website", website_key

        # Then check apps.
        for app_phrase, app_key in sorted(
            known_app_phrases.items(),
            key=lambda item: len(item[0]),
            reverse=True
        ):
            if f" {app_phrase} " in padded_command:
                return "open_app", app_key

    if command.startswith("open "):
        target_name = command.replace("open ", "", 1).strip()

        filler_words = ["my ", "the ", "a ", "an "]

        for filler in filler_words:
            if target_name.startswith(filler):
                target_name = target_name.replace(filler, "", 1).strip()

        return "open_app", target_name

    if command.startswith("set mode "):
        mode_name = command.replace("set mode ", "").strip()
        return "set_mode", mode_name

    if command == "open":
        return "missing_app", None

    if command.startswith("open "):
        app_name = command.replace("open ", "").strip()

        filler_words = ["my ", "the ", "a ", "an "]

        for filler in filler_words:
            if app_name.startswith(filler):
                app_name = app_name.replace(filler, "", 1).strip()
        return "open_app", app_name

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



    if command in ["websites", "show websites", "list websites"]:
        return "show_websites", None

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
    }

    if any(f" {word} " in padded_command for word in open_request_words):
        for website_phrase, website_key in sorted(
            known_website_phrases.items(),
            key=lambda item: len(item[0]),
            reverse=True
        ):
            if f" {website_phrase} " in padded_command:
                return "open_website", website_key

     # Natural app-opening requests
    # Examples:
    # "can you open chrome"
    # "okay so open roblox studio"
    # "how bout you open my google chrome then"
    # "pull up spotify"

    open_request_words = ["open", "launch", "start", "pull up"]

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

    padded_command = f" {command} "

    if any(f" {word} " in padded_command for word in open_request_words):
        for app_phrase, app_key in sorted(
            known_app_phrases.items(),
            key=lambda item: len(item[0]),
            reverse=True
        ):
            if f" {app_phrase} " in padded_command:
                return "open_app", app_key

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

# General conversation fallback
# If I type a normal sentence, send it to the AI brain.
    if len(command.split()) >= 2:
     return "question", user_input
    
    return "unknown", user_input