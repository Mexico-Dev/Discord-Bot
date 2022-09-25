from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


class Cog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: Bot = bot
    