#config (edit this):
#============================================
#general config:
version = "1.16.5"
#location of the mc server
server_dir = "/home/allen/smp3/"

#these defaults shouldn't need to be changed
log_file = server_dir + "/logs/latest.log"

#--------------------------------------------

#discord webhook config
webhook = False #if this is False then the bot will be used instead
webhook_url = "https://discord.com/api/webhooks/xxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
discord_nickname = "Chatlink"

#--------------------------------------------

#discord bot config
bot_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
bot_channel_id = 776294866413682718 #channel id of the channel you want to link to the mc chat
discord_to_mc_message = "§b[Discord]§r {user} » {message}" #message from discord that is sent to the mc chat
discord_ignore_bots = True #ignore bots in linked channel?
command_prefix = "!" #command prefix for the bot
console_channel = False #enable/disable the console channel
console_channel_id = 947707312787841064 #channel id of the optional console channel

#rcon config
#you can find the port and password of the rcon server in server.properties
rcon_address = "127.0.0.1:25575"
rcon_password = "password"

#query config
#again, you can find the address and port in server.properties
query_address = "127.0.0.1:25565"

#--------------------------------------------

#commands config:
#these are the outputs of the commands that are run from discord

#help command:
help_message = """
**Command List:**
 - `{pre}players` - Lists the online players
 - `{pre}stats` - Gets various stats about the server
 - `{pre}run [cmd]` - Run a command in the server (only available to users with access to the configured server console channel)
 - `{pre}help` - Shows this message
""".lstrip().strip().format(pre=command_prefix)

#player list commands
player_list_heading = "**{players}/{maxplayers} players connected:**"
player_list_items = " - {player}"

#stats command
stats_output = """
**Server Stats:**
Players: `{players}/{maxplayers}`
Map name: `{mapname}`
Port: `{server_port}`
MOTD:
```{motd}```
""".lstrip().strip()

#run command
run_output = """
Command output:
```
{output}
```
""".lstrip().strip()

#--------------------------------------------

#messages config:
#these are the messages that are displayed in discord

#chat messages
player_message = "{player} » {chatmsg}"
slash_say_message = "[{player}] » {chatmsg}"

#player join/leave messages
player_join_message = "**{player} joined the game**"
player_leave_message = "**{player} left the game**"

#server start/stop messages
server_start_message = "**:white_check_mark: Server has started**"
server_stop_message = "**:octagonal_sign: Server has stopped**"

#advancement get messages
advancement_message = "**{player} has made the advancement [{advancement}]**"
goal_message = "**{player} has reached the goal [{advancement}]**"
challenge_message = "**{player} has completed the challenge [{advancement}]**"

#death messages
death_message = "{deathmsg}"

#===========================================
