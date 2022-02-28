import chatlink
import bot
import config
from commands import Commands

if config.webhook == True:
    chatlink_object = chatlink.Chatlink()
    for line in chatlink_object.main():
        print("MC -> Discord: "+text)
        data = {
            "content": text,
            "username": config.discord_nickname
        }
        r = requests.post(config.webhook_url, json=data)
else:
    client = bot.BotClient(command_prefix=config.command_prefix,
                           help_command=None)
    client.add_cog(Commands(client))
    print("Starting the bot...")
    client.run(config.bot_token)
