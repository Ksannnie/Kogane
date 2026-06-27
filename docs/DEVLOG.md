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
