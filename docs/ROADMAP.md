# KOGANE Roadmap

## Current reality

KOGANE is a real project with a working desktop assistant foundation and a long-term robotics and AI roadmap.

The current state should be treated as follows:

- Verified and implemented: text command flow, personality modes, app/folder/website launching, JSON-based memory, schedule and reminder logic, intent routing, and schedule tests.
- Runtime-dependent and not guaranteed in every environment: AI conversation through Ollama, local user data access, and desktop automation behavior.
- Planned: voice, visual interface, camera vision, robot hardware, and autonomous flight.

---

## Status legend

- ✅ Verified in code and testable
- ⚠️ Implemented but runtime-dependent or not fully validated in this environment
- ⏳ Planned

---

## v0.1.0 - Initialization ✅

* [x] Set up VS Code
* [x] Set up Python
* [x] Create project structure
* [x] Create project documentation
* [x] Create GitHub repository
* [x] Initialize local git workflow

---

## v0.2.0 - Text Command System ✅

* [x] Add typed input loop
* [x] Add help and status commands
* [x] Add mode switching
* [x] Add greeting and farewell behavior
* [x] Add app launcher
* [x] Add app list command
* [x] Add folder launching
* [x] Add website launching and search
* [x] Add intent routing for desktop commands
* [x] Verify routing behavior through tests

---

## v0.3.0 - Memory ⚠️

* [x] Create local JSON memory storage
* [x] Add memory save and recall commands
* [x] Add delete and clear-memory actions
* [x] Prevent duplicate memory entries
* [x] Keep personal memory files outside the codebase-level project scope
* [ ] Add dedicated automated tests for all memory flows
* [ ] Add stricter privacy controls for loaded memory use

This subsystem is implemented and functions as a local personal data store, but it is not yet fully covered by a dedicated test file.

---

## v0.4.0 - AI Brain ⚠️

* [x] Create `brain/ai_brain.py`
* [x] Add question detection and routing
* [x] Pass memory context into the prompt
* [x] Apply mode-based personality instructions
* [x] Use a local Ollama-compatible LLM backend
* [ ] Add graceful fallback when the model or backend is unavailable
* [ ] Add explicit offline-safe behavior when AI is disabled

This is functional when Ollama and a compatible model are available, but it is not a fully offline guarantee and must be treated as runtime-dependent.

---

## v0.5.0 - Voice ⏳

* [ ] Add speech-to-text
* [ ] Add text-to-speech
* [ ] Add wake phrase activation
* [ ] Add explicit user permission flow for microphones
* [ ] Add voice-friendly responses and fallback behavior
* [ ] Verify reliability in quiet and noisy environments

---

## v0.6.0 - Desktop Assistant ✅ / ⚠️

### Verified desktop features

* [x] Open apps from natural language
* [x] Open websites from natural language
* [x] Search Google, YouTube, and GitHub
* [x] Open documents, folders, and project directories
* [x] Add focused help menus
* [x] Add schedule and reminder parsing
* [x] Add date and weekday resolution logic
* [x] Add schedule listing and deletion by displayed event number
* [x] Add defensive handling for invalid or damaged schedule files
* [x] Verify command routing and schedule behavior with automated tests

### Remaining work for this phase

* [ ] Add website help content for all routes
* [ ] Add project-specific shortcuts
* [ ] Add `open kogane repo`
* [ ] Add `open canvas assignments`
* [ ] Add `open odu email`
* [ ] Improve error messages for failed launches
* [ ] Clean up remaining routing edge cases

---

## v0.7.0 - Vision ⏳

* [ ] Add camera input with explicit permission flow
* [ ] Describe what KOGANE sees
* [ ] Support Watcher Mode comments without constant interruption
* [ ] Add privacy and revocation rules
* [ ] Validate image recognition under real conditions

---

## v0.8.0 - Interface ⏳

* [ ] Add a simple graphical interface
* [ ] Display current mode
* [ ] Display command history
* [ ] Display KOGANE status
* [ ] Display saved memories or memory status
* [ ] Add basic visual personality elements

---

## v0.9.0 - Physical Prototype ⏳

* [ ] Sketch robot body concept
* [ ] Define size and materials
* [ ] Prototype OLED eyes
* [ ] Prototype wing movement
* [ ] Prototype tail movement
* [ ] Add speaker and microphone hardware
* [ ] Design a 3D-printable shell
* [ ] Build the first desk companion prototype

---

## v1.0.0 - Stable Desktop Assistant ⏳

### Acceptance criteria

A stable desktop V1 should be considered ready only when all of the following are true:

* [ ] The assistant can run reliably from a local Python environment without crashing during normal use
* [ ] The command system remains stable and predictable across help, app, folder, website, memory, and schedule commands
* [ ] The project includes automated tests covering routing and critical schedule logic
* [ ] Local personal memory and calendar data are stored safely and are never overwritten by AI responses
* [ ] The user can explicitly enable or disable AI features, voice features, scheduling features, and camera features
* [ ] The documentation explains supported features, limits, and privacy boundaries
* [ ] The project is stable enough to demonstrate to a user without broken workflows

### Required work before V1

* [ ] Full routing cleanup and known-edge-case review
* [ ] Offline-safe behavior when AI services are unavailable
* [ ] Clear user-facing error handling for failed desktop automation
* [ ] Memory and schedule operations with privacy-safe defaults
* [ ] Documentation reviewed against actual verified behavior

---

## Long-term vision

KOGANE should evolve toward a personalized AI companion that can:

* respond to typed and spoken commands
* answer open-ended questions using a private local AI backend
* remember useful information safely and deterministically
* open apps, websites, and workflows on the user's desktop
* manage schedule, reminders, and due dates naturally
* work as a desktop assistant even without robot hardware
* eventually operate as a robot companion with expressive motion and speech
* eventually support a flight-capable simulation-first platform with clear safety boundaries

### Flight development rule

Future autonomous flight is a separate and highly constrained subsystem.

- It must be developed in simulation first.
- It must not be directly controlled by a language model.
- It must include a dedicated flight controller, independent fail-safes, manual override, and emergency landing logic.
- It must not be treated as part of the conversational AI layer.

---