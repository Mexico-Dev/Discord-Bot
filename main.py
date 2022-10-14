import discord
from discord.ext import commands
from src import Environment, Arguments, CommandError
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

    async def on_command_error(self, ctx, error) -> None:
        if isinstance(error, CommandError):
            typed = getattr(error, "type", None)
            if typed == "Embed":
                await ctx.reply(embed=error.embed)
            else:
                await ctx.reply(error)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send("Este comando está en cooldown, intenta de nuevo en {} segundos.".format(int(error.retry_after)), delete_after=10)

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
