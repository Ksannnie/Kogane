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
    user_input = input(f"{user_name}: ")
    intent, data = detect_intent(user_input)

    if intent == "empty":
        kogane_speak(f"{user_name}... you gotta type something.")

    elif intent == "shutdown":
        kogane_speak(f"Session terminated. Bye bye, {user_name}.")
        break

    elif intent == "set_mode_introvert":
        change_mode("introvert")

    elif intent == "set_mode_extrovert":
        change_mode("extrovert")

    elif intent == "set_mode_watcher":
        change_mode("watcher")

    elif intent == "status":
        show_status()

    elif intent == "modes":
        show_modes()

    elif intent == "mode":
        kogane_speak(f"Current mode is {get_mode_name(current_mode)}.")

    elif intent == "open_app":
        success, message = open_app(data)
        kogane_speak(message)

    elif intent == "help":
        show_help()

    elif intent == "greeting":
        kogane_speak(f"Heyo! {user_name}, how can I assist you today?")

    elif intent == "summon":
        kogane_speak(f"I am present, {user_name}.")

    elif intent == "apps":
        show_apps()

    else:
        kogane_speak("I'm sorry. I didn't understand that command. Type 'help' for a list of commands.")