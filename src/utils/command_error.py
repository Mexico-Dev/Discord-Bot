from discord.ext.commands import CommandError as _CommandError
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class CommandError(_CommandError):
    title: str
    message: str
    typeof: Literal["str", "embed"] = "str"
    meta: dict = field(default_factory=lambda: {"color": "#FF006E"}) # Kwargs for the embed constructor

    @property
    def embed(self):
        from .embed_constructor import EmbedConstructor
        return EmbedConstructor.convert(
            {"title": self.title, "description": self.message, **self.meta}
        )

    def __str__(self):
        return f"""**{self.title}**\n{self.message}"""