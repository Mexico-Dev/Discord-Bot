from discord.ext.commands import Cog, hybrid_command, cooldown, BucketType
from discord import app_commands, Embed, TextChannel
from src.utils import Base, link, CommandError


# Typing
from typing import TypedDict
class User(TypedDict):
    name: str
    avatar: str


class Suggestion(Base, Cog):
    suggestions = {}
    channel: TextChannel = property(lambda self: self.bot.get_channel(
        int(self.bot.env["suggestion_channel"])))

    @cooldown(1, (3600*24), BucketType.user)
    @hybrid_command(
        name="suggest",
        description="Envía una sugerencia al staff (Esta puede ser alguna mejora, idea, evento, etc.)",
        aliases=["sugerencia", "sugerir"]
    )
    @app_commands.describe(title="Titulo de la sugerencia", description="Descripción de la sugerencia")
    async def suggest(self, ctx, title: str, *, description: str):
        reset = lambda: self.suggest.reset_cooldown(ctx)
        user: User = {
            "name": f"{ctx.author.name}#{ctx.author.discriminator}",
            "avatar": ctx.author.avatar.url
        }

        embed = self.__create_embed(title, description, user, reset)
        message = await self.channel.send(embed=embed)
        
        if not ctx.interaction:
            self.suggestions[ctx.message.id] = (message.id, embed)            
        await message.add_reaction("✅"); await message.add_reaction("❌")
        await message.create_thread(name=title, auto_archive_duration=60)

        await ctx.defer(ephemeral=True)
        await ctx.reply("Sugerencia enviada con éxito", delete_after=10)

    def __create_embed(self, title: str, description: str, user: User, reset) -> Embed:
        if not 4 <= len(title) <= 24:
            reset()
            raise CommandError(
                typeof="embed",
                title=f"Mmmm, tu titulo no es muy expresivo, intenta con uno más {('largo', 'corto')[len(title) > 24]}.",
                message="Para que tu sugerencia sea mas atractiva, intenta usar un titulo que sea corto y conciso. Pero tampoco te excedas, ya que un titulo muy largo puede ser difícil de entender y no llamar la atención de nadie. Te recomendamos que sea de 4 a 24 caracteres. Asi podrás captar la atención de los demás usuarios y staff.",
                meta={"color": "#FFBE0B"}
            )
        if not 50 <= len(description) <= 1024:
            reset()
            raise CommandError(
                typeof="embed",
                title=f"Tu descripción es demasiado {('corta', 'larga')[len(description) > 1024]}.",
                message="Para que todos entiendan lo que quieres decir, explaya tu idea, que no quede duda de lo que quieres decir. Pero tampoco te excedas, ya que una descripción desmesurada puede que a nadie le interese leer. Te recomendamos que tu descripción sea de 50 a 1024 caracteres.",
                meta={"color": "#FFBE0B"}
            )

        embed = Embed(title=title, description=description, color=0x2F3136)
        embed.set_footer(
            text=f"Sugerencia enviada por {user['name']}", icon_url=user['avatar'])
        return embed
    
    @Cog.listener("on_message_delete")
    async def on_message_delete(self, message):
        if message.id in self.suggestions:
            id_, _ = self.suggestions.pop(message.id)
            suggestion = await self.channel.fetch_message(id_)
            await suggestion.delete()

    @Cog.listener("on_message_edit")
    async def on_message_edit(self, before, after):
        if before.id in self.suggestions:
            id_, embed = self.suggestions[before.id]
            suggestion = await self.channel.fetch_message(id_)
            title, *description = after.content.split(" ")[1:]
            
            embed.title = title
            embed.description = " ".join(description)
            await suggestion.edit(embed=embed)

setup = lambda bot: link(bot, Suggestion)
