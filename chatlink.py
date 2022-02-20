import time
import os
import requests
import re
import deathmessages

#config (edit this):
#--------------------------------------------
#discord webhook config
webhook_url = ""
discord_nickname = "Chatlink"

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
#--------------------------------------------
#end config

#compile regex patterns
death_messages = deathmessages.get_death_messages()
death_messages_regex = []
placeholder1 = re.escape("%1$s")
placeholder2 = re.escape("%2$s")
placeholder3 = re.escape("%3$s")
for death_msg in death_messages:
    death_message_escaped = re.escape(death_msg)
    death_message_escaped = death_message_escaped.replace(placeholder1, "[a-zA-Z0-9_]+")
    death_message_escaped = death_message_escaped.replace(placeholder2, ".+").replace(placeholder3, ".+")
    death_messages_regex.append(re.compile("^"+death_message_escaped+"$"))

stop = False
#detects changes in the log file and returns them
def tail(filename, logdir):
    f = open(filename, "r")
    while not f.readline() == "":
        pass

    all_files = os.listdir(logdir)
    while stop == False:
        all_files_old = all_files[:]
        all_files = os.listdir(logdir)
        if len(all_files) > len(all_files_old):
            #reopen the log file if the server restarts
            print("server start detected")
            f.close()
            f = open(filename, "r")
            
        newline = f.readline()
        if newline == "":
            try:
                time.sleep(0.5)
            except KeyboardInterrupt:
                print("quitting...")
                break
            continue

        yield newline
    f.close()

def main():
    for line in tail("logs/latest.log", "logs"):
        line_stripped = re.sub(r"(\[[0-9][0-9]:[0-9][0-9]:[0-9][0-9]])", "", line, count=1).lstrip()
        if not "[Server thread/INFO]:" in line_stripped:
            continue
        line_formatted = line_stripped.replace("[Server thread/INFO]: ", "").replace("\n", "")
        if line_formatted == "":
            continue
        line_split = line_formatted.split(" ")

        text = ""
        #check for player message
        if line_formatted.startswith("<"):
            if line_formatted.startswith("<--[HERE]"):
                continue
            player = re.findall(r"<(.*?)>", line_formatted)[0]
            chatmsg = line_formatted.replace("<{player}> ".format(player=player), "", 1)
            text = player_message.format(player=player, chatmsg=chatmsg)
        #check for message sent by /say
        elif line_formatted.startswith("["):
            findall = re.findall(r"\[(.*?)\]", line_formatted)
            if not len(findall) > 0:
                continue
            player = findall[0]
            if player == "Dynmap":
                continue
            elif " " in player:
                continue
            chatmsg = line_formatted.replace("[{player}] ".format(player=player), "", 1)
            text = slash_say_message.format(player=player, chatmsg=chatmsg)

        #check for player join/leave
        if " ".join(line_split[1:]) == "left the game":
                player = line_split[0]
                text = player_leave_message.format(player=player)
        elif " ".join(line_split[1:]) == "joined the game":
                player = line_split[0]
                text = player_join_message.format(player=player)

        #check for server start/stop
        if line_formatted.startswith("Done"):
            text = server_start_message
        elif line_formatted == "Stopping server":
            text = server_stop_message

        #check for advancements
        if "has made the advancement" in line_formatted:
            line_split_re = re.split(r"\[(.*?)\]", line_formatted)
            player_string = line_split_re[0]
            player_string_split = player_string.split(" ", 1)
            if not player_string_split[1].strip() == "has made the advancement":
                continue
            advancement = line_split_re[1]
            text = advancement_message.format(player=player_string_split[0], advancement=advancement)
        elif "has reached the goal" in line_formatted:
            line_split_re = re.split(r"\[(.*?)\]", line_formatted)
            player_string = line_split_re[0]
            player_string_split = player_string.split(" ", 1)
            if not player_string_split[1].strip() == "has reached the goal":
                continue
            advancement = line_split_re[1]
            text = goal_message.format(player=player_string_split[0], advancement=advancement)
        elif "has completed the challenge" in line_formatted:
            line_split_re = re.split(r"\[(.*?)\]", line_formatted)
            player_string = line_split_re[0]
            player_string_split = player_string.split(" ", 1)
            if not player_string_split[1].strip() == "has completed the challenge":
                continue
            advancement = line_split_re[1]
            text = challenge_message.format(player=player_string_split[0], advancement=advancement)

        #check for death messages
        for regex in death_messages_regex:
            if not regex.search(line_formatted) == None:
                text = death_message.format(deathmsg=line_formatted)
                
        if not text == "":
            print(text)
            data = {
                "content": text,
                "username": discord_nickname
            }
            r = requests.post(webhook_url, json=data)

if __name__ == "__main__":
    main()
