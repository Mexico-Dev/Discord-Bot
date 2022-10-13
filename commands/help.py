from discord import Embed, TextChannel, Colour
from discord.ext.commands import Cog, command, has_permissions
from discord import app_commands
from src.utils import Base, link


class Help(Base, Cog):
    # @app_commands(name="help", description="Muestra la ayuda del bot")
    # async def slash_help(self, ctx):
    #     await ctx.respond("La ayuda está en desarrollo", ephemeral=True)
        
    @command("help", aliases=["ayuda", "ayudame", "ayudar"], description="Muestra la ayuda del bot")
    async def command_help(self, ctx):
        await ctx.send("La ayuda está en desarrollo")
        
setup = lambda bot: link(bot, Help)
