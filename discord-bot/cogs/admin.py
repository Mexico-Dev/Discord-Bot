from discord.ext import commands
import discord
import utils
import json
import re 

from typing import Any, Union, Optional


class Announcement(commands.Converter):
    regex = re.compile(r"```(.*)\n*([\s\S]*?)\n*```", flags=re.MULTILINE)
    
    def __init__(self) -> None:
        self.message_id: Optional[Union[str, int]] = None
        self.channel_id: Optional[Union[str, int]] = None
        self.mentions: list[str] = []
        
        self.title: str = None
        self.description: Optional[str] = None
        self.thumbnail: Optional[str] = None
        self.image: Optional[str] = None
        self.fields: list[dict[str, str]] = []
        self.color: Optional[discord.Colour] = discord.Colour.default()

    @classmethod
    def from_dict(cls, data: dict):
        self = cls.__new__(cls)
        
        self.message_id = data.get("message_id")
        self.channel_id = data.get("channel_id")
        self.mentions = data.get("mentions", [])
        
        if color := data.get("color"):
            self.color = discord.Colour.from_rgb(*color)
        else:
            self.color = discord.Colour.default()
        
        self.title = data["title"]
        self.description = data.get("description")
        self.thumbnail = data.get("thumbnail")
        self.image = data.get("image")
        self.fields = data.get("fields", [])
        
        return self

    async def convert(self, ctx: utils.Context, argument: str):
        announcement = json.loads(self.regex.findall(argument)[0][1], object_hook=announcement_decoder)
        if not isinstance(announcement, Announcement):
            raise Exception("error in the format")
        
        mentions = [
            ctx.guild.get_role(role).mention
            if role != "everyone" else "@everyone"
            for role in announcement.mentions 
        ]
        announcement.mentions = mentions
        
        return announcement
    
    def to_embed(self, *, author: discord.Member, guild: discord.Guild) -> discord.Embed:
        embed = discord.Embed(color=self.color, title=self.title, description=self.description, timestamp=discord.utils.utcnow())
        embed.set_footer(text=f"Anuncio enviado por {author}", icon_url=author.avatar.url)
        
        if self.thumbnail is not None:
            embed.set_thumbnail(url=(self.thumbnail, guild.icon.url)[self.thumbnail == "guild"])
            
        if self.image is not None:
            embed.set_image(self.image)
            
        for field in self.fields:
            embed.add_field(**field)
        
        return embed
    
    def to_dict(self) -> dict:
        payload = {
            "message_id": self.message_id,
            "channel_id": self.channel_id,
            "mentions": self.mentions,
            "title": self.title
        }
        
        if self.color:
            payload["color"] = self.color.to_rgb()
        
        if self.description:
            payload["description"] = self.description
            
        if self.thumbnail:
            payload["thumbnail"] = self.thumbnail
            
        if self.image:
            payload["image"] = self.image
        
        if self.fields:
            payload["fields"] = self.fields
            
        return payload


class AnnouncementEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Announcement):
            return obj.to_dict()
        
        return super().default(obj)


def announcement_decoder(obj: Any) -> Any:
    if isinstance(obj, dict):
        if "title" in obj:
            return Announcement.from_dict(obj)
    
    return obj


class Admin(utils.Cog):
    def __init__(self, bot) -> None:
        super().__init__(bot)
        self.announces: utils.Config[Announcement] = utils.Config(
            "announces.json", object_hook=announcement_decoder, encoder=AnnouncementEncoder
        )
        
    def cog_check(self, ctx: utils.Context) -> bool:
        return ctx.author.guild_permissions.administrator
    
    @commands.command()
    async def announce(self, ctx: utils.Context, channel: discord.TextChannel, *, announcement: Announcement):
        """Envía un anuncio a un canal especifico"""
        msg = await channel.send(" ".join(map(str, announcement.mentions)), embed=announcement.to_embed(author=ctx.author, guild=ctx.guild), allowed_mentions=discord.AllowedMentions(roles=True, everyone=True))
        announcement.message_id = msg.id
        announcement.channel_id = channel.id
        
        await self.announces.put(ctx.message.id, announcement)
        await ctx.reply("Anuncio enviado!")
            
    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        if payload.message_id in self.announces:
            announcement = self.announces[payload.message_id]
            channel = await self.bot.fetch_channel(announcement.channel_id)
            author = await channel.guild.fetch_member(payload.data["author"]["id"])
            message = await channel.fetch_message(announcement.message_id)
            
            new_announcement: Announcement = json.loads(Announcement.regex.findall(payload.data["content"])[0][1], object_hook=announcement_decoder)
            new_announcement.channel_id = channel.id
            new_announcement.message_id = message.id
            mentions = [
                channel.guild.get_role(role).mention
                if role != "everyone" else "@everyone"
                for role in new_announcement.mentions 
            ]
            new_announcement.mentions = mentions
            
            await self.announces.put(payload.message_id, new_announcement)
            await message.edit(content=" ".join(map(str, new_announcement.mentions)), embed=new_announcement.to_embed(author=author, guild=channel.guild), allowed_mentions=discord.AllowedMentions(roles=True, everyone=True))


async def setup(bot):
    await bot.add_cog(Admin(bot))
