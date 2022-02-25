import discord
import asyncio
from discord.ext import commands
import threading
import os
import subprocess

import chatlink
import config
import rcon

class BotClient(discord.Client):
    def __init__(self, *args, **kwargs):
        self.chatlink_object = chatlink.Chatlink()
        super().__init__(*args, **kwargs)
        self.thread = threading.Thread(target=self.thread_function, daemon=True)
        self.loop = asyncio.get_event_loop()
        
        rcon_split = config.rcon_address.split(":")
        rcon_ip = rcon_split[0]
        rcon_port = int(rcon_split[1])
        self.rcon = rcon.RCON(rcon_ip, rcon_port, config.rcon_password)
        
    #thread to watch the log file
    def thread_function(self):
        channel = self.get_channel(config.bot_channel_id)
        print("Linked to channel #{channel} ({channelid})".format(channel=channel.name,
                                                                 channelid=channel.id))
        for text in self.chatlink_object.main():
            print("MC -> Discord: "+text)
            asyncio.run_coroutine_threadsafe(channel.send(text), self.loop)

    #runs when bot is initalized
    async def on_ready(self):
        print(f'Bot connected as {self.user}')
        self.thread.start()

    #checks for messages in the discord channel
    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        elif message.author.bot and config.discord_ignore_bots:
            return
        if message.channel.id == config.bot_channel_id:
            nickname = message.author.display_name
            message_escaped = message.content.replace('"', '\\"')
            message_escaped = message_escaped.replace("'", "\\'")
            message_formatted = config.discord_to_mc_message.format(message=message_escaped, user=nickname)
            command = 'tellraw @a "{msg}"'.format(msg=message_formatted)
            self.rcon.send_cmd(command)
            print("Discord -> MC: " + message_formatted)

if __name__ == "__main__":
    try:
        client = BotClient()
        print("Starting the bot...")
        client.run(config.bot_token)
    except KeyboardInterrupt:
        print("exiting")
