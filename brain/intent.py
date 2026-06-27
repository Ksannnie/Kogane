def detect_intent(user_input):
    text = user_input.strip().lower()
    words = set(text.split())

    if text == "":
        return "empty"

    if any(word in words for word in ["exit", "quit", "bye", "shutdown"]):
        return "shutdown"

    if "set mode introvert" in text:
        return "set_mode_introvert"

    if "set mode extrovert" in text:
        return "set_mode_extrovert"

    if "set mode watcher" in text:
        return "set_mode_watcher"

    if "status" in words:
        return "status"

    if "modes" in words:
        return "modes"

    if "mode" in words:
        return "mode"

    if "help" in words:
        return "help"

    if any(word in words for word in ["hello", "hi", "hey", "yo"]):
        return "greeting"

    if "kogane" in words:
        return "summon"

    return "unknown"