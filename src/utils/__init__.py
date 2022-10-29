from .command_error import *
from .embed_constructor import *
from .magic_embed import *
from .multi_dict import *
from .storage import *

from discord.ext.commands import Bot, Cog
Base = type(
    "Base", (object,),
    {"__init__": lambda self, bot: setattr(self, "bot", bot)}
)

async def link(bot: Bot, typeof: Cog) -> None:
    await bot.add_cog(typeof(bot))
