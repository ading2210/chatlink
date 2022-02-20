## Chatlink - A Minecraft to Discord Integration Script Written in Python

### Features:
 - Theoretically compatible with any MC server software (1.12 and above), no plugin required.
 - Completely seperate from the MC server.
 - Tracks when players join/leave, send chat messages, get achievements, and when they die.
 - Can detect when the server starts or stops.
 - Will only read info from the server log.

### Setup:
(Note: This has only been tested on Linux)
1. Cd into your server's directory and clone this repository.
2. Edit chatlink.py and add a Discord webhook URL.
3. Edit deathmessages.py and change the MC version to whatever version of MC your server is running.
4. Run `python3 chatlink.py` to start the program
