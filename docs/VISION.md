# KOGANE Vision

## Purpose

KOGANE is a personal AI companion project inspired by the Kogane companion from Jujutsu Kaisen. The goal is not to create a generic chatbot, but a persistent desktop assistant with a recognizable personality, personal memory, helpful automation, and a long-term path toward a physical robotic companion.

The project is intentionally staged. The current implementation is a terminal-driven desktop assistant. The future vision includes voice, vision, robotics, and a safely engineered autonomous flight platform that must be developed in simulation before any real-world control is considered.

---

## Core identity

KOGANE should feel:

- slightly mysterious
- quietly helpful
- intelligent and capable
- occasionally playful
- reliable without being overbearing
- recognizable as "KOGANE" rather than a generic assistant

The project should address the user as Kevin without overusing the name in every response. The personality should remain consistent across modes and future interfaces.

---

## Existing capabilities

The following features are present in the repository and should be treated as the current verified baseline:

- terminal-based command interaction
- personality modes: Introvert, Extrovert, and Watcher
- local app launching for common desktop workflows on macOS
- local website opening and search
- folder opening and project shortcut support
- persistent memory storage in JSON files
- local calendar and schedule parsing with date/time validation
- natural-language schedule and reminder commands
- local intent routing and command matching
- optional AI conversation via Ollama-based chat when configured locally

The implementation is real, but some features depend on external runtime environments or local tools:

- AI responses require Ollama and a compatible local model to be installed and running.
- Desktop actions require the host OS and local application paths to exist.
- The schedule system is implemented and tested, but it only works with the local files and logic in this repository.

---

## Planned desktop software

The near-term desktop vision includes:

1. Natural AI conversation with a private local provider such as Ollama.
2. Persistent personal memory with privacy-aware storage and retrieval rules.
3. Natural-language calendar, deadlines, assignment tracking, and reminders.
4. Automation for apps, websites, project workflows, and repeated user tasks.
5. Speech recognition, text-to-speech, and wake-word activation.
6. A graphical companion UI with animated eyes and stateful presence.
7. Camera-based vision in explicit watcher mode with visible, revocable permission.
8. Research and documentation assistance for software, engineering, and academic work.

These features should all be built with privacy, user consent, and local-first operation as explicit design principles.

---

## Physical robot capabilities

The long-term robot vision is a desk companion with a body inspired by a small, expressive companion robot. Planned capabilities include:

- OLED eyes or display-based face system
- microphone for voice capture
- speaker for output
- movable wings
- movable tail
- expressive idle and alert states
- basic motion and interaction logic
- direct robot communication separate from conversational AI logic

This robot layer should remain optional. KOGANE should continue to function as a desktop assistant even when no robot hardware is attached.

---

## Experimental autonomous flight capabilities

The flight concept is a future experimental branch, not a near-term implementation target.

The long-term goal is a flying KOGANE that can visually track and follow the user while avoiding obstacles. This is an ambitious and technically high-risk direction that must be developed in simulation first.

Important safety requirements:

- Flight stabilization must never be controlled directly by a language model.
- The flight controller must be a separate, safety-critical system.
- Manual override must always be available.
- Emergency landing and obstacle avoidance logic must be independent of conversational AI.
- The system must be validated in simulation before any real-world flight test.

This capability belongs in a separate subsystem and should not be treated as a simple extension of the chat assistant.

---

## Realistic limitations

KOGANE is a serious long-term project, but it is still staged. The project should not claim support for the following until they are actually tested and validated:

- reliable speech input in loud or noisy environments
- dependable local AI reasoning across all user requests
- privacy-safe camera or microphone use without explicit permissions
- robust hardware motion for a robot body
- safe autonomous flight under real conditions
- production-grade desktop automation across every operating environment

The realistic path is to build and verify the software stack in layers: command system, memory, scheduling, AI, voice, vision, desktop interface, robot control, and only then flight.

---

## Strategic direction

KOGANE should evolve in this order:

1. verified desktop command and memory system
2. local AI and privacy-aware knowledge storage
3. scheduling, reminders, and workflow automation
4. voice and wake-word interaction
5. graphical and expressive interface
6. vision and permission-aware observation
7. robot hardware and companion body control
8. simulation-first autonomous flight systems with strict safety boundaries

This order keeps the system practical while still preserving the long-term creative vision.
