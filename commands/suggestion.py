from discord.ext.commands import Cog, command
from src.utils import Base, link


class Suggestion(Base, Cog):
    @command("suggest", aliases=["sugerencia", "sugerir"], description="Envía una sugerencia al servidor")
    async def command_suggest(self, ctx):
        pass

setup = lambda bot: link(bot, Suggestion)
