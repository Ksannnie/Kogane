from brain.intent import detect_intent
from skills.app_launcher import get_available_apps, open_app
from brain.ai_brain import answer_question
from skills.website_launcher import (
    get_available_websites,
    open_website,
    search_website,
)
from skills.folder_launcher import get_available_folders, open_folder
from memory.memory_store import (
    remember_fact,
    get_facts,
    delete_fact,
    clear_all_memories as clear_memory_store,
)
from memory.schedule_store import (
    add_event,
    delete_event,
    list_upcoming_events,
    list_today_events,
    list_tomorrow_events,
    list_week_events,
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
displayed_schedule_events = None
current_schedule_view = "upcoming"


def kogane_speak(message):
    print(f"{assistant_name}: {message}")


def startup_status():
    kogane_speak(f"Awaiting your command, {user_name}.")
    kogane_speak(f"Current mode is {get_mode_name(current_mode)}.")


def show_status():
    kogane_speak(f"Current mode is {get_mode_name(current_mode)}.")


def show_help():
    kogane_speak("- Open apps")
    kogane_speak("- Open websites and folders")
    kogane_speak("- Search Google, YouTube, and GitHub")
    kogane_speak("- Start coding, school, or music workflows")
    kogane_speak("- Save and recall memories")
    kogane_speak("- Save events and check your schedule")
    kogane_speak("- Switch personality modes")
    kogane_speak(
        "Try: app help, website help, search help, folder help, project help, "
        "workflow help, schedule help, memory help, or mode help."
    )


def show_app_help():
    kogane_speak("App commands:")
    kogane_speak("- open chrome")
    kogane_speak("- open spotify")
    kogane_speak("- open fl studio")
    kogane_speak("- open roblox")
    kogane_speak("- open roblox studio")
    kogane_speak("- can you open chrome")
    kogane_speak("- pull up spotify")


def show_website_help():
    kogane_speak("Website commands:")
    kogane_speak("- websites")
    kogane_speak("- open youtube")
    kogane_speak("- open github")
    kogane_speak("- open chatgpt")
    kogane_speak("- open canvas")
    kogane_speak("- open google")
    kogane_speak("- pull up github")
    kogane_speak("- can you open chatgpt")


def show_memory_help():
    kogane_speak("Memory commands:")
    kogane_speak("- remember that ...")
    kogane_speak("- memory")
    kogane_speak("- memory count")
    kogane_speak("- delete memory 1")
    kogane_speak("- clear memory")


def show_schedule_help():
    kogane_speak("Schedule commands:")
    kogane_speak("- schedule help / calendar help")
    kogane_speak("- add event YYYY-MM-DD HH:MM event title")
    kogane_speak("- add event YYYY-MM-DD event title (all day)")
    kogane_speak("- schedule / calendar: today and later")
    kogane_speak("- today / tomorrow")
    kogane_speak("- this week: today and the next six days")
    kogane_speak("- delete event NUMBER: use the number in the last displayed list")
    kogane_speak("Dates and 24-hour times use your computer's local time.")


def show_schedule(view):
    global displayed_schedule_events, current_schedule_view

    views = {
        "upcoming": list_upcoming_events,
        "today": list_today_events,
        "tomorrow": list_tomorrow_events,
        "this week": list_week_events,
    }
    displayed_schedule_events = None
    events = views[view]()
    displayed_schedule_events = events
    current_schedule_view = view

    if not events:
        kogane_speak("No events found, Kevin.")
        return

    kogane_speak(f"Your schedule ({view}):")
    for number, event in enumerate(events, start=1):
        event_time = event["time"] or "All day"
        kogane_speak(f"{number}. {event['date']} {event_time} - {event['title']}")


def handle_schedule_command(intent, data):
    try:
        if intent == "show_schedule":
            show_schedule(data)
        elif intent == "add_event":
            success, message = add_event(data)
            kogane_speak(message)
            if success:
                show_schedule("upcoming")
        elif intent == "delete_event":
            success, message = delete_event(data, displayed_schedule_events)
            kogane_speak(message)
            if success:
                show_schedule(current_schedule_view)
    except (OSError, ValueError) as error:
        kogane_speak(f"I could not finish that schedule request: {error}")


def show_mode_help():
    kogane_speak("Mode commands:")
    kogane_speak("- mode")
    kogane_speak("- modes")
    kogane_speak("- set mode introvert")
    kogane_speak("- set mode extrovert")
    kogane_speak("- set mode watcher")

def show_modes():
    kogane_speak("Available modes:")

    for mode_key, mode_info in get_all_modes().items():
        kogane_speak(f"{mode_info['name']} - {mode_info['description']}")

def show_search_help():
    kogane_speak("Search commands:")
    kogane_speak("- google search esp32 s3 pinout")
    kogane_speak("- youtube search python classes tutorial")
    kogane_speak("- github search ollama python")
    kogane_speak("- search google for kogane jjk")
    kogane_speak("- search youtube for gamemaker tutorial")
    kogane_speak("- search github for esp32 projects")


def show_folder_help():
    kogane_speak("Folder commands:")
    kogane_speak("- folders")
    kogane_speak("- open downloads")
    kogane_speak("- open documents")
    kogane_speak("- open desktop")
    kogane_speak("- open kogane folder")
    kogane_speak("- pull up my kogane project")


def show_project_help():
    kogane_speak("Project commands:")
    kogane_speak("- open kogane repo")
    kogane_speak("- open github kogane")
    kogane_speak("- open my github")
    kogane_speak("- open canvas assignments")
    kogane_speak("- open odu email")


def show_workflow_help():
    kogane_speak("Workflow commands:")
    kogane_speak("- start coding: KOGANE project folder, KOGANE GitHub repo, and VS Code")
    kogane_speak("- start school: Canvas assignments, ODU email, and ChatGPT")
    kogane_speak("- start music: Spotify and YouTube")


def start_workflow(workflow_name):
    workflows = {
        "coding": [
            (open_folder, "kogane folder"),
            (open_website, "kogane repo"),
            (open_app, "vscode"),
        ],
        "school": [
            (open_website, "canvas assignments"),
            (open_website, "odu email"),
            (open_website, "chatgpt"),
        ],
        "music": [
            (open_app, "spotify"),
            (open_website, "youtube"),
        ],
    }

    kogane_speak(f"Starting {workflow_name} workflow.")

    for launcher, target in workflows[workflow_name]:
        success, message = launcher(target)
        kogane_speak(message)


def change_mode(new_mode):
    global current_mode

    if is_valid_mode(new_mode):
        current_mode = new_mode
        kogane_speak(get_activation_message(new_mode, user_name))
    else:
        kogane_speak("Unknown mode. Available modes are: introvert, extrovert, watcher.")

def show_websites():
    kogane_speak("Websites I can open:")

    for site_key in get_available_websites():
        kogane_speak(f"- {site_key}")

def show_folders():
    kogane_speak("Folders I can open:")

    for folder_key in get_available_folders():
        kogane_speak(f"- {folder_key}")

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

    elif intent == "app_help":
        show_app_help()

    elif intent == "website_help":
        show_website_help()

    elif intent == "memory_help":
        show_memory_help()

    elif intent == "schedule_help":
        show_schedule_help()

    elif intent in ["add_event", "show_schedule", "delete_event"]:
        handle_schedule_command(intent, data)

    elif intent == "mode_help":
        show_mode_help()

    elif intent == "search_help":
        show_search_help()

    elif intent == "folder_help":
        show_folder_help()

    elif intent == "project_help":
        show_project_help()

    elif intent == "workflow_help":
        show_workflow_help()

    elif intent == "start_workflow":
        start_workflow(data)

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
        folder_targets = [
            "desktop",
            "downloads",
            "download",
            "documents",
            "document",
            "kogane",
            "kogane folder",
            "kogane project",
        ]

        app_target = data.lower().strip()

        if app_target in folder_targets:
            if app_target == "download":
                app_target = "downloads"

            if app_target == "document":
                app_target = "documents"

            success, message = open_folder(app_target)
        else:
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

    elif intent == "show_websites":
        show_websites()

    elif intent == "open_website":
        success, message = open_website(data)
        kogane_speak(message)

    elif intent == "search_website":
        site_name, search_query = data
        success, message = search_website(site_name, search_query)
        kogane_speak(message)

    elif intent == "show_folders":
        show_folders()

    elif intent == "open_folder":
        success, message = open_folder(data)
        kogane_speak(message)
