import argparse

ARGS = {
    "env": [
        ["-e", "--env"],
        {
            "required": False,
            "help": "Environment to deploy to",
            "default": ".env"
        }
    ],
    "case-insensitive": [
        ["-ci", "--case-insensitive"],
        {
            "required": False,
            "help": "Whether or not the bot should be case insensitive",
            "default": True
        }
    ],
    "reconnect": [
        ["-r", "--reconnect"],
        {
            "required": False,
            "help": "Whether or not the bot should reconnect on disconnect",
            "default": True
        }
    ]
}


class Arguments(dict):
    """ With this class, you can get the arguments from the command line"""

    def __init__(self) -> None:
        """
        Input: `main.py -e .env -ci True -r True` (CMD)
        ------
        Returns: `{"env": ".env", "case-insensitive": True, "reconnect": True}`
        -------
        """
        options = argparse.ArgumentParser()
        for arg in ARGS:
            options.add_argument(*ARGS[arg][0], **ARGS[arg][1])
        args = options.parse_args()

        super().__init__(vars(args))
