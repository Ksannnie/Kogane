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

    question_starters = [
    "what",
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
]

    if command.endswith("?"):
        return "question", user_input

    for starter in question_starters:
        if command.startswith(starter + " ") or command == starter:
            return "question", user_input


    return "unknown", user_input