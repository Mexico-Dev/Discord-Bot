# Base class for all cogs ---------------------------
from discord.ext.commands import Bot, Cog

Base = type("Base", (object,), {"__init__": lambda self, bot: setattr(self, "bot", bot)})  # Create a base inheritance
async def link(bot: Bot, typeof: Cog) -> None:
    await bot.add_cog(typeof(bot))
# --------------------------------------------------

# Embed constructor ---------------------------
from discord import Embed, Colour
from datetime import datetime
import json, toml, yaml

class EmbedConstructor:
    converters = {
        "json": json.loads,
        "toml": toml.loads,
        "yaml": yaml.safe_load,
    }
    typing = {
        "title": str,
        "description": str,
        "color": (str, list, tuple),
        "timestamp": str,
        "footer": dict,
        "image": str,
        "thumbnail": str,
        "author": dict,
        "fields": list,
        "url": str,
    }

    @staticmethod
    def __parse_kwargs(kwargs: dict) -> list[dict]:
        """
        It validates if the kwargs are part of the Embed class properties and if the type of the value is correct.
        In addition, it removes null values and parses values such as color. After divide the kwargs into those needed for the class initializer and those added after initialization.

        Parameters
        ----------
        kwargs: dict
            The dictionary to process.

        Returns
        -------
        list[dict]: Return a partitions of the dictionary.
        """
        to_delete = []
        for key, value in kwargs.items():
            if not key in Embed.__dict__:
                raise KeyError(f"Invalid key: {key} in kwargs")
            if not isinstance(value, EmbedConstructor.typing[key]):
                if not value is None:
                    raise TypeError(
                        f"Invalid type: {type(value)} for key: {key} in kwargs")
                to_delete.append(key)

            if key == "color":
                if isinstance(value, str):
                    kwargs[key] = Colour.from_str(value)
                elif isinstance(value, (list, tuple)):
                    if not len(value) == 3:
                        raise ValueError(
                            f"Invalid length: {len(value)} for key: {key} in kwargs")
                    kwargs[key] = Colour.from_rgb(*value)

            if key == "timestamp":
                if value in ("now", "current", "today"):
                    kwargs[key] = datetime.utcnow()
                else:
                    kwargs[key] = datetime.fromisoformat(value)

        for key in to_delete: del kwargs[key]
        return [
            {key: value for key, value in kwargs.items() if key in ("title", "description", "color", "timestamp", "url")},
            {key: value for key, value in kwargs.items() if not key in ("thumbnail", "image", "footer", "author", "fields")}
        ]

    @staticmethod
    def convert(embed: str, type_:str = "json") -> Embed:
        kwargs = EmbedConstructor.converters[type_](embed)
        init, before = EmbedConstructor.__parse_kwargs(kwargs)
        embed = Embed(**init)

        if "thumbnail" in before:
            embed.set_thumbnail(url=before["thumbnail"])
        if "image" in before:
            embed.set_image(url=before["image"])
        if "footer" in before:
            embed.set_footer(**before["footer"])
        if "author" in before:
            embed.set_author(**before["author"])
        if "fields" in before:
            [embed.add_field(**field) for field in before["fields"]]

        return embed

# --------------------------------------------------


class MultiDict(dict):
    """A multi-keyed dictionary."""

    def __search(self, key: str):
        for k in self:
            if key in k and isinstance(k, (tuple, list)):
                return k
        return None

    def __setitem__(self, key, value):
        key = self.__search(key) or key
        return super().__setitem__(key, value)

    def __getitem__(self, key):
        key = self.__search(key) or key
        return super().__getitem__(key)

    def __delitem__(self, key):
        key = self.__search(key) or key
        return super().__delitem__(key)

    def get(self, key, default=None):
        key = self.__search(key) or key
        return super().get(key, default)
