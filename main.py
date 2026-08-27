from brain.intent import detect_intent
from skills.app_launcher import get_available_apps, open_app
from brain.ai_brain import answer_question
from memory.memory_store import (
    remember_fact,
    get_facts,
    delete_fact,
    clear_all_memories as clear_memory_store,
)
from personality.modes import (
    get_activation_message,
    get_all_modes,
    get_mode_name,
    is_valid_mode,
)
from personality.responses import (
    get_greeting,
    get_farewell,
    get_empty_response,
    get_unknown_response,
    get_question_response,
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
    kogane_speak("Here is what I can do right now.")

    kogane_speak("Chat:")
    kogane_speak("- Ask me questions normally")
    kogane_speak("- Example: what is an API?")
    kogane_speak("- Example: explain python imports")

    kogane_speak("Apps:")
    kogane_speak("- open chrome")
    kogane_speak("- open spotify")
    kogane_speak("- open fl studio")
    kogane_speak("- open roblox")
    kogane_speak("- open roblox studio")
    kogane_speak("- You can also say things like: can you open chrome")

    kogane_speak("Memory:")
    kogane_speak("- remember that ...")
    kogane_speak("- memory")
    kogane_speak("- memory count")
    kogane_speak("- delete memory 1")
    kogane_speak("- clear memory")

    kogane_speak("Modes:")
    kogane_speak("- mode")
    kogane_speak("- modes")
    kogane_speak("- set mode introvert")
    kogane_speak("- set mode extrovert")
    kogane_speak("- set mode watcher")

    kogane_speak("Other:")
    kogane_speak("- hello")
    kogane_speak("- status")
    kogane_speak("- bye")


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

def remember_memory(memory_text):
    success, message = remember_fact(memory_text)
    kogane_speak(message)


def show_memory():
    facts = get_facts()

    if not facts:
        kogane_speak("I do not have any saved memories yet.")
        return

    kogane_speak("Here’s what I remember.")

    for index, fact in enumerate(facts, start=1):
        kogane_speak(f"{index}. {fact['text']}")


def delete_memory(memory_number):
    success, message = delete_fact(memory_number)
    kogane_speak(message)


def clear_memory():
    success, message = clear_memory_store()
    kogane_speak(message)

def show_memory_count():
    facts = get_facts()
    count = len(facts)

    if count == 0:
        kogane_speak("I do not have any saved memories yet.")
    elif count == 1:
        kogane_speak("I currently have 1 saved memory.")
    else:
        kogane_speak(f"I currently have {count} saved memories.")

startup_status()

while True:
    user_input = input("Kevin: ")
    intent, data = detect_intent(user_input)

    if intent == "empty":
       kogane_speak(get_empty_response(user_name))

    elif intent == "greeting":
        kogane_speak(get_greeting(current_mode, user_name))

    elif intent == "exit":
       kogane_speak(get_farewell(current_mode, user_name))
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

    elif intent == "missing_memory":
        kogane_speak("You told me to remember, but did not give me anything to store.")
        kogane_speak("Try: remember that I am building KOGANE.")
        
    elif intent == "remember":
        remember_memory(data)
        
    elif intent == "recall_memory":
        show_memory()
  
    elif intent == "memory_count":
        show_memory_count()

    elif intent == "missing_delete_memory":
        kogane_speak("Tell me which memory to delete.")
        kogane_speak("Try: delete memory 1")

    elif intent == "delete_memory":
        delete_memory(data)

    elif intent == "clear_memory":
        clear_memory()
    
    elif intent == "question":
        memories = get_facts()
        response = answer_question(data, user_name, current_mode, memories)
        kogane_speak(response)

    elif intent == "unknown":
        kogane_speak(get_unknown_response(data, user_name))