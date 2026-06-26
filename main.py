assistant_name = "Kogane"
user_name = "Kevin"
mode = "Silent Mode"

def kogane_speak(message):
    print(f"{assistant_name}: {message}")


def show_status():
    kogane_speak(f"Awaiting your command, {user_name}.")
    kogane_speak(f"Current mode is: {mode}.")


show_status()

while True:
    user_input = input(f"{user_name}: ").strip().lower()

    if user_input == "":
        kogane_speak(f"Kevin... you gotta type something.")
    
    elif any(word in user_input for word in ["exit", "quit", "bye", "shutdown"]):
        kogane_speak(f"Session terminated. Bye bye!, {user_name}.")
        break

    elif any(word in user_input for word in ["hello", "hi", "hey", "kogane"]):
        kogane_speak(f"Heyo! {user_name}, how can I assist you today?")

    elif "status" in user_input:
        show_status()

    elif "mode" in user_input:
        kogane_speak(f"Current mode is {mode}.")

    elif "help" in user_input:
        kogane_speak("Available commands: hello, status, mode, help, exit, quit, bye, shutdown.")

    else:
        kogane_speak("I'm sorry. I didn't understand that command. Type 'help' for a list of commands.")