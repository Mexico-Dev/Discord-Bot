import discord
from discord.ext import commands
from src import Environment, Arguments
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
