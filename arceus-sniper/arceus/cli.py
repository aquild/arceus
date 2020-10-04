#!/usr/bin/env python
import os
import sys
import typing
import traceback
from datetime import datetime, timedelta
import json

import click
from PyInquirer import style_from_dict, Token, prompt

from .account import Account
from .snipers import Blocker, Transferrer
from .benchmark import Benchmarker
from .logger import log, log_logo


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


class Config:
    def __init__(self, config_json: dict):
        self.offset: timedelta = timedelta(
            milliseconds=config_json["offset"] if "config" in config_json else 0
        )
        self.attempts: int = config_json["attempts"]
        self.accounts: typing.List[Account] = [
            Account(account["email"], account["password"])
            for account in config_json["accounts"]
        ]


def ask_target() -> str:
    return prompt(
        {
            "type": "input",
            "name": "target",
            "message": "Enter the username you want to block:",
        }
    )["target"]


def ask_config_file() -> str:
    return prompt(
        [
            {
                "type": "input",
                "name": "config_file",
                "message": "Enter path to config file",
                "default": "config.json",
            }
        ]
    )["config_file"]


def auth_fail_prompt():
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


def exit(message: str = None):
    log(message or "Exiting...", "red")
    sys.exit()


@click.group()
def cli():
    pass


@cli.command()
@click.option("-t", "--target", type=str, help="Name to block")
@click.option("-c", "--config", "config_file", type=str, help="Path to config file")
@click.option("-a", "--attempts", type=int, default=20, help="Number of block attempts")
@click.option("-l", "--later", type=int, default=0, help="Days later to snipe")
def block(target: str, config_file: str, attempts: int, later: int):
    log_logo()

    if not target:
        target = ask_target()

    if not config_file:
        config_file = ask_config_file()

    try:
        config = Config({**json.load(open(config_file)), "attempts": attempts})
    except json.JSONDecodeError:
        exit("Config file is not valid JSON! Exiting...")

    log("Verifying accounts...", "yellow")

    auth_fail = False
    for account in config.accounts:
        try:
            account.authenticate()
            if account.get_challenges():
                auth_fail = True
                log(f'Account "{account.email}" is secured', "magenta")
        except:
            auth_fail = True
            traceback.print_exc()
            log(f'Failed to authenticate account "{account.email}"', "magenta")

    if auth_fail:
        auth_fail_prompt()

    try:
        blocker = Blocker(target, config.accounts, offset=config.offset)
        log(f"Setting up blocker...", "yellow")
        blocker.setup(attempts=attempts, later=timedelta(days=later), verbose=True)
    except AttributeError:
        traceback.print_exc()
        exit(message="Getting drop time failed. Name may be unavailable.")

    for account in config.accounts:
        if account.check_blocked(target):
            log(f'Success! Account "{account.email}" blocked target name.', "green")
        else:
            log(
                f'Failure! Account "{account.email}" failed to block target name. 😢',
                "red",
            )

    exit()


@cli.command()
@click.option("-t", "--target", type=str, help="Name to block")
@click.option("-c", "--config", "config_file", type=str, help="Path to config file")
@click.option(
    "-a", "--attempts", type=int, default=100, help="Number of block attempts"
)
@click.option("-l", "--later", type=int, default=0, help="Days later to snipe")
def transfer(target: str, config_file: str, attempts: int, later: int):
    log_logo()

    if not target:
        target = ask_target()

    if not config_file:
        config_file = ask_config_file()

    try:
        config = Config({**json.load(open(config_file)), "attempts": attempts})
    except json.JSONDecodeError:
        exit("Config file is not valid JSON! Exiting...")

    log("Verifying accounts...", "yellow")

    auth_fail = False
    for account in config.accounts:
        try:
            account.authenticate()
            if account.get_challenges():
                auth_fail = True
                log(f'Account "{account.email}" is secured', "magenta")
        except:
            auth_fail = True
            log(f'Failed to authenticate account "{account.email}"', "magenta")

    if auth_fail:
        auth_fail_prompt()

    try:
        transferrer = Transferrer(target, config.accounts, offset=config.offset)
        log(f"Setting up sniper...", "yellow")
        transferrer.setup(attempts=attempts, later=timedelta(days=later), verbose=True)
    except AttributeError:
        traceback.print_exc()
        exit(message="Getting drop time failed. Name may be unavailable.")

    # for account in config.accounts:
    #     if account.check_blocked(target):
    #         log(f'Success! Account "{account.email}" sniped target name.', "green")
    #     else:
    #         log(
    #             f'Failure! Account "{account.email}" failed to snipe target name. 😢',
    #             "red",
    #         )

    exit()


@cli.command()
@click.option(
    "-h",
    "--host",
    type=str,
    default="https://snipe-benchmark.herokuapp.com",
    help="Benchmark API to use",
)
@click.option("-o", "--offset", type=int, default=0, help="Request timing offset")
@click.option("-a", "--attempts", type=int, default=100, help="Number of attempts")
@click.option("-d", "--delay", type=float, default=15)
def benchmark(host: str, offset: int, attempts: int, delay: int):
    log_logo()

    benchmarker = Benchmarker(
        datetime.now() + timedelta(seconds=delay),
        offset=timedelta(milliseconds=offset),
        api_base=host,
    )
    benchmarker.setup(attempts=attempts, verbose=True)

    result = benchmarker.result
    log(f"Results:", "green")
    log(f"Delay: {result['delay']}ms", "magenta")
    requests = result["requests"]
    log(
        f"Requests: {requests['early'] + requests['late']} Total | {requests['early']} Early | {requests['late']} Late",
        "magenta",
    )
    log(f"Requests per second: {requests['rate']}", "magenta")

    exit()


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        exit(message=traceback.format_exc())
