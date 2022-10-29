from discord import Embed, Colour, SelectOption, Button, ButtonStyle
from discord.ext.commands import Context
from discord.ui import View, Button, Select
from typing import Callable, Literal


class MagicEmbed:
    embed_mods = []
    default_embed = Embed(
        title="Your title here",
        description="Your description here",
        color=Colour.from_rgb(255, 0, 110)
    )

    options = Select(
        placeholder="Personaliza tu embed",
        options=[
            SelectOption(label="Titulo", value="title",
                         description="Cambia el titulo del embed", emoji="✒"),
            SelectOption(label="Descripción", value="description",
                         description="Cambia la descripcion del embed", emoji="📝"),
            SelectOption(label="Color", value="color",
                         description="Cambia el color del embed", emoji="🎨"),
            SelectOption(label="Thumbnail", value="thumbnail",
                         description="Cambia el thumbnail del embed", emoji="🖼"),
            SelectOption(label="Imagen", value="image",
                         description="Cambia la imagen del embed", emoji="🖼"),
            SelectOption(label="URL", value="url",
                         description="Cambia la url del embed", emoji="🔗"),
            SelectOption(label="Añade un campo", value="add_field",
                         description="Añade un campo al embed", emoji="➕"),
        ]
    )

    buttons = [
        Button(label="Enviar", style=ButtonStyle.green,
               emoji="✅", custom_id="send"),
        Button(label="Cancelar", style=ButtonStyle.danger,
               emoji="❌", custom_id="cancel"),
        Button(label="Deshacer", style=ButtonStyle.grey,
               emoji="↩", custom_id="undo"),
    ]

    def __init__(self, author_name: str, author_icon: str, footer=Literal["announce", "offer"]):
        self.embed = self.default_embed
        self.embed.set_footer(
            text=f"{('Oferta', 'Anuncio')[footer == 'announce']} enviada por {author_name}",
            icon_url=author_icon
        )

    async def launch(self, ctx, reset, sender: Callable[[Context, Embed], None]):
        view = View()
        view.timeout = (60 * 10)

        self.ctx = ctx
        self.user = ctx.author
        self.reset = reset
        self.sender = sender
        self.options.callback = self.handle_select
        view.add_item(self.options)

        for button in self.buttons:
            button.callback = self.handle_buttons
            view.add_item(button)

        self.root = await ctx.send(
            embed=self.embed,
            view=view,
        )

    async def check_interaction(self, interaction):
        if interaction.user != self.user:
            await interaction.response.send_message(
                "Este no es tu embed",
                ephemeral=True
            )
            return False

        elif self.root.id != interaction.message.id:
            self.reset()
            await interaction.message.delete()
            return False
        return True

    async def handle_select(self, interaction):
        await interaction.response.send_message("Selecciona una opción", ephemeral=True)
        print(interaction.data["values"])

    async def handle_buttons(self, interaction):
        if not await self.check_interaction(interaction):
            return

        custom_id = interaction.data["custom_id"]
        num_of_mods = len(self.embed_mods)

        if custom_id == "send":
            if num_of_mods == 0:

                return await interaction.response.send_message(
                    "No has realizado ninguna modificación",
                    ephemeral=True,
                )

            await self.root.delete()
            return await self.sender(self.ctx, self.embed)

        elif custom_id == "cancel":
            return await self.root.delete()

        else:
            if num_of_mods == 0:
                return await interaction.response.send_message(
                    "No hay modificaciones que deshacer",
                    ephemeral=True
                )

            self.embed = self.embed_mods.pop()
            return await self.root.edit(embed=self.embed)
