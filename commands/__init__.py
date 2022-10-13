from os import listdir

# __path__ = "<absolute_path>\\Discord-Bot\\commands"
# __package__ = "commands"

modules = [
    # Remove the .py extension (main.py -> main) and concatenate the package name (commands.main).
    f"{__package__}.{f[:-3]}"
    # Iterate over the files in the directory ("commands").
    for f in listdir(*__path__)
    # If the file is a python file and not a special file.
    if f.endswith(".py") and not f.startswith("__")
]
