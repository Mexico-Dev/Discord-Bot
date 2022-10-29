from discord import Embed
from discord.ext.commands import Cog, hybrid_command, cooldown, BucketType
from src.utils import Base, link, MagicEmbed


class Offer(Base, Cog):
    magic_embed: list[MagicEmbed] = []
    channel = property(
        lambda self: self.bot.get_channel(
            self.bot.env["offer_channel"]
        )
    )
    
    # @cooldown(3, (3600*24), BucketType.user)
    @hybrid_command(
        name="offer",
        description="Envía una oferta de trabajo al servidor.",
        aliases=["oferta", "ofertar"]
    )
    async def offer(self, ctx):
        if not ctx.interaction:
            await ctx.message.delete()
        
        reset = lambda : print("reset")
        is_offer = ctx.guild.get_role(int(self.bot.env["offer_role"])) in ctx.author.roles
        embed = MagicEmbed(
            author_name=f"{ctx.author.name}#{ctx.author.discriminator}",
            author_icon=ctx.author.avatar.url,
            footer="offer"
        )
        
        await ctx.defer()
        await embed.launch(
            ctx, reset,
            (self.moderator, self.send)[is_offer]
        )
    
    async def moderator(self,ctx, embed: Embed):
        print(embed)
    
    async def send(self,ctx, embed: Embed):
        print(embed)
    

setup = lambda bot: link(bot, Offer)
