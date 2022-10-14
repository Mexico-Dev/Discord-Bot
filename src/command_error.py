from discord.ext.commands import CommandError
from dataclasses import dataclass, field
from .utils import EmbedConstructor
from typing import Literal
import json


@dataclass
class CommandError(CommandError):
    title: str
    message: str
    type: Literal["str", "Embed"] = field(default="str")
    meta: dict = field(default_factory={  # kwargs of the embed
        "color": 0x2F3136,
        "timestamp": None,
        "footer": None,
        "image": None,
        "thumbnail": "guild",
    })

    embed = property(lambda self: EmbedConstructor.convert(
        json.dumps(
            {"title": self.title, "description": self.message, **self.meta}
        )
    ))

    def __str__(self):
        return f"""**{self.title}**\n{self.message}"""
