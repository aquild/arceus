from pyfiglet import figlet_format
from . import __version__

try:
    import colorama

    colorama.init()
except ImportError:
    colorama = None

try:
    from termcolor import colored
except ImportError:
    colored = None


def log(string, color, font="slant", figlet=False):
    if colored:
        if not figlet:
            print(colored(string, color))
        else:
            print(colored(figlet_format(string, font=font), color))
    else:
        print(string)


def log_logo():
    log(f"Arceus v{__version__.split('.')[0]}", "yellow", figlet=True)
