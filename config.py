#config (edit this):
#============================================
#general config:
version = "1.16.5"
#location of the mc server
server_dir = "/home/allen/smp3/"

#these defaults shouldn't need to be changed
log_file = server_dir + "/logs/latest.log"

#often server plugins will use "[PluginName] message" to log messages
#this results in false positives for the /say detection,
#since /say results in the output [player] message

#anything put in this list will not trigger the /say detection
blacklisted_users = ["Dynmap"] #"[Dynmap] something" will not trigger the /say detection

#--------------------------------------------

#discord webhook config
webhook = False #if this is False then the bot will be used instead
webhook_url = "https://discord.com/api/webhooks/xxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
discord_nickname = "Chatlink"

#--------------------------------------------

#discord bot config
bot_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
bot_channel_id = 776294866413682718 #channel id of the channel you want to link to the mc chat
command_prefix = "!" #command prefix for the bot

#messages from discord that are sent to the mc chat
#valid placholders: user, message, reply_user, reply_message
discord_to_mc_message = "§b[Discord]§r {user} » {message}" 
discord_reply_message = "§b[Discord]§r {user} (replying to {reply_user}) » {message}"
discord_ignore_bots = True #ignore bots in linked channel?

console_channel = True #enable/disable the console channel
console_channel_id = 947707312787841064 #channel id of the optional console channel

#set a custom status
#valid placeholders: motd, gametype, map, numplayers, maxplayers, hostport, hostip
#valid status types: playing, streaming, listening, watching, and competing
custom_status = True
custom_status_type = "playing"
custom_status_message = "with {numplayers}/{maxplayers} players" #will display as "playing with x/y players"


#rcon config
#you can find the port and password of the rcon server in server.properties
rcon_address = "127.0.0.1:25575"
rcon_password = "password"

#query config
#you can find the address and port in server.properties
use_query = False #use the query protocol, which is backwards compatible to beta 1.9, but must be explicitly enabled
#if this is false, then it will only work for versions 1.7 and up
query_address = "127.0.0.1:25565"

#ping config
server_address = "127.0.0.1:25565"

#--------------------------------------------

#commands config:
#these are the outputs of the commands that are run from discord

#help command:
#{pre} is a placeholder for the prefix
help_message = """
**Command List:**
 - `{pre}players` - Lists the online players
 - `{pre}stats` - Gets various stats about the server
 - `{pre}run [cmd]` - Run a command in the server (only available to users with access to the configured server console channel)
 - `!motd (address) (port)` - Displays a server MOTD as an image (only works on servers 1.7+).
 - `{pre}help` - Shows this message
"""

#player list commands
#valid placeholders: motd, gametype, map, numplayers, maxplayers, hostport, hostip
player_list_message = """
**{numplayers}/{maxplayers} players connected:**
{items}
"""
#valid placeholders: player
player_list_item = " - {player}"

#stats command
#valid placeholders: hostname, gametype, game_id, version, plugins,
#map, numplayers, maxplayers, hostport, hostip
stats_output_query = """
**Server Stats:**
Players: `{numplayers}/{maxplayers}`
Map name: `{map}`
Port: `{hostport}`
Version: `{version}`
MOTD:
```{hostname}```
"""

#run command
#valid placeholders: output
run_output = """
Command output:
```
{output}
```
"""

#motd command
#no placeholders
motd_output = """
**Server MOTD:**
"""
#name of the server
motd_title = "SMP Server"
bad_ip_output = "Invalid IP address!"

#--------------------------------------------

#messages config:
#these are the messages that are displayed in discord

#chat messages
#valid placeholders: player, chatmsg
player_message = "{player} » {chatmsg}"
slash_say_message = "[{player}] » {chatmsg}"

#player join/leave messages
#valid placeholders: player
player_join_message = "**{player} joined the game**"
player_leave_message = "**{player} left the game**"

#server start/stop messages
#valid placeholders: [none]
server_start_message = "**:white_check_mark: Server has started**"
server_stop_message = "**:octagonal_sign: Server has stopped**"

#advancement get messages
#valid placeholders: players
advancement_message = "**{player} has made the advancement [{advancement}]**"
goal_message = "**{player} has reached the goal [{advancement}]**"
challenge_message = "**{player} has completed the challenge [{advancement}]**"

#death messages
#valid placeholders: chatmsg
death_message = "{deathmsg}"

#===========================================
