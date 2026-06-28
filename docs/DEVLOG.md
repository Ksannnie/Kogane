# KOGANE Devlog

## Day 1 - Project Setup

Today I started Project KOGANE, a personal AI companion inspired by Kogane from Jujustu Kaisen.

### What I completed
- Installed Visual Studio Code
- Installed Python
- Created the KOGANE project folder 
- Created 'main.py' 
- Ran my first Python script successfully
- Set up the firt basic Kogane response
- Created the KOGANE GitHub repository
- Initialized Git locally
- Made the first commit
- Connected the local project to the GitHub remote repository
- Pushed the project to GitHub successfully

### First working output
'''text
Kogane: Awaiting your command.

### Milestone Completed
v0.1.0 - Initialization

## Day 2 - Text Command System Completed

Today I finished the main work for **v0.2.0 - Text Command System**.

KOGANE is now able to run as a terminal-based assistant that accepts typed commands, responds with personality, switches modes, lists available apps, and opens applications on macOS.

### Completed Today

* Improved the text command loop
* Added cleaner unknown command handling
* Added a greeting intent for commands like `hello`, `hi`, and `yo`
* Added an app list command
* Fixed the app launcher system
* Separated Roblox and Roblox Studio commands
* Fixed FL Studio by matching the correct macOS app name: `FL Studio 2025`
* Confirmed that major app-opening commands work
* Updated KOGANE's command system to feel more polished

### Commands Tested

```text
hello
help
apps
open
open chrome
open spotify
open roblox
open roblox studio
open fl
open fl studio
mode
modes
set mode introvert
set mode extrovert
set mode watcher
bye
```

### Working App Commands

```text
open chrome
open spotify
open roblox
open roblox studio
open fl
open fl studio
```

### Important Fixes

The app launcher was updated so that KOGANE can return both a success value and a message.

This fixed the earlier `ValueError` caused by `main.py` expecting two return values from `open_app()`.

KOGANE now uses app aliases so that different user commands can open the correct macOS application.

For example:

```text
roblox = Roblox
roblox studio = RobloxStudio
fl studio = FL Studio 2025
```

### What I Learned

* How to debug Python import errors
* How to fix return value mismatches
* How to separate similar commands like Roblox and Roblox Studio
* How macOS application names need to match exactly when using Python to open apps
* How command aliases make an assistant easier to use
* How to make unknown commands respond cleanly instead of feeling broken

### Milestone Completed

**v0.2.0 - Text Command System** is now complete.

### Next Milestone

The next milestone is:

**v0.3.0 - Memory**

The goal will be to let KOGANE save and load useful information instead of forgetting everything when the program closes.

## Day 3 - Memory System and Personality Layer

Today I started **v0.3.0 - Memory** and improved how KOGANE speaks.

The main goal for today was to make KOGANE feel less like a basic command-line program and more like the beginning of an actual AI companion.

### Completed Today

* Created the first memory system
* Added `memory/memory_store.py`
* Added `memory/__init__.py`
* Generated `memory/memory.json` for stored memories
* Added commands for saving and recalling memories
* Confirmed that KOGANE can remember information after restarting
* Added a new personality response file
* Created `personality/responses.py`
* Improved greeting responses
* Improved goodbye responses
* Added more playful KOGANE-style dialogue
* Added randomized responses so KOGANE does not say the same line every time
* Added a placeholder for future AI question answering

### Memory Commands Added

```text
remember that I am building KOGANE as my portfolio project
memory
recall
show memory
what do you remember
```

### Memory Test

I tested KOGANE by telling it:

```text
remember that I am building KOGANE as my portfolio project
```

KOGANE responded:

```text
I will remember that, Kevin.
```

Then after restarting the program, I typed:

```text
memory
```

KOGANE successfully recalled the saved memory.

### Personality Improvements

KOGANE originally sounded too serious when responding to greetings. For example, it said:

```text
I am present, Kevin. What do you require?
```

Today I started adjusting the personality so KOGANE feels more like a playful AI companion with a Kogane-inspired tone.

The new response system supports different types of dialogue, including:

* Greetings
* Farewells
* Empty input responses
* Unknown command responses
* Future question responses

### New File Added

```text
personality/responses.py
```

This file stores KOGANE's personality-based responses separately from `main.py`.

This makes the project cleaner because the main program controls behavior, while the personality file controls how KOGANE sounds.

### Question Answering Plan

KOGANE does not have a full AI brain connected yet, but today I added a placeholder response for questions.

The long-term goal is for KOGANE to eventually answer open-ended questions like an AI assistant, but in KOGANE's own tone and personality.

Future flow:

```text
Kevin asks a question
↓
KOGANE detects it as a general question
↓
AI brain generates an answer
↓
Personality layer makes it sound like KOGANE
↓
KOGANE responds
```

### What I Learned

* How to save data using JSON
* How persistent memory works
* How to load saved data after restarting a program
* Why private memory files should not be pushed to GitHub
* How to split personality responses into a separate Python file
* How random response selection can make an assistant feel more alive
* How KOGANE can eventually combine memory, AI answers, and personality

### Current Status

```text
v0.1.0 - Initialization complete
v0.2.0 - Text Command System complete
v0.3.0 - Memory in progress
```

### Next Goals

* Clean up memory formatting
* Add better memory recall commands
* Add a way to clear or delete memories
* Improve KOGANE's personality responses
* Begin planning the future AI brain system
