from os import listdir, environ
from dotenv import load_dotenv
from discord import Intents
from discord.ext import commands

# ----- Setup ----- #
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

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
    
# Load the commands from the commands folder 
for file in listdir("commands"):
    if file.endswith(".py"): # Only load .py files
        bot.load_extension(f"commands.{file[:-3]}") # Remove the .py from the file name "file.py" -> "commands.file"

load_dotenv()
bot.run(environ["DISCORD-TOKEN"])
