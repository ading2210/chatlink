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
2. Edit config.py and add a Discord webhook URL. Also edit the MC version and edit the location of the MC server's log file (needs to be an absolute path).
4. Run `python3 chatlink.py` to start the program.
