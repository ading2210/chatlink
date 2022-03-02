from utils import query, rcon
import discord
from discord.ext import commands
import config
import textwrap

class Commands(commands.Cog, name="commands module"):
    def __init__(self, client):
        self.client = client

    #command to list players
    @commands.command(name="players")
    async def players(self, ctx):
        stats = self.client.query.full_stat()
        players = stats.pop("players")
        players_list = []
        for player in players:
            players_list.append(config.player_list_item.format(player=player))
        message = config.player_list_message.format(items="\n".join(players_list), **stats)
        await ctx.send(message)

    #command to get some misc server stats
    @commands.command(name="stats")
    async def stats(self, ctx):
        stats = self.client.query.full_stat()
        players = stats.pop("players")
        response = config.stats_output.format(**stats).lstrip().strip()
        await ctx.send(response)

    #command to run a command in mc
    @commands.command(name="run")
    async def run_cmd(self, ctx):
        if config.console_channel == False:
            return
        if not ctx.channel.id == config.console_channel_id:
            return
        
        cmd = ctx.message.content.replace(ctx.prefix + "run", "", 1).lstrip()
        try:
            response = self.client.rcon.send_cmd(cmd)
        except (BrokenPipeError, ConnectionRefusedError) as e:
            #error handling in case the server restarts
            print("Attempting to reconnect to the RCON server...")
            try:
                self.client.rcon.reconnect()
                response = self.client.rcon.send_cmd(cmd)
                print("Reconnection successful!")
            except ConnectionRefusedError:
                response = "Error: The connection to the RCON server was refused. Either the server is offline/starting or rcon is not enabled."

        if response == "":
            response = "The command was executed successfully but the response from the server was empty."
        max_length = 2000-len(config.run_output.lstrip().strip())
        msg = config.run_output.format(output=textwrap.shorten(response, width=max_length)) 
        
        await ctx.send(msg)

    @commands.command(name="help")
    async def help(self, ctx):
        await ctx.send(config.help_message.format(pre=command_prefix).lstrip().strip())
