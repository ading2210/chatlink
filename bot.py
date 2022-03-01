import discord
import asyncio
import threading
import os
import struct
import time

import chatlink
import config
from discord.ext import commands, tasks
from utils import rcon, query

class BotClient(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.chatlink_object = chatlink.Chatlink()
        super().__init__(*args, **kwargs)
        self.thread = threading.Thread(target=self.thread_function, daemon=True)
        self.loop = asyncio.get_event_loop()

        query_address_str = config.query_address.split(":")[0]
        query_port = int(config.query_address.split(":")[1])
        self.query_address = (query_address_str, query_port)
        self.query = query.Query(self.query_address)

        rcon_split = config.rcon_address.split(":")
        rcon_ip = rcon_split[0]
        rcon_port = int(rcon_split[1])
        self.rcon = rcon.RCON(rcon_ip, rcon_port, config.rcon_password)

        if config.custom_status == True:
            print("Custom Discord status is enabled.")
            self.status_thread_function.start()

    @discord.ext.tasks.loop(seconds=30)
    async def status_thread_function(self):
        stats = self.query.basic_stat()
        new_status_message = config.custom_status_message.format(**stats)
        if not new_status_message == self.status_message:
            await self.change_presence(activity=discord.Game(new_status_message))
        self.status_message = new_status_message
        
    @status_thread_function.before_loop
    async def wait_for_ready(self):
        await self.wait_until_ready()
        self.status_message = ""
        
    #thread to watch the log file
    def thread_function(self):
        channel = self.get_channel(config.bot_channel_id)
        print("Chat linked to channel #{channel} ({channelid})".format(channel=channel.name,
                                                                 channelid=channel.id))
        for text in self.chatlink_object.main():
            print("MC -> Discord: "+text)
            asyncio.run_coroutine_threadsafe(channel.send(text), self.loop)

    #runs when bot is initalized
    async def on_ready(self):
        print(f'Bot connected as {self.user}')
        self.thread.start()

        if config.console_channel == True:
            console_channel = self.get_channel(config.console_channel_id)
            print("Console linked to channel #{channel} ({channelid})"
                  .format(channel=console_channel.name, channelid=console_channel.id))
        
    #checks for messages in the discord channel
    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        elif message.author.bot and config.discord_ignore_bots:
            return
        await self.process_commands(message)

        if message.content.startswith(config.command_prefix):
            return
        if message.channel.id == config.bot_channel_id:
            nickname = message.author.display_name
            message_formatted = config.discord_to_mc_message.format(message=message.content, user=nickname).replace("'", r"\'").replace('"', r'\"')
            command = 'tellraw @a "{msg}"'.format(msg=message_formatted)
            try:
                self.rcon.send_cmd(command)
            except (BrokenPipeError, struct.error) as e:
                #error handling in case the server restarts
                print("Attempting to reconnect to the RCON server...")
                try:
                    self.rcon.reconnect()
                    self.rcon.send_cmd(command)
                    print("Reconnection successful!")
                except ConnectionRefusedError:
                    print("Connection has been refused. Either the server is still starting or RCON is not enabled.")
            print("Discord -> MC: " + message_formatted)
            
