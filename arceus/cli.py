#!/usr/bin/env python
import sys
import traceback
import time
from datetime import datetime
import ssl
import json

import click
from PyInquirer import style_from_dict, Token, prompt

from .account import Account, InvalidAccountError, RatelimitedError
from .blocker import Blocker
from .logger import log

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


def exit(message: str = None):
    log(message or "Exiting...", "red")
    sys.exit()


@click.command()
@click.option("-t", "--target", type=str, help="Name to block")
@click.option("-c", "--config", "config_file", type=str, help="Path to config file")
@click.option(
    "-a", "--attempts", type=int, default=100, help="Number of block attempts"
)
def main(target: str, config_file: str, attempts: int):
    log("Arceus v1", "yellow", figlet=True)

    if not target:
        target = prompt(
            {
                "type": "input",
                "name": "target",
                "message": "Enter the username you want to block:",
            }
        )["target"]

    if not config_file:
        config_file = prompt(
            [
                {
                    "type": "input",
                    "name": "config_file",
                    "message": "Enter path to config file",
                    "default": "config.json",
                }
            ]
        )["config_file"]

    config = json.load(open(config_file))
    accounts = [Account(acc["email"], acc["password"]) for acc in config["accounts"]]

    log("Verifying accounts...", "yellow")

    auth_fail = False
    with click.progressbar(accounts) as bar:
        for account in bar:
            try:
                account.authenticate()
                if account.get_challenges():
                    auth_fail = True
                    log(f'Account "{account.email}" is secured', "magenta")
                    accounts.remove(account)
            except:
                traceback.print_exc()
                auth_fail = True
                log(f'Failed to authenticate account "{account.email}"', "magenta")
                traceback.print_exc()
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
    for account in accounts:
        try:
            blocker = Blocker(target, account)
            log(f'Initiating block on account "{account.email}"', "yellow")
            blocker.block(attempts=attempts, verbose=True)

        except AttributeError:
            traceback.print_exc()
            # exit(message="Getting drop time failed. Name may be unavailable.")

    for account in accounts:
        if account.check_blocked(target):
            log(f'Success! Account "{account.email}" blocked target name.', "green")
        else:
            log(
                f'Failure! Account "{account.email}" failed to block target name. 😢',
                "red",
            )

    exit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        exit(message=traceback.format_exc())
