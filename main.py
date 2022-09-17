from os import listdir, environ
from dotenv import load_dotenv
from discord import Intents
from discord.ext import commands

# ----- Setup ----- #
paths = {"commands": r"commands"}
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents)

@bot.event
async def on_ready():
    print("\x1b[1;32m[+]\x1b[0m Bot is currently online")
    print(f"\t\x1b[1;30m[!]\x1b[0m Current Prefix: {bot.command_prefix}")
    print(f"\t\x1b[1;30m[!]\x1b[0m Connected to Discord as: {bot.user.name}#{bot.user.discriminator}")
    print(f"\t\x1b[1;30m[!]\x1b[0m Logged in as: {bot.user.id}")  

@bot.command(name="reload")
async def admin_ping(ctx):
    await ctx.send("pong")

# ----- Commands ----- #
@bot.slash_command()
async def ping(ctx, name: str = None):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")
    

for file in listdir(paths["commands"]):
    if file.endswith(".py"):
        bot.load_extension(f"{paths['commands']}.{file[:-3]}")


load_dotenv()
bot.run(environ["DISCORD-TOKEN"])