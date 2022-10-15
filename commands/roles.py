from discord.ext.commands import Cog, command, has_permissions
from discord.ui import Select, View
from discord import Embed, Colour, SelectOption
from src.utils import Base, MultiDict, link
import json


# Tree commands
class Roles(Base, Cog):
    def __init__(self, bot):
        Base.__init__(self, bot)
        self.messages_id = []
        self.options = MultiDict({ # Create a dictionary of the options for manipulation of the roles
            (*name.split("_"),): func # (append, add, insert) -> self.append_add_insert
            for name, func in self.__class__.__dict__.items() 
            if not name.startswith("_") and "_" in name
        })

        with open("data/roles.json") as file:
            self.roles = json.load(file)
            

    async def append_add_insert(self, ctx, section: str, roles: list = None):
        """
        Añade un rol, o una sección.\n**Sintaxis:**\n```{prefix}roles add <sección: str> <roles: list[role:id]>```\n**Ejemplo:**\n*Crear una sección con roles*\n```{prefix}roles add Nacionalidades España:1234 Mexico:4235 Francia:4356```\n*Crear una sección*\n```{prefix}roles add Idioma```\n*Añadir roles a una sección existente*\n```{prefix}roles add Idioma Español:32454 Inglés:4354```
        """
        embed = Embed() # Create a comunal embed to send
        embed.set_footer(text=f"Comando ejecutado por {ctx.author}", icon_url=ctx.author.avatar.url)
        
        if section in self.roles: 
            if len(roles) > 1:
                roles = {rol[:rol.find(x:=rol.split(":")[-1])]:x for rol in roles} # Create a dictionary of the roles and their ids {role: id}
                self.roles[section]["roles"].update(roles)
                embed.title = f"Roles añadidos a la sección: {section}"
                embed.description = "\n".join( # Create a list of the roles and the new roles
                    [
                        (
                            f"•{rol}",
                            f"•**{rol}** --Rol añadido"
                        )[rol in roles]
                        for rol in self.roles[section]["roles"].keys()
                    ]
                )
                embed.colour = Colour.from_rgb(6, 214, 160)
                await ctx.send(embed=embed)
                return None
            else:
                await ctx.send("No se han proporcionado roles para añadir a la sección")
                return None
        else:
            await ctx.send("Por favor proporciona una descripción para la sección. Si no quieres descripción, escribe `NONE`.")
            event = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            description = event.content if event.content != "NONE" else None
            await event.delete()  # Delete the message
            
            if len(roles) > 1:
                roles = {rol[:rol.find(x:=rol.split(":")[-1])]:x for rol in roles} # Create a dictionary of the roles and their ids {role: id}
                self.roles[section] = {"description": description, "roles": roles} # Create the section
                embed.title = f"Sección creada: {section}"
                embed.description = "\n".join([f"•{rol}" for rol in roles.keys()])
                embed.colour = Colour.from_rgb(6, 214, 160)
                
                await ctx.send(embed=embed)
                return None
            else:
                self.roles[section] = {"roles": {"description": description}}
                embed.title = f"Sección creada: {section}"
                embed.colour = Colour.from_rgb(6, 214, 160)
                
                await ctx.send(embed=embed)
                return None

        
        
        
        
    
    def removed_del_delete(self, section: str, roles: list = None):
        """
        Removes the role(s) from the section, or deletes the section if no roles have been provided to be deleted.
        Parameters
        ----------
        section : `str`
            The section to remove the role from, or the section to delete.
        roles : `list | None` 
            The role(s) to remove from the section.

        Returns
        -------
        `Embed`: The embed to send.
        """
        
    def show_get_view(self, sections: list = "all"):
        """
        Shows the roles in the section, or all the sections if no section has been provided.
        Parameters
        ----------
        section : `list`
            The section to show the roles from, or all the sections.
        
        Returns
        -------
        `Embed`: The embed to send.
        """

    async def publish_post_send(self, ctx, sections: list = None):
        """
        Publishes the section, or all the sections if no section has been provided.
        Parameters
        ----------
        section : `list`
            The section to publish, or all the sections.
        Returns
        -------
            None
        """
        sections = sections or self.roles.keys()
        selects = [
            Select(
                options=[
                    SelectOption(label=section, value="Test")
                ]
            )
        for section in sections]
        
        view = View(*selects)
        await ctx.send("Test", view=view)


    def save(self):
        with open("data/roles.json", "w") as f:
            f.write(json.dumps(self.roles, indent=4))
            
    def update(self):
        """
        Update a message with the new roles.
        Returns
        -------
            None
        """
    
    #?roles instert    
    @has_permissions(manage_roles=True)
    @command(name="roles", aliases=["rol", "r"], description="The roles to add/remove")
    async def roles_command(self, ctx, option=None, *value):
        section, *roles = value or [None] # Get the section and the roles
        func = self.options.get(option) # Get the function to run
        arguments = {
            "self": self,
            "section": section,
            "sections": section.split("&&") if section else "all",
            "roles": roles,
            "ctx": ctx
        }

        if func:
            # Get the arguments for the function
            args = [arguments.get(arg) for arg in func.__code__.co_varnames if arg in arguments]
            await func(*args) # Run the function
        else: 
            embed = Embed(
                title=f"Opción invalida: {option}",
                description="Actualmente solo se pueden usar las siguientes opciones:",
                color=Colour.from_rgb(239, 71, 111),
            )
            [
                embed.add_field(
                    name="-".join(key), 
                    value=func.__doc__, 
                    inline=False
                ) 
            for key, func in self.options.items()]
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text="Comando ejecutado por: " + ctx.author.name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            
setup = lambda bot: link(bot, Roles)
