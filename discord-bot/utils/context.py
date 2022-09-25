import aiohttp
import discord
import datetime
from discord.ext import commands


class Context(commands.Context):
    @property
    def session(self) -> aiohttp.ClientSession:
        return self.bot.session
    
    @property
    def locale(self) -> discord.Locale:
        if self.interaction is not None:
            return self.interaction.locale
        
        return self.guild.preferred_locale
        
    def utcnow(self) -> datetime.datetime:
        return discord.utils.utcnow()
