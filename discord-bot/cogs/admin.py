from discord.ext import commands
import discord
import utils
import json
import re 

from typing import Any, Union


class Announcement(commands.Converter):
    def __init__(self, message_id: Union[int, str] = None, *, channel_id: Union[int, str] = None, embed: discord.Embed = None, mentions: list = None) -> None:
        self.message_id = message_id
        self.channel_id = channel_id
        self.embed = embed
        self.mentions = mentions
        self.regex = re.compile(r"```(.*)\n*([\s\S]*?)\n*```", flags=re.MULTILINE)

    async def convert(self, ctx: utils.Context, argument: str):
        data: dict = json.loads(self.regex.findall(argument)[0][1])
        channel = data.pop("channel")
        mentions = data.pop("mentions", [])
        if mentions:
            mentions = [
                ctx.guild.get_role(role)
                if role != "everyone" else ctx.guild.default_role
                for role in mentions 
            ]
        
        if color := data.get("color"):
            data["color"] = discord.Colour.from_rgb(*color)
        else:
            data["color"] = discord.Colour.default()
        
        thumbnail = data.pop("thumbnail", None)
        image = data.pop("image", None)
        fields = data.pop("fields", [])
        
        # Embed
        embed = discord.Embed(timestamp=ctx.utcnow(), **data).set_footer(text=f"Anuncio enviado por {ctx.author}", icon_url=ctx.author.avatar.url)
        
        if thumbnail is not None:
            embed.set_thumbnail(url=(thumbnail, ctx.guild.icon.url)[thumbnail == "guild"])
            
        if image is not None:
            embed.set_image(image)
            
        for field in fields:
            embed.add_field(**field)
        
        ad = Announcement(
            0, channel_id=channel, embed=embed, mentions=mentions
        )
        
        return ad
    
    def to_dict(self) -> dict:
        payload = {
            "message_id": self.message_id,
            "channel_id": self.channel_id,
            "embed": self.embed.to_dict(),
        }

        payload["mentions"] = [
            role.id 
            if isinstance(role, discord.Role) else role
            for role in self.mentions
        ]
        
        return payload


class AnnouncementEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Announcement):
            return obj.to_dict()
        
        return super().default(obj)


def announcement_decoder(obj: Any) -> Any:
    if isinstance(obj, dict):
        if "message_id" in obj:            
            return Announcement(
                obj["message_id"], channel_id=obj["channel_id"], embed=discord.Embed.from_dict(obj["embed"]), mentions=obj["mentions"]
            )
    
    return obj


class Admin(utils.Cog):
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self.announces: utils.Config[Announcement] = utils.Config(
            "announces.json", object_hook=announcement_decoder, encoder=AnnouncementEncoder
        )
        self.regex = re.compile(r"```(.*)\n*([\s\S]*?)\n*```", flags=re.MULTILINE)
        
    def cog_check(self, ctx: utils.Context) -> bool:
        return ctx.author.guild_permissions.administrator
    
    @commands.command()
    async def announce(self, ctx: utils.Context, channel: discord.TextChannel, *, announcement: Announcement):
        """Envía un anuncio a un canal especifico"""
        msg = await channel.send(" ".join(map(str, announcement.mentions)), embed=announcement.embed)
        announcement.message_id = msg.id
        
        await self.announces.put(ctx.message.id, announcement)
        await ctx.reply("Anuncio enviado!", allowed_mentions=discord.AllowedMentions(roles=True, everyone=True))
        
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.id in self.announces:
            announcement = self.announces[before.id]
            channel = await self.bot.fetch_channel(announcement.channel_id)
            message = await channel.fetch_message(announcement.message_id)
            
            content = json.loads(self.regex.findall(after.content)[0][1])
            embed = announcement.embed
            mentions = content.pop("mentions", announcement.mentions)
            
            # Update the embed
            if title := content.get("title"): 
                embed.title = title
            
            if description := content.get("description"): 
                embed.description = description
            
            if url := content.get("url"): 
                embed.url = url
            
            if color := content.get("color"): 
                embed.colour = discord.Colour.from_rgb(*color)
            
            if image := content.get("image"): 
                embed.set_image(url=image)
            
            if fields := content.get("fields"):
                embed.clear_fields() 
                [embed.add_field(**field) for field in fields]
            
            if thumbnail := content.get("thumbnail"): 
                embed.set_thumbnail(
                    url=thumbnail
                    if thumbnail != "guild" else 
                    channel.guild.icon.url
                )
            
            await self.announces.put(before.id, announcement)
            await message.edit(content=" ".join(map(str, mentions)), embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))
