import discord
from discord import Embed, Colour, SelectOption, Button, ButtonStyle
from discord.ext.commands import Context
from discord.ui import View, Button, Select
from typing import Callable, Literal, Optional, Any
import asyncio


class MagicEmbed:
    class __Embed(Embed):
        __default_embed: dict = dict(
            title="<Tu título>",
            description="<Tu descripción>",
            color=Colour.from_rgb(255, 255, 255),
        )

        def __init__(self, **kwargs) -> None:
            self.__guild_icon: str = kwargs.pop("guild_icon")
            self.__mods: list[dict] = []

            kwargs = self.__default_embed | kwargs
            super().__init__(**kwargs)

        def __next__(self) -> Embed:
            # TODO: Revisar por que falla al usar el método next() cuando se quiere revertir un cambio hecho al embed - undo
            before = self.__mods.pop() if len(
                self.__mods) > 1 else self.__mods[0]
            self = Embed.from_dict(before)
            return self

        def is_sendable(self) -> bool:
            return self.title != self.__default_embed["title"] and \
                self.description != self.__default_embed["description"]
        
        def set_item(
            self,
            typeof: Literal["title", "description", "color", "thumbnail", "image", "url", "field", "footer"],
            value: str
        ) -> bool:
            if typeof == "title":
                if 4 <= len(value) <= 24:
                    self.title = value

            elif typeof == "description":
                if len(value) >= 16:
                    self.description = value

            elif typeof == "color":
                if value.startswith("#") or value.startswith("0x") or \
                        value.startswith("0x#") or value.startswith("rgb"):
                    self.color = Colour.from_str(value)

            elif typeof == "thumbnail":
                if value.startswith("http"):
                    self.set_thumbnail(url=value)
                elif value == "guild":
                    self.set_thumbnail(url=self.__guild_icon)

            elif typeof == "image":
                if value.startswith("http"):
                    self.set_image(url=value)

            elif typeof == "url":
                if value.startswith("http"):
                    self.url = value

            elif typeof == "field":
                name, value, inline = value.split("|")
                inline = inline.lower() == "true"
                self.add_field(name=name, value=value, inline=inline)

            elif typeof == "footer":
                self.set_footer(**value)

            else:
                return False

            self.__mods.append(self.to_dict())
            return True

    __options: Select = Select(
        placeholder="Personaliza tu embed",
        options=[
            SelectOption(label="Titulo", value="title",
                         description="Cambia el titulo del embed", emoji="✒"),
            SelectOption(label="Descripción", value="description",
                         description="Cambia la descripcion del embed", emoji="📝"),
            SelectOption(label="Color", value="color",
                         description="Cambia el color del embed", emoji="🎨"),
            SelectOption(label="Thumbnail", value="thumbnail",
                         description="Cambia el thumbnail del embed", emoji="📌"),
            SelectOption(label="Imagen", value="image",
                         description="Cambia la imagen del embed", emoji="🖼"),
            SelectOption(label="URL", value="url",
                         description="Cambia la url del embed", emoji="🔗"),
            SelectOption(label="Añade un campo", value="field",
                         description="Añade un campo al embed", emoji="➕"),
        ]
    )

    __buttons: list[Button] = [
        Button(label="Enviar", style=ButtonStyle.green,
               emoji="✅", custom_id="send"),
        Button(label="Cancelar", style=ButtonStyle.danger,
               emoji="❌", custom_id="cancel"),
        Button(label="Deshacer", style=ButtonStyle.grey,
               emoji="↩", custom_id="undo"),
    ]

    def __init__(self, ctx: Context, typeof: Literal["announce", "offer"], timeout: Optional[float] = 180, **kwargs) -> None:
        self.__ctx: Context = ctx
        self.__view: View = View(timeout=timeout)
        self.__embed: Embed = MagicEmbed.__Embed(
            **kwargs | {"guild_icon": ctx.guild.icon.url})

        MagicEmbed.__options.callback = self.__on_select
        self.__view.add_item(MagicEmbed.__options)

        for button in MagicEmbed.__buttons:
            button.callback = self.__on_click
            self.__view.add_item(button)

        self.__embed.set_item("footer", {
            "text": f"{('Anuncio', 'Oferta')[typeof == 'offer']} enviada por {ctx.author.name}#{ctx.author.discriminator}",
            "icon_url": ctx.author.avatar.url
        }
        )

    def on_ready(self, callback: Callable[[discord.Interaction, Embed], None]) -> None:
        """Sett the callback associated with the send button """
        self.__on_ready = callback

    def __check(self, interaction: discord.Interaction) -> bool:
        # TODO: Revisar por que cuando 2 personas usan el comando al mismo tiempo, el bot le sede el control a la ultima persona que lo uso
        is_author = interaction.user == self.__ctx.author
        is_channel = interaction.channel == self.__ctx.channel

        return is_author and is_channel

    async def __on_ready(self, interaction: discord.Interaction, embed: Embed) -> None:
        """The callback associated with the send button """
        pass

    async def __on_select(self, interaction: discord.Interaction) -> None:
        """The callback associated with the select menu """
        if not self.__check(interaction):
            return await interaction.response.send_message("No puedes usar este menú", ephemeral=True)

        check = lambda m: m.author == self.__ctx.author and m.channel == self.__ctx.channel
        option = interaction.data["values"][0]

        match option:
            case "title":
                await interaction.response.send_message("Escribe el nuevo titulo del embed", ephemeral=True)
            case "description":
                await interaction.response.send_message("Escribe la nueva descripción del embed", ephemeral=True)
            case "color":
                await interaction.response.send_message("Escribe el nuevo color del embed `rgb(R, G, B)` o Hex", ephemeral=True)
            case "thumbnail":
                await interaction.response.send_message("Escribe la nueva url del thumbnail del embed o `guild`", ephemeral=True)
            case "image":
                await interaction.response.send_message("Escribe la nueva url de la imagen del embed", ephemeral=True)
            case "url":
                await interaction.response.send_message("Escribe la nueva url del embed", ephemeral=True)
            case "field":
                await interaction.response.send_message("Escribe el nombre del campo, su valor y si es inline separado por `|`", ephemeral=True)
            
        try:
            message: discord.Message = await self.__ctx.bot.wait_for("message", check=check, timeout=60)

        except asyncio.TimeoutError:
            return await interaction.response.send_message("Se ha acabado el tiempo", ephemeral=True)

        if not self.__embed.set_item(option, message.content):
            return await interaction.response.send_message("Opción no válida", ephemeral=True)

        await self.__root.edit(embed=self.__embed)
        await message.delete()

    async def __on_click(self, interaction: discord.Interaction) -> None:
        """The callback associated with the buttons """
        if not self.__check(interaction):
            return await interaction.response.send_message("No puedes usar este botón", ephemeral=True)

        custom_id = interaction.data["custom_id"]

        if custom_id == "send":
            if self.__embed.is_sendable():
                await self.__on_ready(interaction, self.__embed)
                self.__view.stop()
                return
            return await interaction.response.send_message("No puedes enviar un embed vacío", ephemeral=True)
        elif custom_id == "cancel":
            self.__view.stop()
            await self.__root.delete()
            return await interaction.response.send_message("Se ha cancelado el envío", ephemeral=True)
        else:
            # Undo
            await self.__root.edit(embed=next(self.__embed))
            return await interaction.response.defer()

    async def launch(self) -> None:
        self.__root = await self.__ctx.send(
            content=f"<@{self.__ctx.author.id}> aquí tienes tu embed personalízalo a tu gusto.",
            embed=self.__embed,
            view=self.__view
        )
