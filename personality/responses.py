import random


GREETINGS = {
    "introvert": [
        "Heyo, Kevin.",
        "Oh. Hey, Kevin.",
        "I'm here, Kevin. Quietly, as requested.",
        "Heyo. Standing by."
    ],
    "extrovert": [
        "Heyo, Kevin!",
        "Kevin! Heyo! What are we doing?",
        "There you are, Kevin!",
        "Heyo heyo! KOGANE is awake."
    ],
    "watcher": [
        "Heyo, Kevin. I'm watching... respectfully.",
        "KOGANE is here. Eyes open.",
        "Heyo. Observation mode vibes.",
        "I'm awake, Kevin. Nothing suspicious yet."
    ]
}


FAREWELLS = {
    "introvert": [
        "Bye bye, Kevin.",
        "Session closed. Bye bye.",
        "I'll be quiet now. Bye bye, Kevin."
    ],
    "extrovert": [
        "Bye bye, Kevin!",
        "Later, Kevin! KOGANE out!",
        "Bye byeee!"
    ],
    "watcher": [
        "Bye bye, Kevin. I'll stop observing now.",
        "Watcher mode resting. Bye bye.",
        "KOGANE going dark. Bye bye."
    ]
}


EMPTY_RESPONSES = [
    "You typed absolutely nothing, Kevin.",
    "Silence. Very dramatic.",
    "No command detected. Mysterious.",
    "Kevin, I cannot read invisible text yet."
]


UNKNOWN_RESPONSES = [
    "Hmm... I don't know that one yet, Kevin.",
    "That command is not in my brain yet.",
    "I heard you, but I don't understand that command yet.",
    "Noted. Confusing, but noted."
]


def get_greeting(mode, user_name):
    responses = GREETINGS.get(mode, GREETINGS["introvert"])
    return random.choice(responses).replace("Kevin", user_name)


def get_farewell(mode, user_name):
    responses = FAREWELLS.get(mode, FAREWELLS["introvert"])
    return random.choice(responses).replace("Kevin", user_name)


def get_empty_response(user_name):
    return random.choice(EMPTY_RESPONSES).replace("Kevin", user_name)


def get_unknown_response(user_input, user_name):
    response = random.choice(UNKNOWN_RESPONSES)
    return f"{response} Type 'help' if you want to see what I can do."


def get_question_response(user_name):
    return (
        f"That sounds like a real question, {user_name}. "
        "My general AI brain is not connected yet, but that is coming soon."
    )