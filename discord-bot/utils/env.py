from dotenv import load_dotenv
from os import environ


class Environment:
    def __init__(self) -> None:
        load_dotenv()
        for k, v in environ.items():
            setattr(self, k.lower(), v)
