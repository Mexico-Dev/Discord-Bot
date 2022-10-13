from discord.ext.commands import Cog, command
from discord import app_commands
from src.utils import Base, link

class HowTo(Base, Cog):
    
    @app_commands.command(
        name="how-to",
        description="Respuesta a las preguntas más frecuentes",)
    async def slash_how_to(self, ctx):
        pass
        
    
    @command("how_to", aliases=["como", "como_hacer", "como_hago", "como_hacerlo", "como_hacerlo"], description="Muestra un tutorial")
    async def command_how_to(self, ctx):
        pass

setup = lambda bot: link(bot, HowTo)
