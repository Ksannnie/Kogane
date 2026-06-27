from brain.intent import detect_intent
from skills.app_launcher import get_available_apps, open_app
from personality.modes import (
    get_activation_message,
    get_all_modes,
    get_mode_name,
    is_valid_mode,
)


assistant_name = "Kogane"
user_name = "Kevin"
current_mode = "introvert"


def kogane_speak(message):
    print(f"{assistant_name}: {message}")


def startup_status():
    kogane_speak(f"Awaiting your command, {user_name}.")
    kogane_speak(f"Current mode is {get_mode_name(current_mode)}.")


def show_status():
    kogane_speak(f"Current mode is {get_mode_name(current_mode)}.")


def show_help():
    kogane_speak(
        "Available commands: hello, status, mode, modes, "
        "set mode introvert, set mode extrovert, set mode watcher, "
        "open chrome, open spotify, open vscode, open fl studio, help, bye."
    )


def show_modes():
    kogane_speak("Available modes:")

    for mode_key, mode_info in get_all_modes().items():
        kogane_speak(f"{mode_info['name']} - {mode_info['description']}")


def change_mode(new_mode):
    global current_mode

    if is_valid_mode(new_mode):
        current_mode = new_mode
        kogane_speak(get_activation_message(new_mode, user_name))
    else:
        kogane_speak("Unknown mode. Available modes are: introvert, extrovert, watcher.")


def show_apps():
    kogane_speak("Apps I can open:")

    for app_key in get_available_apps():
        kogane_speak(f"- {app_key}")


startup_status()

while True:
    user_input = input("Kevin: ")
    intent, data = detect_intent(user_input)

    if intent == "empty":
        kogane_speak("You summoned silence, Kevin. Very mysterious.")

    elif intent == "greeting":
        kogane_speak("I am present, Kevin. What do you require?")

    elif intent == "exit":
        kogane_speak("Session terminated. Goodbye, Kevin.")
        break

    elif intent == "help":
        show_help()

    elif intent == "status":
        show_status()

    elif intent == "mode":
        show_status()

    elif intent == "modes":
        show_modes()

    elif intent == "set_mode":
        change_mode(data)

    elif intent == "show_apps":
        show_apps()

    elif intent == "missing_app":
        kogane_speak("You said open, but did not name an app, Kevin.")
        kogane_speak("Try something like: open chrome, open spotify, or open fl studio.")

    elif intent == "open_app":
        success, message = open_app(data)
        kogane_speak(message)

    elif intent == "unknown":
        kogane_speak(f"I do not understand '{data}' yet, Kevin.")
        kogane_speak("Type 'help' to see what I can currently do.")