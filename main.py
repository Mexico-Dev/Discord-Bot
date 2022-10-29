import discord
from discord.ext import commands
from src.environment import Environment, Arguments
from src.utils import CommandError
from commands import modules


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
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

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
        for module in modules:
            await self.load_extension(module)

        await self.tree.sync()
        return await super().setup_hook()

    def run(self) -> None:
        super().run(
            token=self.env.token,
            reconnect=self.reconnect
        )


if __name__ == "__main__":
    args = Arguments()
    Bot(**args).run()
