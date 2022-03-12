import discord
import asyncio
import threading
import os
import struct
import time

import chatlink
import config
from discord.ext import commands, tasks
from utils import rcon, query, ping

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
        rcon_address = rcon_split[0]
        rcon_port = int(rcon_split[1])
        self.rcon = rcon.RCON(rcon_address, rcon_port, config.rcon_password)

        server_address_split = config.server_address.split(":")
        server_port = int(server_address_split[1])
        self.server_address = (server_address_split[0], server_port)

        if config.custom_status == True:
            print("Custom Discord status is enabled.")
            self.status_thread_function.start()

    @discord.ext.tasks.loop(seconds=30)
    async def status_thread_function(self):
        if config.use_query == True:
            stats = self.query.full_stat()
            stats["protocol_version"] = "Unknown"
        else:
            pinger = ping.Pinger(self.server_address)
            stats = pinger.ping_converted()
        new_status_message = config.custom_status_message.format(**stats)
        if not new_status_message == self.status_message:
            activities = {
                "playing": discord.Game(new_status_message),
                "streaming": discord.Activity(type=discord.ActivityType.streaming, name=new_status_message),
                "listening": discord.Activity(type=discord.ActivityType.listening, name=new_status_message),
                "watching": discord.Activity(type=discord.ActivityType.watching, name=new_status_message),
                "competing": discord.Activity(type=discord.ActivityType.competing, name=new_status_message)
            }
            activity = activities[config.custom_status_type]
            await self.change_presence(activity=activity)
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
            placeholders = {
                "user": message.author.display_name,
                "message": message.content,
                "reply_user": None,
                "reply_message": None
            }
            
            if not message.reference == None:
                reply = message.reference.resolved
                reply_member = await message.guild.fetch_member(reply.author.id)
                placeholders["reply_user"] = reply_member.display_name
                placeholders["reply_message"] = reply.content
                message_formatted = config.discord_reply_message.format(**placeholders).replace("'", r"\'").replace('"', r'\"')
            else:
                message_formatted = config.discord_to_mc_message.format(**placeholders).replace("'", r"\'").replace('"', r'\"')
                
            command = 'tellraw @a "{msg}"'.format(msg=message_formatted)
            try:
                self.rcon.send_cmd(command)
            except (BrokenPipeError, ConnectionRefusedError, struct.error) as e:
                #error handling in case the server restarts
                print("Attempting to reconnect to the RCON server...")
                try:
                    self.rcon.reconnect()
                    self.rcon.send_cmd(command)
                    print("Reconnection successful!")
                except ConnectionRefusedError:
                    print("Connection has been refused. Either the server is still starting or RCON is not enabled.")
            print("Discord -> MC: " + message_formatted)
            
