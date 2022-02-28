from utils import query, rcon
import discord
import config
import textwrap

class Commands(discord.ext.commands.Cog, name="commands module"):
    def __init__(self, client):
        self.client = client
        
        query_address_str = config.query_address.split(":")[0]
        query_port = int(config.query_address.split(":")[1])
        self.query_address = (query_address_str, query_port)
        self.Query = query.Query(self.query_address)

        rcon_split = config.rcon_address.split(":")
        rcon_ip = rcon_split[0]
        rcon_port = int(rcon_split[1])
        self.rcon = rcon.RCON(rcon_ip, rcon_port, config.rcon_password)
        self.rcon.login()

    #command to list players
    @discord.ext.commands.command(name="players")
    async def players(self, ctx):
        stats = self.Query.full_stat()
        message_base = config.player_list_heading.format(
            players=stats["numplayers"], maxplayers=stats["maxplayers"])
        
        for player in stats["players"]:
            message_base = message_base+"\n"+config.player_list_items.format(player=player)
        await ctx.send(message_base)

    #command to get some misc server stats
    @discord.ext.commands.command(name="stats")
    async def stats(self, ctx):
        stats = self.Query.full_stat()
        response = config.stats_output.format(motd=stats["hostname"],
                        players=stats["numplayers"], maxplayers=stats["maxplayers"],
                        mapname=stats["map"], server_port=stats["hostport"])
        await ctx.send(response)

    #command to run a command in mc
    @discord.ext.commands.command(name="run")
    async def run_cmd(self, ctx):
        if config.console_channel == False:
            return
        if not ctx.channel.id == config.console_channel_id:
            return
        
        cmd = ctx.message.content.replace(ctx.prefix + "run", "", 1).lstrip()
        try:
            response = self.rcon.send_cmd(cmd)
        except (BrokenPipeError, ConnectionRefusedError) as e:
            #error handling in case the server restarts
            print("Attempting to reconnect to the RCON server...")
            try:
                self.rcon.reconnect()
                response = self.rcon.send_cmd(command)
                print("Reconnection successful!")
            except ConnectionRefusedError:
                response = "Error: The connection to the RCON server was refused. Either the server is offline/starting or rcon is not enabled."

        max_length = 2000-len(config.run_output)
        msg = config.run_output.format(output=textwrap.shorten(response, width=max_length)) 
        
        await ctx.send(msg)

    @discord.ext.commands.command(name="help")
    async def help(self, ctx):
        await ctx.send(config.help_message)
