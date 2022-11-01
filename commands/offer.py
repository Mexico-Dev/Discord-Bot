from discord import Embed
from discord.ext.commands import Cog, hybrid_command, Context
from src.utils import Base, link, MagicEmbed


class Offer(Base, Cog):
    channel = property(
        lambda self: self.bot.get_channel(
            self.bot.env["offer_channel"]
        )
    )
    
    @hybrid_command(
        name="offer",
        description="Envía una oferta de trabajo al servidor.",
        aliases=["oferta", "ofertar"]
    )
    async def offer(self, ctx: Context):
        if not ctx.interaction:
            await ctx.message.delete()

        event = MagicEmbed(ctx, "offer", (60 * 10))
        @event.on_ready
        async def on_ready(interaction, embed):
            print("Ready")
        
        await event.launch()
    

setup = lambda bot: link(bot, Offer)
