## Chatlink - A Minecraft to Discord Integration Script Written in Python

### Features:
 - Theoretically compatible with any MC server (advancment messages will only work on 1.12 and above), no plugin required.
 - Completely seperate from the MC server.
 - Tracks when players join/leave, send chat messages, get achievements, and when they die.
 - Can detect when the server starts or stops.
 - Will only read messages from the server log.
 - Every message in the bot is configurable
 - Supports two way communication via the Minecraft RCON protocol.
 - Can retrieve server stats using the Minecraft query protocol. 
 - Has commands to get player count and misc stats.
 - Allows you to run server commands through Discord.
 - Has a customizable status that can display stats.

### Webhook Setup:
1. Cd into your server's directory and clone this repository.
2. Edit config.py and add a Discord webhook URL. Also, edit the MC version and the location of the MC server (needs to be an absolute path). Finally, make sure `webhook = True` is set in config.py.
3. Run `python3 main.py` to start the program.

### Bot Setup:
1. Cd into your server's directory and clone this repository.
2. Open server.properties and enable the RCON protocol and set a password. Also, enable the query protocol in the same file.
3. Edit config.py and put in your bot token and the ID of the channel to link to MC. Edit the MC version and the location of the MC server (needs to be and absolute path). 
4. In config.py, change the password for the RCON server to the one you set in step 2.
5. OPTIONAL: Link a channel to the server console by setting `console_channel` to True and setting the ID of the channel in config.py
6. Run `python3 main.py` to start the program.

###: Bash Script:
Use this script to start Chatlink and have it run in the background. Needs GNU Screen to be installed (`sudo apt install screen` on Debian systems). 
```
#!/bin/bash

#example path, this should be changed
cd /home/allen/smp3/chatlink
screen -dmS chatlink python3 main.py
```

### Command List:
Here, ! is used as the prefix, but this can be changed.
 - `!players` - Lists the online players
 - `!stats` - Gets various stats about the server
 - `!run [cmd]` - Run a command in the server (only available to users with access to the configured server console channel)
 - `!help` - Shows a help message

Note: This has only been tested on Linux.