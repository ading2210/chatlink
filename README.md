## Chatlink - A Minecraft to Discord Integration Script Written in Python

### Features:
 - Theoretically compatible with any MC server software (1.12 and above), no plugin required.
 - Completely seperate from the MC server.
 - Tracks when players join/leave, send chat messages, get achievements, and when they die.
 - Can detect when the server starts or stops.
 - Will only read info from the server log.
 - Supports two way communication via the Minecraft RCON protocol.

### Webhook Setup:
1. Cd into your server's directory and clone this repository.
2. Edit config.py and add a Discord webhook URL. Also edit the MC version and the location of the MC server (needs to be an absolute path). Finally make sure `webhook = True` is set in config.py.
4. Run `python3 main.py` to start the program.

### Bot Setup:
1. Cd into your server's directory and clone this repository.
2. Open server.properties and enable the RCON protocol and set a password.
3. Edit config.py and put in your bot token and the id of the channel to link to MC. Also edit the MC version and the location of the MC server (needs to be absolute). Finally change the password for the RCON server to the one you set in step 2.
4. Run `python3 main.py` to start the program.

Note: This has only been tested on Linux