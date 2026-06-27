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


def show_status():
    kogane_speak(f"Awaiting your command, {user_name}.")
    kogane_speak(f"Current mode is {get_mode_name(current_mode)}.")


def show_help():
    kogane_speak(
        "Available commands: hello, status, mode, modes, "
        "set mode introvert, set mode extrovert, set mode watcher, help, bye."
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


show_status()

while True:
    user_input = input(f"{user_name}: ").strip().lower()
    words = user_input.split()

    if user_input == "":
        kogane_speak(f"{user_name}... you gotta type something.")

    elif any(word in words for word in ["exit", "quit", "bye", "shutdown"]):
        kogane_speak(f"Session terminated. Bye bye, {user_name}.")
        break

    elif "set mode introvert" in user_input:
        change_mode("introvert")

    elif "set mode extrovert" in user_input:
        change_mode("extrovert")

    elif "set mode watcher" in user_input:
        change_mode("watcher")

    elif "status" in words:
        show_status()

    elif "modes" in words:
        show_modes()

    elif "mode" in words:
        kogane_speak(f"Current mode is {get_mode_name(current_mode)}.")

    elif "help" in words:
        show_help()

    elif any(word in words for word in ["hello", "hi", "hey", "yo"]):
        kogane_speak(f"Heyo! {user_name}, how can I assist you today?")

    elif "kogane" in words:
        kogane_speak(f"I am present, {user_name}.")

    else:
        kogane_speak("I'm sorry. I didn't understand that command. Type 'help' for a list of commands.")