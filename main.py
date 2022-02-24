import chatlink
import bot
import config

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
    client = bot.BotClient()
    print("Starting the bot...")
    client.run(config.bot_token)
