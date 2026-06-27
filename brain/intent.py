def detect_intent(user_input):
    text = user_input.strip().lower()
    words = set(text.split())

    if text == "":
        return "empty", None

    if any(word in words for word in ["exit", "quit", "bye", "shutdown"]):
        return "shutdown", None

    if "set mode introvert" in text:
        return "set_mode", "introvert"

    if "set mode extrovert" in text:
        return "set_mode", "extrovert"

    if "set mode watcher" in text:
        return "set_mode", "watcher"

    if text.startswith("open "):
        app_name = text.replace("open ", "", 1).strip()
        return "open_app", app_name

    if "status" in words:
        return "status", None

    if "modes" in words:
        return "modes", None

    if "mode" in words:
        return "mode", None
    
    if "apps" in words:
        return "apps", None

    if "help" in words:
        return "help", None

    if any(word in words for word in ["hello", "hi", "hey", "yo"]):
        return "greeting", None

    if "kogane" in words:
        return "summon", None

    return "unknown", None