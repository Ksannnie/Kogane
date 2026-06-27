import json
from datetime import datetime
from pathlib import Path


MEMORY_FILE = Path(__file__).parent / "memory.json"


def load_memory():
    if not MEMORY_FILE.exists():
        return {"facts": []}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {"facts": []}


def save_memory(memory_data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory_data, file, indent=4)


def remember_fact(fact):
    memory_data = load_memory()

    memory_data["facts"].append({
        "text": fact,
        "created_at": datetime.now().isoformat(timespec="seconds")
    })

    save_memory(memory_data)


def get_facts():
    memory_data = load_memory()
    return memory_data.get("facts", [])