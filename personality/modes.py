MODES = {
    "introvert": {
        "name": "Introvert Mode",
        "description": "I only speak when called upon.",
        "activation": "Introvert Mode activated. I shall remain quiet until summoned, {user_name}.",
    },
    "extrovert": {
        "name": "Extrovert Mode",
        "description": "I may speak proactively, but not annoyingly.",
        "activation": "Extrovert Mode activated. I may speak freely... within reason, of course.",
    },
    "watcher": {
        "name": "Watcher Mode",
        "description": "I observe through vision features once they exist.",
        "activation": "Watcher Mode activated. I shall observe... respectfully, of course.",
    },
}


def is_valid_mode(mode_key):
    return mode_key in MODES


def get_mode_name(mode_key):
    return MODES[mode_key]["name"]


def get_activation_message(mode_key, user_name):
    return MODES[mode_key]["activation"].format(user_name=user_name)


def get_all_modes():
    return MODES