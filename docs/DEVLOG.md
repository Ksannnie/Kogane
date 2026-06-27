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

## Day 2 - Text Command System Started

Today I continued building KOGANE past the initial setup stage and started turning it into an actual command-based assistant.
Main Progress

KOGANE now has the beginning of a modular software structure instead of everything being stored inside one file.

New Folders and Files Added
brain/
├── __init__.py
└── intent.py

personality/
├── __init__.py
└── modes.py

skills/
├── __init__.py
└── app_launcher.py
What Each File Does

brain/intent.py
Handles command detection. This file helps KOGANE understand what the user is trying to do, such as asking for help, checking status, changing modes, or opening an app.

personality/modes.py
Stores KOGANE's personality modes. The current modes include introvert, extrovert, and watcher.

skills/app_launcher.py
Handles opening applications on macOS. This gives KOGANE the ability to launch apps based on typed commands.

main.py
Acts as the main control center. It starts KOGANE, takes user input, sends commands to the intent system, and runs the correct response or skill.

Commands Added / Tested
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
App Launcher Progress

KOGANE can now recognize app-opening commands such as:

open chrome

and respond with:

Kogane: Opening Google Chrome.

This is the first real “skill” added to the project.

Current Milestone

v0.2.0 - Text Command System is now in progress.

Next Goals
Clean up the command system
Add better responses for unknown commands
Improve mode switching
Add more app shortcuts
Commit and push the updated text command system to GitHub