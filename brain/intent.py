def detect_intent(user_input):
    command = user_input.lower().strip()

    if command == "":
        return "empty", None

    if command in ["bye", "exit", "quit", "stop"]:
        return "exit", None
    
    if command in ["hello", "hi", "hey", "yo", "sup", "what's up"]:
       return "greeting", None

    if command in ["help", "commands", "what can you do"]:
        return "help", None

    if command in ["status", "current status"]:
        return "status", None

    if command in ["mode", "current mode"]:
        return "mode", None

    if command in ["modes", "show modes", "list modes"]:
        return "modes", None

    if command in ["apps", "show apps", "list apps", "what can you open"]:
        return "show_apps", None

    if command.startswith("set mode "):
        mode_name = command.replace("set mode ", "").strip()
        return "set_mode", mode_name

    if command == "open":
        return "missing_app", None

    if command.startswith("open "):
        app_name = command.replace("open ", "").strip()
        return "open_app", app_name

    return "unknown", user_input