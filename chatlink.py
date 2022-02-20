import time
import os
import requests
import re
import deathmessages
import config

#compile regex patterns
def compile_regex():
    print("Fetching a list of death messages...")
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
    return death_messages_regex

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

def main(death_messages_regex):
    for line in tail(config.log_file, os.path.dirname(config.log_file)):
        line_stripped = re.sub(r"(\[[0-9][0-9]:[0-9][0-9]:[0-9][0-9]])", "", line, count=1).lstrip()
        if not "[Server thread/INFO]:" in line_stripped:
            continue
        line_formatted = line_stripped.replace("[Server thread/INFO]: ", "").replace("\n", "")
        if line_formatted == "":
            continue
        line_split = line_formatted.split(" ")

        text = ""
        #check for player message
        if re.match(r"^<[a-zA-Z0-9_]+> .+$", line_formatted):
            if line_formatted.startswith("<--[HERE]"):
                continue
            player = re.findall(r"<(.*?)>", line_formatted)[0]
            chatmsg = line_formatted.replace("<{player}> ".format(player=player), "", 1)
            text = config.player_message.format(player=player, chatmsg=chatmsg)
        #check for message sent by /say
        elif re.match(r"^\[[a-zA-Z0-9_]+\] .+$", line_formatted):
            findall = re.findall(r"\[(.*?)\]", line_formatted)
            if not len(findall) > 0:
                continue
            player = findall[0]
            if player == "Dynmap":
                continue
            elif " " in player:
                continue
            chatmsg = line_formatted.replace("[{player}] ".format(player=player), "", 1)
            text = config.slash_say_message.format(player=player, chatmsg=chatmsg)

        #check for player join/leave
        if re.match(r"^[a-zA-Z0-9_]+ left the game$", line_formatted):
                player = line_split[0]
                text = config.player_leave_message.format(player=player)
        elif re.match(r"^[a-zA-Z0-9_]+ joined the game$", line_formatted):
                player = line_split[0]
                text = config.player_join_message.format(player=player)

        #check for server start/stop
        if line_formatted.startswith("Done"):
            text = config.server_start_message
        elif line_formatted == "Stopping server":
            text = config.server_stop_message

        #check for advancements
        if re.match(r"^[a-zA-Z0-9_]+ has made the advancement \[.+\]$", line_formatted):
            line_split_re = re.split(r"\[(.*?)\]", line_formatted)
            player_string = line_split_re[0]
            player_string_split = player_string.split(" ", 1)
            advancement = line_split_re[1]
            text = config.advancement_message.format(player=player_string_split[0], advancement=advancement)
        elif re.match(r"^[a-zA-Z0-9_]+ has reached the goal \[.+\]$", line_formatted):
            line_split_re = re.split(r"\[(.*?)\]", line_formatted)
            player_string = line_split_re[0]
            player_string_split = player_string.split(" ", 1)
            advancement = line_split_re[1]
            text = config.goal_message.format(player=player_string_split[0], advancement=advancement)
        elif re.match(r"^[a-zA-Z0-9_]+ has completed the challenge \[.+\]$", line_formatted):
            line_split_re = re.split(r"\[(.*?)\]", line_formatted)
            player_string = line_split_re[0]
            player_string_split = player_string.split(" ", 1)
            advancement = line_split_re[1]
            text = config.challenge_message.format(player=player_string_split[0], advancement=advancement)

        #check for death messages
        for regex in death_messages_regex:
            if not regex.search(line_formatted) == None:
                text = config.death_message.format(deathmsg=line_formatted)
                
        if not text == "":
            print(text)
            data = {
                "content": text,
                "username": config.discord_nickname
            }
            r = requests.post(config.webhook_url, json=data)

if __name__ == "__main__":
    print("Compiling regex patterns...")
    regex_patterns = compile_regex()
    print("Starting the program...")
    main(regex_patterns)
