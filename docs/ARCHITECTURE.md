# KOGANE Architecture

## Overview

KOGANE is structured as a staged desktop companion system built around a central command loop and modular subsystems. The architecture separates:

- user interface and command routing
- personality behavior
- memory and schedule storage
- local automation skills
- AI provider integration
- future robot and flight systems

This separation is intentional. The assistant can operate as a desktop agent even when a robot body is not connected, and future robot control remains isolated from conversational AI logic.

---

## Actual current architecture

### 1. Entry point

The application begins in `main.py`.

Responsibilities:

- initialize the assistant state
- print startup status
- read user input
- route user text through `brain.intent.detect_intent()`
- dispatch actions for apps, websites, memory, schedule, and modes
- continue looping until the user exits

This is a command-driven architecture, not a full event bus or service framework.

### 2. Intent routing

`brain/intent.py` contains the command parser.

What it does:

- normalizes user input
- detects commands such as help, open app, schedule, memory, mode changes, and workflow shortcuts
- routes natural-language schedule commands before generic app/website matches
- returns an intent and payload to `main.py`

This layer is intentionally lightweight and deterministic. It is the main router for the current desktop assistant.

### 3. AI brain

`brain/ai_brain.py` handles general question answering using an Ollama-backed model.

Responsibilities:

- build memory context for the prompt
- apply mode-based system instructions
- send a user question to the configured local model
- clean the output and return a final answer

Important limitation: the AI layer is infrastructural and external-service dependent. It is not the robot control layer and should not directly manage movement, hardware, or safety-critical systems.

### 4. Personality system

`personality/modes.py` and `personality/responses.py` define the assistant persona.

Responsibilities:

- maintain the supported modes: Introvert, Extrovert, Watcher
- provide activation messages
- provide reusable greeting, farewell, and unknown-command responses

This keeps the persona separate from app logic and AI logic, which is important for future interface or robot expansion.

### 5. Memory subsystem

`memory/memory_store.py` stores user facts as JSON.

Responsibilities:

- load and save memory JSON
- normalize and deduplicate facts
- recall, delete, and clear saved facts

Current behavior is local and deterministic. The memory file is treated as user data and should not be overwritten by AI-generated content without explicit user intent.

### 6. Calendar and reminders

`memory/schedule_store.py` stores events and reminders in JSON.

Responsibilities:

- validate date/time values
- parse natural-language schedule commands
- normalize time phrases like `5pm`, `9:30am`, and `17:00`
- support schedule queries for today, tomorrow, and this week
- save and delete events safely
- protect the schedule file from silent corruption

This is one of the strongest existing subsystems and should be treated as the current source of truth for time-based planning.

### 7. Skills layer

The `skills/` package contains desktop automation helpers.

- `app_launcher.py` opens macOS apps by alias
- `folder_launcher.py` opens local folders
- `website_launcher.py` opens browser destinations and search URLs

These are simple, direct wrappers around OS and browser commands and are intentionally separate from the AI and persona layers.

### 8. Testing layer

`tests/` validates the routing and scheduling logic.

Current tests verify:

- intent detection and route selection
- schedule parsing and validation
- date resolution behavior
- safe handling of invalid or damaged schedule files

This is the project’s current verification baseline and should be used as the minimum correctness gate before making changes.

---

## Future modular interfaces

### AI providers

A provider interface should abstract the model backend so KOGANE can switch between:

- Ollama (local, private, preferred)
- OpenAI-compatible services (optional)
- other local LLM backends in the future

Proposed interface:

- `generate_response(prompt, context, mode)`
- `stream_response(...)` for future UI
- `health_check()` to verify the provider is available
- `system_instructions(mode)` to manage persona behavior

The AI layer should not be responsible for robot movement or hardware safety.

### Personality and conversation

A future personality layer should manage:

- mode logic
- voice tone
- response style
- user naming rules
- escalation or privacy-aware tone adjustment

This layer should consume structured context from memory, schedule, and app state instead of hard-coding text in multiple places.

### Memory

Memory should evolve into a multi-layer system:

- short-term conversation memory
- long-term personal facts
- privacy classification (public, personal, sensitive)
- explicit user control for recall, deletion, and export

The current JSON-based memory is a good baseline, but it should be treated as a local storage adapter rather than the final architecture.

### Calendar and reminders

Future reminders should support:

- recurring events
- reminder channels (terminal, GUI, TTS, notification)
- user-defined urgency levels
- timezone and locale awareness
- explicit consent before sending reminders or alerts

The schedule subsystem should stay deterministic and personal-data safe.

### Voice

Voice support should be isolated as a module with:

- speech recognition
- wake-word detection
- text-to-speech
- voice command validation
- permission gating for microphones

The voice subsystem should be designed to respect user permission and to fail safely if a microphone or speech model is unavailable.

### Vision

Camera handling should be segmented into:

- device acquisition and permission
- frame capture
- image preprocessing
- optional AI vision analysis
- user-visible explanation and logging
- explicit revocation of camera access

This should remain behind an opt-in permission model and never be silently active in the background.

### Desktop interface

A future graphical interface should separate:

- shell / text loop
- UI state representation
- rendering layer
- visual personality behavior
- events from the assistant core

This allows KOGANE to remain a terminal assistant while still supporting a richer desktop UI later.

### Automation skills

Automation should stay modular and declarative:

- app launchers
- filesystem actions
- browser automation
- project workflow commands
- permission-gated actions for sensitive desktops

Every automation command should be explicit, understandable, and safe by default.

### Robot communication

Robot control should be separated into a standalone communication layer:

- serial or network driver abstraction
- command validation
- low-level motion commands
- sensor feedback ingestion
- fail-safe monitoring

This layer must never be controlled by the general conversational AI without a dedicated validation path.

### Future flight simulation

A separate simulation-first flight subsystem should include:

- physics and environment simulation
- obstacle detection and avoidance
- user-tracking behavior
- emergency landing logic
- manual override and shutdown paths
- independent safety monitor

The flight subsystem must not share the same control path as the LLM or the user chat loop. It should be treated as a validated control architecture with its own review process.

---

## Design principles

1. Local-first when possible.
2. Privacy-aware memory and camera usage.
3. Deterministic storage for personal facts and schedules.
4. AI brain independent from robot hardware.
5. Safety before autonomous control.
6. Simulation before real hardware flight.
7. Small, verifiable improvements before major feature expansion.

---

## Recommended future system boundaries

The cleanest architecture is:

- `main.py` or desktop shell
- `brain/` for routing and AI question handling
- `personality/` for persona and response style
- `memory/` for durable personal data
- `skills/` for OS/browser/project automation
- `voice/` for audio input/output
- `vision/` for images and permission flows
- `robot/` for physical hardware drivers
- `flight/` for simulation and safety-critical control

This keeps KOGANE usable as a desktop assistant even if a robot body is not present, while preserving the path toward a physical and eventually flying companion.
