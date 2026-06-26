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

    if user_input in["exit", "quit", "bye", "shutdown"]:
        kogane_speak(f"Session terminated. Bye Bye!, {user_name}.")
        break

    elif user_input in ["hello, hi", "kogane", "hey"]:
        kogane_speak(f"Heyo! {user_name}, how can I assist you today?")

    elif user_input == "status":
        show_status()

    elif user_input == "mode":
        kogane_speak(f"Current mode is {mode}.")
    
    elif user_input == "help":
        kogane_speak("Available commands: hello, status, mode, help, exit, quit, bye, shutdown.")

    else:
        kogane_speak("I'm sorry, I didn't understand that command. Type 'help' for a list of commands.")