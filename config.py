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
bot_token = "Nzc2Mjk3MDExNDEwMTA4NDQ3.X6y07g.Db_0WYkska90SWptuUB2RWr8eWA" 
bot_channel_id = 776294866413682718 #channel id of the channel you want to link to the mc chat
discord_to_mc_message = "[§bDiscord§r] [{user}] {message}"
discord_ignore_bots = True

#rcon config
#you can find the port and password of the rcon server in server.properties
rcon_address = "127.0.0.1:25575"
rcon_password = "password"

#--------------------------------------------

#messages config:
#these placeholders cannot be removed or else there will be an error

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
