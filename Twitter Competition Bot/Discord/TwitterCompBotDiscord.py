import tweepy, json, discord, time, threading, DiscordConstants
from discord.ext import commands

twitter_bearer_token = DiscordConstants.twitter_bearer_token
bot_token = DiscordConstants.bot_token
bot_admin_chat_id = DiscordConstants.bot_admin_chat_id
read_file = DiscordConstants.read_file

auth = tweepy.OAuth2BearerHandler(twitter_bearer_token)
api = tweepy.API(auth)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/')

@bot.command()
async def test(ctx):
    print("Testing")


bot.add_command(test)

