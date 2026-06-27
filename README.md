# KOGANE

KOGANE is an AI-assisted personal companion project built in Python.

The project is inspired by the idea of a small intelligent companion that can respond to commands, switch personality modes, launch applications, and eventually grow into a voice-enabled and vision-capable desktop assistant.

This repository is being developed as a long-term learning and portfolio project focused on Python, software architecture, AI tools, automation, and eventually robotics.

---

## Current Version

**v0.2.0 - Text Command System In Progress**

---

## Current Features

* Modular Python project structure
* Terminal-based command interaction
* Basic intent detection system
* Personality modes
* App launcher skill for macOS
* GitHub version control
* Development documentation

---

## Current Commands

```text
help
status
mode
modes
set mode introvert
set mode extrovert
set mode watcher
open chrome
open spotify
open vscode
open fl studio
open roblox
bye
```

---

## Project Structure

```text
KOGANE/
├── assets/
├── automation/
├── brain/
│   ├── __init__.py
│   └── intent.py
├── docs/
│   ├── DESIGN.md
│   ├── DEVLOG.md
│   └── ROADMAP.md
├── memory/
├── personality/
│   ├── __init__.py
│   └── modes.py
├── skills/
│   ├── __init__.py
│   └── app_launcher.py
├── voice/
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

---

## Development Note

This project is being built with AI-assisted coding support.

I am using AI as a learning tool to help plan, write, understand, debug, and improve the code while I actively test the program, organize the repository, document progress, and make design decisions.

The purpose of this project is not just to create an assistant, but to progressively learn software development, Python project structure, GitHub workflow, and AI-powered development.

---

## Roadmap

* [x] Project setup
* [x] GitHub repository setup
* [x] Basic Python startup script
* [x] Modular folder structure
* [x] Text command loop
* [x] Personality modes
* [x] App launcher skill
* [ ] Better unknown-command handling
* [ ] More app shortcuts
* [ ] Long-term memory
* [ ] Voice input
* [ ] Text-to-speech output
* [ ] Camera vision
* [ ] Physical companion prototype

---

## Long-Term Goal

The long-term goal is to turn KOGANE into a personalized AI companion that can:

* Talk with the user
* Remember useful information
* Switch between behavior modes
* Open apps and assist with workflows
* Use voice input and speech output
* Use camera vision in Watcher Mode
* Eventually connect to a physical robotic body

---

## Status

KOGANE is currently in early development. The current focus is building a clean text-based command system before adding memory, voice, vision, and hardware features.
