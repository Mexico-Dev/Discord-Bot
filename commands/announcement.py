import discord
from discord.ext.commands import Bot, Cog, command, slash_command
from discord.commands import Option
from utils import link


class Announcement(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command()
    async def announce(self, ctx, channel: Option(discord.TextChannel, "The channel to send the announcement to"), *, message: Option(str, "The message to send")):
        await ctx.respond("Done!")
        

setup = lambda bot: link(bot, Announcement)