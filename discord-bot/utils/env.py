from dotenv import load_dotenv
from os import getenv


class Environment:
    def __init__(self) -> None:
        load_dotenv()
        self.discord_token = getenv("DISCORD_TOKEN")
        self.guild = getenv("GUILD")
    