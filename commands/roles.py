import discord
from discord.ext.commands import Bot, Cog, command, slash_command
from discord.commands import Option
from discord.ui import Select
from utils import embedTemp, link

class Roles(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        
    @slash_command()
    async def roles(self, ctx, role: Option(str, "The role to add/remove")):
        print(role, ctx.author.roles)
        await ctx.respond("Done!")
    
    @command(name="roles", aliases=["r"], description="The roles to add/remove")
    async def admin_roles(self, ctx):
        print(ctx.author.roles)
         
        
setup = lambda bot: link(bot, Roles)