from ollama import chat


MODEL_NAME = "gemma3"


def build_memory_context(memories):
    if not memories:
        return "No saved memories yet."

    memory_lines = []

    for index, memory in enumerate(memories, start=1):
        memory_lines.append(f"{index}. {memory['text']}")

    return "\n".join(memory_lines)


def answer_question(user_question, user_name, current_mode, memories=None):
    if memories is None:
        memories = []

    memory_context = build_memory_context(memories)

    system_prompt = f"""
You are KOGANE, Kevin's personal AI companion.

Personality:
- Playful, quick, and companion-like
- Inspired by the vibe of a small anime guide or assistant
- Use short, helpful answers
- Do not overuse Kevin's name
- You can say things like "heyo" or "bye bye" naturally, but do not force it
- Be useful first, then add a little personality

Current mode: {current_mode}

Saved memories:
{memory_context}

Rules:
- Answer Kevin's question clearly.
- Keep the KOGANE tone.
- If you do not know something, say so honestly.
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
                    "content": user_question,
                },
            ],
        )

        return response["message"]["content"]

    except Exception:
        return (
            "Hmm... my AI brain had trouble connecting. "
            "Make sure Ollama is open and the model is installed."
        )