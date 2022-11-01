import discord
from discord.ext import commands
from src.environment import Environment, Arguments
from src.utils import CommandError
from commands import modules
import time


class Bot(commands.Bot):
    def __init__(self, env: str, case_insensitive: bool, reconnect: bool) -> None:
        self.env = Environment(env)
        self.reconnect = reconnect

        allowed_mentions = discord.AllowedMentions(
            roles=True, everyone=True, users=True
        )

        super().__init__(
            command_prefix=self.env.prefix,
            description=self.env.description,
            allowed_mentions=allowed_mentions,
            intents=discord.Intents.all(),
            case_insensitive=case_insensitive,
            help_command=None
        )

    async def on_ready(self) -> None:
        print(f"\x1b[1;30m{self.time_now}\x1b[0m \x1b[1;32mLOGGED\x1b[0m   \x1b[0;35m{self.user}\x1b[0m (ID: \x1b[0;35m{self.user.id}\x1b[0m) \x1b[1;30m|\x1b[0m Prefix: \x1b[0;35m{self.env.prefix}\x1b[0m \x1b[1;30m|\x1b[0m Connected to: \x1b[0;35m{len(set(self.get_all_members()))} members\x1b[0m \x1b[1;30m|\x1b[0m Connected to: \x1b[0;35m{len(self.guilds)} servers\x1b[0m")

    # async def on_command_error(self, ctx, error) -> None:
    #     if isinstance(error, CommandError):
    #         typed = getattr(error, "typeof", None)
    #         if typed == "embed":
    #             embed = error.embed
    #             embed.set_thumbnail(url=ctx.guild.icon.url)
    #             embed.set_footer(
    #                 text=f"En respuesta a {ctx.author}",
    #                 icon_url=ctx.author.avatar.url
    #             )
    #             await ctx.reply(embed=embed)
    #         else:
    #             await ctx.reply(str(error))
    #     elif isinstance(error, commands.CommandOnCooldown):
    #         await ctx.reply("Este comando está en cooldown, intenta de nuevo en {} segundos.".format(int(error.retry_after)))
    #     else:
    #         raise error

    async def setup_hook(self) -> None:
        print(f"\x1b[1;30m{self.time_now}\x1b[0m \x1b[1;34mINFO\x1b[0m     Loading modules...")
        for module in modules[:]:
            try:
                print("\t" * 3, f"    \x1b[1;30mLOADING\x1b[0m \x1b[0;35m{module}\x1b[0m", end="\r")
                await self.load_extension(module)
                print("\t" * 3, f"    \x1b[1;32mLOADED\x1b[0m   \x1b[0;35m{module}\x1b[0m")
            except Exception as e:
                modules.pop(modules.index(module))
                print("\t" * 3, f"    \x1b[1;31mFAILED\x1b[0m   \x1b[0;35m{module}\x1b[0m \x1b[1;37m(Error:\x1b[0m {e}\x1b[1;37m)\x1b[0m")

        print(f"\x1b[1;30m{self.time_now}\x1b[0m \x1b[1;34mINFO\x1b[0m     Loaded modules: \x1b[0;35m{len(modules)}\x1b[0m")
        await self.tree.sync()
        return await super().setup_hook()

    def run(self) -> None:
        super().run(
            token=self.env.token,
            reconnect=self.reconnect
        )

    time_now: str = property(lambda self: time.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    args = Arguments()
    Bot(**args).run()
