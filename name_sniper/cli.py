#!/usr/bin/env python
import sys
import traceback

import click
from PyInquirer import style_from_dict, Token, prompt

from account import Account, InvalidAccountError

from pyfiglet import figlet_format

try:
    import colorama

    colorama.init()
except ImportError:
    colorama = None

try:
    from termcolor import colored
except ImportError:
    colored = None

style = style_from_dict(
    {
        Token.Separator: "#cc5454",
        Token.QuestionMark: "#673ab7 bold",
        Token.Selected: "#cc5454",
        Token.Pointer: "#673ab7 bold",
        Token.Instruction: "",
        Token.Answer: "#f44336 bold",
        Token.Question: "",
    }
)


def log(string, color, font="slant", figlet=False):
    if colored:
        if not figlet:
            print(colored(string, color))
        else:
            print(colored(figlet_format(string, font=font), color))
    else:
        print(string)

def exit(message: str = None):
    log(message or 'Exiting...', 'red')
    sys.exit()


@click.command()
@click.option("-c", "--challenge", is_flag=True, default=False)
def main(challenge: bool):
    log("Name Sniper", "yellow", figlet=True)
    questions = [
        {
            "type": "input",
            "name": "target",
            "message": "Enter the username you want to block:",
        },
        {
            "type": "input",
            "name": "accounts",
            "message": 'Enter path to a file with list of accounts in the format "email:password" on each line:',
            "default": "./accounts.txt",
        },
    ]

    answers = prompt(questions)
    target = answers["target"]
    accounts = []
    with open(answers["accounts"]) as f:
        for acc in f.readlines():
            email, passw = acc.rstrip().split(":")
            accounts.append(Account(email, passw))

    log("Verifying accounts", "yellow")

    auth_fail = False
    with click.progressbar(accounts) as bar:
        for account in bar:
            try:
                account.authenticate()
            except:
                auth_fail = True
                log(f'Failed to authenticate account "{account.email}"', "magenta")
                accounts.remove(account)

            if not account.check_security():
                auth_fail = True
                log(f'Account "{account.email}" is secured', "magenta")
                accounts.remove(account)

    if auth_fail:
        if not prompt(
            [
                {
                    "type": "confirm",
                    "message": "One or more accounts failed to authenticate. Continue?",
                    "name": "continue",
                    "default": False,
                }
            ]
        )["continue"]:
            exit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        exit(message=traceback.format_exc())
