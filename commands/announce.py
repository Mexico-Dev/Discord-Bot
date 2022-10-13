from discord import Embed, TextChannel, Colour
from discord.ext.commands import Cog, command, has_permissions
from discord.abc import Role
from src.utils import Base, link
import re, json

# Administration Command
class Announce(Base, Cog):
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self.announces = {}
        # This regex is for the code blocks in the message ```json\n{...}\n```
        self.regex = re.compile(r"```(.*)\n*([\s\S]*?)\n*```", flags=re.MULTILINE)
        
    @has_permissions(mention_everyone=True)
    @command("announce", aliases=["news", "proclaim", "spot"], description="Envía un anuncio a un canal especifico")
    async def command_announce(self, ctx):
        message = ctx.message.content

        if len(message) < 0 and not self.regex.search(message):
            await ctx.reply("El mensaje no tiene ningún anuncio para enviar.")
            return

        try:
            # Extract the elements that are not part of the Embed initializer.
            message = json.loads(self.regex.findall(message)[0][1]) # Convert the raw message to a dict.
            channel = message.pop("channel", None)
            mentions = message.pop("mentions", [])
            color = message.pop("color", None)
            thumbnail = message.pop("thumbnail", None)
            image = message.pop("image", None)
            fields = message.pop("fields", None)

            # Check if the keys correspond to the Embed attributes
            if not all(x in Embed.__dict__ for x in message.keys()):
                await ctx.reply("El anuncio no tiene un formato válido")
                return

            if not channel:
                await ctx.reply("No se ha proporcionado un canal al que enviar el anuncio")
                return

            # Generate a embed with the parameters of the message
            embed: Embed = Embed(**message)
            channel: TextChannel = ctx.guild.get_channel(channel)  # Get the channel from the id
            if mentions:
                mentions: list[Role] = [
                    ctx.guild.get_role(role) 
                    if role != "everyone" else 
                    ctx.guild.default_role for role in mentions
                ]

            # Personalize the embed
            embed.set_footer(text=f"Anuncio enviado por {ctx.author}", icon_url=ctx.author.avatar.url)
            if color: embed.colour = Colour.from_rgb(*color)
            if fields: [embed.add_field(**field) for field in fields]
            if thumbnail: embed.set_thumbnail(url=(thumbnail, ctx.guild.icon.url)[thumbnail == "guild"])
            if image: embed.set_image(url=image)

            await channel.send(" ".join(map(str, mentions)), embed=embed)
            # Storage the command for later is edit
            self.announces[ctx.message.id] = {
                "id":  channel.last_message.id,
                "channel": channel,
                "embed": embed,
                "mentions": mentions
            }
            
            await ctx.reply("Anuncio enviado")
            
                 
        except Exception as e:
            await ctx.reply(f"Error al procesar el anuncio: ```{e}```")
            
    @Cog.listener("on_message_edit")
    async def on_message_edit(self, before, after):
        if before.id in self.announces:
            channel = self.announces[before.id]["channel"]
            message = channel.get_partial_message(self.announces[before.id]["id"])
            
            content = json.loads(self.regex.findall(after.content)[0][1])
            embed = self.announces[before.id]["embed"]
            mentions = content.pop("mentions", self.announces[before.id]["mentions"])
            
            # Update the embed
            if content.get("title"): embed.title = content["title"]
            if content.get("description"): embed.description = content["description"]
            if content.get("url"): embed.url = content["url"]
            if content.get("color"): embed.colour = Colour.from_rgb(*content["color"])
            if content.get("image"): embed.set_image(url=content["image"])
            if content.get("fields"):
                embed.clear_fields() 
                [embed.add_field(**field) for field in content["fields"]]
            if content.get("thumbnail"): 
                embed.set_thumbnail(
                    url=content["thumbnail"] 
                    if content["thumbnail"] != "guild" else 
                    channel.guild.icon.url
                )
            
            await message.edit(content=" ".join(map(str, mentions)), embed=embed)

setup = lambda bot: link(bot, Announce)
