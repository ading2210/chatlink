from utils import query, rcon, motd_renderer, ping
import discord
from discord.ext import commands
import config
import textwrap
import struct
import socket
from io import BytesIO

def embed_builder(embed_dict, placeholders):
    for item in embed_dict:
        if type(embed_dict[item]) is str:
            embed_dict[item] = embed_dict[item].format(**placeholders)
    embed = discord.Embed(**embed_dict)
    if "fields" in embed_dict:
        for field in embed_dict["fields"]:
            field["value"] = field["value"].format(**placeholders)
            embed.add_field(**field)
    if not embed_dict["footer"] == None:
        embed.set_footer(text=embed_dict["footer"])
    return embed
        
class Commands(commands.Cog, name="commands module"):
    def __init__(self, client):
        self.client = client

    def get_stats(self):
        if config.use_query == True:
            stats = self.client.query.full_stat()
            players = stats.pop("players")
            stats["protocol_version"] = "Unknown"
        else:
            stats = self.client.pinger.ping_converted()
            players = stats.pop("players")
            
        if len(players) == 0 or players[0] == "":
            players = []
        return stats, players

    #command to list players
    @commands.command(name="players")
    async def players(self, ctx):
        try:
            stats, players = self.get_stats()
        except socket.timeout:
            await ctx.send(config.timeout_message)
            return
        except ConnectionRefusedError:
            await ctx.send(config.connection_refused_message)
            return
        
        players_list = []
        for player in players:
            players_list.append(config.player_list_item.format(player=player))
        if len(players) > 0:
            stats["items"] = items="\n".join(players_list)
        else:
            stats["items"] = chr(173)
            
        message = {}
        if config.player_list_use_embed:
            embed = embed_builder(config.player_list_embed, stats)
            message["embed"] = embed
        else:
            response = config.player_list_message.format(**stats)
            message["content"] = response

        if config.thumbnail_in_player_list and config.player_list_use_embed:
            message["files"] = []
            renderer = motd_renderer.MOTDRenderer()
            ip, port = config.server_address.split(":")
            thumbnail = renderer.get_thumbnail(address=(ip, int(port)))
            with BytesIO() as thumbnail_output:
                thumbnail.save(thumbnail_output, format="PNG")
                thumbnail_output.seek(0)
                file = discord.File(fp=thumbnail_output, filename="thumbnail.png")
                if config.player_list_use_embed:
                    message["embed"].set_thumbnail(url="attachment://thumbnail.png")
                message["files"].append(file)
            
        await ctx.send(**message)

    #command to get some misc server stats
    @commands.command(name="stats")
    async def stats(self, ctx):
        try:
            stats, players = self.get_stats()
        except socket.timeout:
            await ctx.send(config.timeout_message)
            return
        except ConnectionRefusedError:
            await ctx.send(config.connection_refused_message)
            return
        message = {}
        if config.stats_use_embed:
            embed = embed_builder(config.stats_output_embed, stats)
            message["embed"] = embed
        else:
            response = config.stats_output_query.format(**stats).lstrip().strip()
            message["content"] = response

        renderer = motd_renderer.MOTDRenderer()
        ip, port = config.server_address.split(":")
        message["files"] = []
        if config.motd_image_in_stats:
            image = renderer.get_full_image(title=config.motd_title, address=(ip, int(port)))
            with BytesIO() as output:
                image.save(output, format="PNG")
                output.seek(0)
                file = discord.File(fp=output, filename="motd.png")
                if config.stats_use_embed:
                    message["embed"].set_image(url="attachment://motd.png")
                message["files"].append(file)
                
        if config.stats_use_embed and config.thumbnail_in_stats:
            thumbnail = renderer.get_thumbnail(address=(ip, int(port)))
            with BytesIO() as thumbnail_output:
                thumbnail.save(thumbnail_output, format="PNG")
                thumbnail_output.seek(0)
                file = discord.File(fp=thumbnail_output, filename="thumbnail.png")
                message["embed"].set_thumbnail(url="attachment://thumbnail.png")
                message["files"].append(file)
            
        await ctx.send(**message)

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
        except (BrokenPipeError, ConnectionRefusedError, struct.error) as e:
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

    #command to render the server motd
    @commands.command(name="motd")
    async def get_motd(self, ctx, address="127.0.0.1", port=None):
        if port == None:
            port = self.client.server_address[1]
        if address.startswith("192.") or address=="localhost" or address=="0.0.0.0":
            await ctx.send(config.motd_invalid_ip_message)
            return
        if address == "127.0.0.1" and not port==self.client.server_address[1]:
            await ctx.send(config.motd_invalid_ip_message)
            return
        if address == "127.0.0.1":
            title = config.motd_title
        else:
            title = address+":"+str(port)

        message_old = await ctx.send(config.motd_pinging_message)

        message = {}
        if config.motd_use_embed:
            message["embed"] = embed_builder(config.motd_embed, {})
        else:
            message["content"] = config.motd_message.strip().lstrip()

        renderer = motd_renderer.MOTDRenderer()
        image = renderer.get_full_image(title=title, address=(address, port))
        with BytesIO() as output:
            image.save(output, format="PNG")
            output.seek(0)
            message["file"] = discord.File(fp=output, filename="motd.png")
            if config.motd_use_embed:
                message["embed"].set_image(url="attachment://motd.png")

        await ctx.send(**message)
        await message_old.delete()

    #help command
    @commands.command(name="help")
    async def help(self, ctx):
        message = {}
        if config.help_use_embed:
            message["embed"] = embed_builder(config.help_output_embed, {})
        else:
            await ctx.send(config.help_message.lstrip().strip())
            return
        
        if config.thumbnail_in_help:
            renderer = motd_renderer.MOTDRenderer()
            ip, port = config.server_address.split(":")
            message["files"] = []
            thumbnail = renderer.get_thumbnail(address=(ip, int(port)))
            with BytesIO() as thumbnail_output:
                thumbnail.save(thumbnail_output, format="PNG")
                thumbnail_output.seek(0)
                file = discord.File(fp=thumbnail_output, filename="thumbnail.png")
                message["embed"].set_thumbnail(url="attachment://thumbnail.png")
                message["files"].append(file)
        await ctx.send(**message)
            
