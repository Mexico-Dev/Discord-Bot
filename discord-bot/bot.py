from discord.ext import commands
import discord
import traceback
import aiohttp
import sys

import utils
from typing import Optional, Union
from cogs import initial_extensions


description = """
MexicoDev's Discord-Bot
"""


def _prefix_callable(bot, msg: discord.Message):
    user_id = bot.user.id
    base = [f"<@!{user_id}> ", f"<@{user_id}> "]
    if msg.guild is None:
        base.append('?')
        base.append('!')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['?', '!']))
    
    return base


class ProxyObject(discord.Object):
    def __init__(self, guild: Optional[discord.abc.Snowflake]):
        super().__init__(id=0)
        self.guild: Optional[discord.abc.Snowflake] = guild
        

class Bot(commands.Bot):
    def __init__(self) -> None:
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)
        intents = discord.Intents(
            guilds=True,
            members=True,
            messages=True,
            message_content=True
        )
        
        super().__init__(
            command_prefix=_prefix_callable,
            description=description,
            allowed_mentions=allowed_mentions,
            intents=intents,
            case_insensitive=True
        )
        
        self.env = utils.Environment()
        
    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        
        # prefixes[guild_id]: list
        self.prefixes: utils.Config[list[str]] = utils.Config("prefixes.json")
        
        self.bot_app_info = await self.application_info()
        self.owner_id = self.bot_app_info.owner.id
        
        for ext in initial_extensions:
            try:
                await self.load_extension(ext)
            except Exception as e:
                print(f"Failed to load extension {ext}.", file=sys.stderr)
                traceback.print_exc()
                
        # sync
        await self.tree.sync()
        
    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner
    
    def get_guild_prefixes(self, guild: Optional[discord.abc.Snowflake], *, local_inject=_prefix_callable) -> list[str]:
        proxy_msg = ProxyObject(guild)
        return local_inject(self, proxy_msg) 
        
    def get_raw_guild_prefixes(self, guild_id: int) -> list[str]:
        return self.prefixes.get(guild_id, ['?', '!'])
        
    async def set_guild_prefixes(self, guild: discord.abc.Snowflake, prefixes: list[str]) -> None:
        if len(prefixes) == 0:
            await self.prefixes.put(guild.id, [])
        elif len(prefixes) > 10:
            raise RuntimeError("Cannot have more than 10 custom prefixes.")
        else:
            await self.prefixes.put(guild.id, sorted(set(prefixes), reverse=True))
        
    async def get_context(
        self, 
        origin: Union[discord.Message, discord.Interaction], 
        *, 
        cls=utils.Context
    ):
        return await super().get_context(origin, cls=cls)

    async def on_command_error(self, ctx: utils.Context, error: commands.CommandError):
        err = getattr(error, "original", error)
        err = getattr(err, "original", err) # original hybrid command error
        if isinstance(err, commands.CommandNotFound):
            return
        elif isinstance(err, commands.NoPrivateMessage):
            await ctx.send("Este comando no se puede usar en mensajes privados")
        else:
            await ctx.send(f"{err.__class__.__name__}: {err}")

        print(f"In {ctx.command.qualified_name}:", file=sys.stderr)
        traceback.print_tb(err.__traceback__)
        print(f"{err.__class__.__name__}: {err}", file=sys.stderr)

    async def on_ready(self):
        print(f"Ready: {self.user} (ID: {self.user.id})")

    async def close(self):
        await super().close()
        await self.session.close()
        
    def run(self):
        super().run(self.env.discord_token, reconnect=True)
    