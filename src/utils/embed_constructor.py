from discord import Embed, Colour
from datetime import datetime
from typing import Literal
import json, toml, yaml


class EmbedConstructor:
    error = {
        "color": "#FFBE0B",
        "fields": [
            {
                "name": "¿Por que sucedió esto?",
                "value": "Hay muchas razones por las cuales puedo haber sucedido este error. Pero la mas probable es que hayas cometido un error de sintaxis al escribir tu comando.",
                "inline": False
            },
            {
                "name": "¿Cómo puedo solucionarlo?",
                "value": "Revisa tu sintaxis y vuelve a intentarlo. Existen muchas herramientas que te pueden facilitar esta tarea. Puedes usar:\n > **JSON** - https://jsonformatter.org/\n > **TOML** - https://toml.io/en/\n > **YAML** - https://yaml-online-parser.appspot.com/",
                "inline": False
            },
            {
                "name": "¿Cuales son los formatos soportados?",
                "value": "Los formatos soportados son: **JSON**, **TOML** y **YAML**.",
                "inline": False
            }
        ]
    }
    
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
            {key: value for key, value in kwargs.items() if key in ("thumbnail", "image", "footer", "author", "fields")}
        ]

    @staticmethod
    def convert(kwargs: dict) -> Embed:
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
    
    @staticmethod
    def loader(string: str, type_:Literal["json", "toml", "yaml"]) -> dict:
        from command_error import CommandError
        if type_:
            try:
                return EmbedConstructor.converters[type_](string)
            except:
                raise CommandError(
                    typeof="embed",
                    title="El formato no es válido",
                    message=f"El formato contenido de la cadena no es válido para el tipo: **{type_}** especificado.",
                    meta=EmbedConstructor.error
                )

        for try_type in EmbedConstructor.converters:
            try:
                return EmbedConstructor.converters[try_type](string)
            except:
                continue
        raise CommandError(
            typeof="embed",
            title="El contenido no es válido",
            message="El contenido de la cadena no es válido para ninguno de los formatos soportados.",
            meta=EmbedConstructor.error
        )