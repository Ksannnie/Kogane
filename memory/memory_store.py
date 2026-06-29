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


def normalize_fact(fact):
    return fact.strip().lower()


def remember_fact(fact):
    memory_data = load_memory()
    clean_fact = normalize_fact(fact)

    if clean_fact == "":
        return False, "You did not give me anything to remember."

    for saved_fact in memory_data.get("facts", []):
        if saved_fact["text"] == clean_fact:
            return False, "I already remember that."

    memory_data["facts"].append({
        "text": clean_fact,
        "created_at": datetime.now().isoformat(timespec="seconds")
    })

    save_memory(memory_data)
    return True, "I will remember that."


def get_facts():
    memory_data = load_memory()
    return memory_data.get("facts", [])


def delete_fact(memory_number):
    memory_data = load_memory()
    facts = memory_data.get("facts", [])

    try:
        index = int(memory_number) - 1
    except ValueError:
        return False, "That memory number is not valid."

    if index < 0 or index >= len(facts):
        return False, "I could not find a memory with that number."

    removed_fact = facts.pop(index)
    memory_data["facts"] = facts
    save_memory(memory_data)

    return True, f"I deleted memory {memory_number}: {removed_fact['text']}"


def clear_all_memories():
    save_memory({"facts": []})
    return True, "All memories have been cleared."