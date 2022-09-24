from discord.ext.commands import Bot, Cog

# Cogs ------------------------------
Base = type("Base", (object,), {"__init__": lambda self, bot: setattr(self, "bot", bot)}) # Create a base inheritance
def link(bot: Bot, typeof: Cog) -> None: 
    bot.add_cog(typeof(bot))  # Link the cog to the bot

# Roles ------------------------------
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
    