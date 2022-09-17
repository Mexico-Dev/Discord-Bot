from discord import Embed, Colour
from discord.ext.commands import Bot, Cog
import re


def link(bot: Bot, typeof: Cog) -> None:
    bot.add_cog(typeof(bot))

def embedTemp(template: dict, dependencies: dict = None) -> Embed:
    """
    Creates an embed from a template.

    Parameters
    ----------
    template: `dict`
        The template to use.

    dependencies: `dict`
        The dependencies to use.
    """

    # Error handling
    if not template: # If the template is null
        raise ValueError("\x1b[1;33mTemplate\x1b[0m cannot be \x1b[1;31mnull and void\x1b[0m.")
    elif not isinstance(template, dict): # If the template is not a dictionary
        raise TypeError("\x1b[1;33mTemplate\x1b[0m must be a \x1b[1;30mdictionary\x1b[0m.")
    elif dependencies and not isinstance(dependencies, dict): # If the dependencies is not a dictionary
        raise TypeError("\x1b[1;33mDependencies\x1b[0m must be a \x1b[1;30mdictionary\x1b[0m.")

    # Resolve dependencies
    regex = r"{(.*?)}"  # Regex to find dependencies
    dependencies_keys = dependencies.keys() if dependencies else []  # List of dependencies keys
    def resolve(match: list[str], value: str) -> str:
        """
        Resolves dependencies.
        
        Remplaces the dependency with the value.

        Parameters
        ----------
        match: `list[str]`
            The match of the regex.
        value: `str`
            The value to use.
        
        Returns
        -------
        `str`: The resolved value.
        """
        # For each in the match dependencies
        for match_key in set(match): 
            
            # If the dependency not exists in the dependencies, raise an error
            if not match_key in dependencies_keys: 
                raise ValueError(f"\x1b[1;33mDependency\x1b[0m \x1b[1;34m{match_key}\x1b[0m \x1b[1;31mnot found\x1b[0m.")
            
            # Replace the dependency with the value 
            value = value.replace("{" + match_key + "}", str(dependencies[match_key]))
        return value


    # Resolve the template
    # For each in the template
    for key, value in template.items():  
             
        # If the value is a string
        if isinstance(value, str):
            if match := re.findall(regex, value): # If the value contains dependencies to resolve
                value = resolve(match, value)  # Resolve the value 
                template[key] = value # Replace the value with the resolved value
        
        # If the value is a dictionary
        elif isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, str):
                    if match:=re.findall(regex, v):
                        value[k] = resolve(match, v) 
            template[key] = value 
        
        # If the value is a list
        elif isinstance(value, list): 
            if key == "fields": 
                for field in range(len(value)): 
                    if isinstance(value[field], dict): 
                        for k, v in value[field].items(): 
                            if isinstance(v, str):
                                if match:=re.findall(regex, v):
                                    value[field][k] = resolve(match, v) 
                
            elif key == "color":
                if len(value) == 3: template[key] = Colour.from_rgb(*value)
                else : raise ValueError("The \x1b[1;30mformat\x1b[0m of the color \x1b[1;31mnot is correct\x1b[0m.")
            else: raise ValueError(f"\x1b[1;33mKey\x1b[0m \x1b[1;31m{key}\x1b[0m \x1b[1;33mnot supported\x1b[0m.")
    
    
    embed = Embed()
    
    if "title" in template: embed.title = template["title"]
    if "description" in template: embed.description = template["description"]
    if "color" in template: embed.colour = template["color"]
    if "thumbnail" in template: embed.set_thumbnail(url=template["thumbnail"])
    if "footer" in template: embed.set_footer(**template["footer"])
    if "image" in template: embed.set_image(url=template["image"])
    if "fields" in template: [embed.add_field(**field) for field in template["fields"]]
    if "author" in template: embed.set_author(**template["author"])
    
    return embed


