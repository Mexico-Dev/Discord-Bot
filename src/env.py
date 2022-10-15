from os import environ
from dotenv import load_dotenv
from typing import Any


class Environment:
    """Class to load environment variables from a .env file"""

    def __init__(self, env_path: str) -> None:
        """
        Parameters
        ----------
        env_path : str
            Path to the .env file, by default ".env"
        """
        load_dotenv(env_path)
        for key, value in environ.items():
            setattr(self, key.lower(), value)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key, None)
