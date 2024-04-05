#config (edit this):
#============================================
#general config:
version = "1.19.4"
#location of the mc server
server_dir = "/home/allen/smp/"

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
bot_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
bot_channel_id = 99999999999999999 #channel id of the channel you want to link to the mc chat
command_prefix = "!" #command prefix for the bot

#messages from discord that are sent to the mc chat
#valid placholders: user, message, reply_user, reply_message
discord_to_mc_message = "§b[Discord]§r {user} » {message}" 
discord_reply_message = "§b[Discord]§r {user} (replying to {reply_user}) » {message}"
discord_ignore_bots = True #ignore bots in linked channel?

console_channel = False #enable/disable the console channel
console_channel_id = 99999999999999999 #channel id of the optional console channel

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
use_query = True #use the query protocol, which is backwards compatible to beta 1.9, but must be explicitly enabled
#if this is false, then it will only work for versions 1.7 and up
#it is reccomended to set this to true
query_address = "127.0.0.1:25565"

#ping config
server_address = "127.0.0.1:25565"

#error messages
timeout_message = "```Error: Request timed out. Is the MC server running?.```"
connection_refused_message = "```Error: Connection refused. Is the MC server running?.```"

#--------------------------------------------

#commands config:
#these are the outputs of the commands that are run from discord

#help command:
#{pre} is a placeholder for the prefix
help_use_embed = True #use embeds?

#message to send if embeds are disabled
help_message = """**Command List:**
- `{pre}players` - Lists the online players
- `{pre}stats` - Gets various stats about the server
- `{pre}run [cmd]` - Run a command in the server console
- `!motd (address) (port)` - Displays a server MOTD as an image.
- `{pre}help` - Shows this message

Source code: <https://github.com/ading2210/chatlink>
""".format(pre=command_prefix)

#will only be used for the embed
command_list = """
- `{pre}players` - Lists the online players
- `{pre}stats` - Gets various stats about the server
- `{pre}run [cmd]` - Run a command in the server console
- `!motd (address) (port)` - Displays a server MOTD as an image.
- `{pre}help` - Shows this message
""".format(pre=command_prefix)

#the embed to send, if enabled
help_output_embed = {
    "title": "**Command List:**",
    "footer": "Source code: github.com/ading2210/chatlink",
    "color": 0x3CB371,
    "description": command_list
}
thumbnail_in_help = True

#--------------------------------------------

#player list commands
#valid placeholders: hostname, gametype, game_id, version, plugins,
#map, numplayers, maxplayers, hostport, hostip
player_list_use_embed = True #use embeds?

#the message to send if embeds are disabled
player_list_message = """
**{numplayers}/{maxplayers} players connected:**
{items}
"""
#valid placeholders: player
player_list_item = "- {player}"

#the embed to send, if enabled
player_list_embed = {
    "title": "**{numplayers}/{maxplayers} Players Connected:**",
    "footer": None,
    "color": 0x3CB371,
    "fields": [
        {
            "name": "Players:",
            "value": "{items}",
            "inline": False
         },
    ]
}
thumbnail_in_player_list = True

#--------------------------------------------

#stats command
#valid placeholders: hostname, gametype, game_id, version, plugins,
#map, numplayers, maxplayers, hostport, hostip
stats_use_embed = True #use embeds?

#will only be used if the embed is disabled
stats_output_query = """
**Server Stats:**
Players: `{numplayers}/{maxplayers}`
Map name: `{map}`
Port: `{hostport}`
Version: `{version}`
MOTD:
```{hostname}```
"""
#the embed to send, if enabled
stats_output_embed = {
    "title": "**Server Stats:**",
    "footer": "Server IP: example.com:{hostport}",
    "color": 0x3CB371,
    "fields": [
        {
            "name": "Players:",
            "value": "`{numplayers}/{maxplayers}`",
            "inline": True
         },
        {
            "name": "Map Name:",
            "value": "`{map}`",
            "inline": True
        },
        {
            "name": "Version",
            "value": "`{version}`",
            "inline": True
        }
    ]
}
motd_image_in_stats = True
thumbnail_in_stats = True #will only work if the embed is enabled

#--------------------------------------------

#run command
#valid placeholders: output
run_output = """
Command output:
```
{output}
```
"""

#--------------------------------------------

#motd command
#no placeholders
motd_use_embed = True #use embeds?
#the message to send if embeds are disabled
motd_message = """
**Server MOTD:**
"""
#the embed to send, if enabled
motd_embed = {
    "title": "**Server MOTD:**",
    "footer": None,
    "color": 0x3CB371
}
#the message to send while the desired server is being pinged
motd_pinging_message = "Pinging the server..."

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
