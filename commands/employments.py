from discord.ext.commands import Cog, command
from src.utils import Base, link


class Employments(Base, Cog):
    @command("employments", aliases=["empleo"], description="Envía una sugerencia al servidor")
    async def command_suggest(self, ctx):
        pass
    

setup = lambda bot: link(bot, Employments)
