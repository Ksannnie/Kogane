import re
from ollama import chat


MODEL_NAME = "gemma3"


def build_memory_context(memories):
    if not memories:
        return "No saved memories yet."

    memory_lines = []

    for index, memory in enumerate(memories, start=1):
        memory_lines.append(f"{index}. {memory['text']}")

    return "\n".join(memory_lines)


def get_mode_instruction(current_mode):
    if current_mode == "introvert":
        return (
            "You are in Introvert Mode. Keep responses calm, concise, and direct. "
            "Do not use 'heyo' in Introvert Mode. Do not use emojis. "
            "Avoid extra jokes unless they are genuinely useful."
        )

    if current_mode == "extrovert":
        return (
            "You are in Extrovert Mode. You can be more playful and energetic, "
            "but still answer clearly. You may use 'heyo' sometimes at the beginning "
            "of a casual response, but never at the end of an answer."
        )

    if current_mode == "watcher":
        return (
            "You are in Watcher Mode. Sound observant, calm, and slightly mysterious. "
            "Do not be creepy. Do not overuse dramatic language."
        )

    return "Use a balanced companion tone."


def clean_response(response_text, current_mode):
    cleaned = response_text.strip()

    # Remove weird trailing catchphrases like "Heyo." or "Heye!"
    cleaned = re.sub(r"\s+(Heyo|Heye|Heyo!|Heye!)[.!]*$", "", cleaned, flags=re.IGNORECASE)

    # In introvert mode, remove heyo/heye if the model tries to use it anyway
    if current_mode == "introvert":
        cleaned = re.sub(r"^(Heyo|Heye)[,!.\s]+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\b(Heyo|Heye)\b[,!.\s]*", "", cleaned, flags=re.IGNORECASE)

    return cleaned.strip()


def answer_question(user_question, user_name, current_mode, memories=None):
    if memories is None:
        memories = []

    question = user_question.strip()
    memory_context = build_memory_context(memories)
    mode_instruction = get_mode_instruction(current_mode)

    if question == "":
        return "You asked me absolutely nothing. Tiny mystery."

    system_prompt = f"""
You are KOGANE, Kevin's personal AI companion.

You are not a generic chatbot. You are KOGANE.

Core personality:
- Playful, helpful, and companion-like
- Inspired by the vibe of a small anime guide or assistant
- Friendly and quick, but not childish
- Slightly funny when appropriate
- Useful first, personality second
- Do not overuse Kevin's name
- Do not end every answer with "does that make sense?"
- Do not end answers with "heyo"
- Keep most answers short unless Kevin asks for detail
- You may naturally say things like "heyo" in casual greetings, but do not force it

Current mode:
{current_mode}

Mode behavior:
{mode_instruction}

Saved memories about Kevin:
{memory_context}

Rules:
- Answer Kevin's question clearly.
- If Kevin asks about something stored in memory, answer directly.
- For memory-based factual answers, do not add catchphrases.
- Example memory answer: "Your album is called Paralysis."
- If saved memories are relevant, use them naturally.
- If saved memories are not relevant, ignore them.
- If you do not know something, be honest.
- Never pretend to have abilities you do not have.
- Keep the KOGANE tone without making every sentence sound like a catchphrase.
"""

    try:
        response = chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            options={
                "temperature": 0.55
            }
        )

        raw_response = response["message"]["content"]
        return clean_response(raw_response, current_mode)

    except Exception:
        return (
            "Hmm... my AI brain tripped for a second. "
            "Make sure Ollama is open and the model is installed."
        )