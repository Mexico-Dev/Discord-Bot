from discord import Embed, TextChannel
from discord.ext.commands import Cog, command, has_permissions
from discord.abc import Role
from src.utils import Base, link, EmbedConstructor, CommandError
import re

# Administration Command
class Announce(Base, Cog):
    regex = re.compile(r"```(.*)\n*([\s\S]*?)\n*```", flags=re.MULTILINE)
    announces = {}
    channel = property(
        lambda self: self.bot.get_channel(
            self.bot.env["announcements_channel"])
    )

    @has_permissions(mention_everyone=True)
    @command("announce", aliases=["news", "proclaim", "spot"], description="Envía un anuncio a un canal especifico")
    async def announce(self, ctx):
        message = ctx.message.content
        content = self.regex.search(message)
        if len(message) < 0 and not content:
            raise CommandError(
                title="No puedes enviar un anuncio vacío",
                message="El mensaje no tiene ningún anuncio para enviar."
            )

        type_, content = content.groups()
        content = EmbedConstructor.loader(content, type_)
        mentions = content.pop("mentions", [])
        channel = content.pop("channel", self.channel)

        if not channel :
            raise CommandError(
                title="No hay canal al cual enviar el anuncio",
                message="No se ha especificado un canal al cual enviar el anuncio. Ademas de que no se ha encontrado un canal por defecto.",
                meta={"color": "#FF006E"}
            )
        else:
            if isinstance(channel, str):
                channel = self.bot.get_channel(int(channel))
                if not channel:
                    raise CommandError(
                        title="Canal no encontrado",
                        message="El canal especificado no se ha encontrado.",
                        meta={"color": "#FF006E"}
                    )

        # Generate a embed with the parameters of the message
        embed: Embed = EmbedConstructor.convert(content)
        if mentions:
            mentions: list[Role] = [
                ctx.guild.get_role(role)
                if role != "everyone" else
                ctx.guild.default_role for role in mentions
            ]

        # Personalize the embed
        embed.remove_footer()
        embed.set_footer(
            text=f"Anuncio enviado por {ctx.author}", 
            icon_url=ctx.author.avatar.url
        )
        
        if "thumbnail" in content:
            thumbnail = content["thumbnail"]
            embed.set_thumbnail(
                url=(thumbnail, ctx.guild.icon.url)[thumbnail == "guild"]
            )

        # Storage the command for later is edit
        announce = await self.channel.send(" ".join(map(str, mentions)), embed=embed)
        self.announces[ctx.message.id] = {
            "id":  announce.id,
            "channel": self.channel,
            "embed": embed,
            "mentions": mentions
        }
        await ctx.reply("Anuncio enviado")

    # @Cog.listener("on_message_edit")
    # async def on_message_edit(self, before, after):
    #     if before.id in self.announces:
    #         channel = self.announces[before.id]["channel"]
    #         message = channel.get_partial_message(
    #             self.announces[before.id]["id"])

    #         content = json.loads(self.regex.findall(after.content)[0][1])
    #         embed = self.announces[before.id]["embed"]
    #         mentions = content.pop(
    #             "mentions", self.announces[before.id]["mentions"])

    #         # Update the embed
    #         if content.get("title"):
    #             embed.title = content["title"]
    #         if content.get("description"):
    #             embed.description = content["description"]
    #         if content.get("url"):
    #             embed.url = content["url"]
    #         if content.get("color"):
    #             embed.colour = Colour.from_rgb(*content["color"])
    #         if content.get("image"):
    #             embed.set_image(url=content["image"])
    #         if content.get("fields"):
    #             embed.clear_fields()
    #             [embed.add_field(**field) for field in content["fields"]]
    #         if content.get("thumbnail"):
    #             embed.set_thumbnail(
    #                 url=content["thumbnail"]
    #                 if content["thumbnail"] != "guild" else
    #                 channel.guild.icon.url
    #             )

    #         await message.edit(content=" ".join(map(str, mentions)), embed=embed)

setup = lambda bot: link(bot, Announce)
