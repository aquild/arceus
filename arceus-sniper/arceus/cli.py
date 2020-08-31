#!/usr/bin/env python
import os
import sys
import traceback
from datetime import datetime, timedelta
import json

import click
from PyInquirer import style_from_dict, Token, prompt

from .account import Account, InvalidAccountError, RatelimitedError
from .snipers import Blocker, Changer
from .benchmark import Benchmarker
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


@click.group()
def cli():
    pass


@cli.command()
@click.option("-t", "--target", type=str, help="Name to block")
@click.option("-c", "--config", "config_file", type=str, help="Path to config file")
@click.option(
    "-w",
    "--workers",
    type=int,
    default=min(4, os.cpu_count()),
    help="Number of workers",
)
@click.option("-a", "--attempts", type=int, default=20, help="Number of block attempts")
def block(target: str, config_file: str, workers: int, attempts: int):
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
    account = Account(config["account"]["email"], config["account"]["password"])
    if "offset" in config:
        offset = timedelta(milliseconds=config["offset"])
    else:
        offset = timedelta(milliseconds=0)

    log("Verifying accounts...", "yellow")

    try:
        account.authenticate()
        if account.get_challenges():
            auth_fail = True
            log(f'Account "{account.email}" is secured', "magenta")
    except:
        log(f'Failed to authenticate account "{account.email}"', "magenta")
        traceback.print_exc()
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

    try:
        blocker = Blocker(target, account, offset=offset)
        log(f"Setting up blocker...", "yellow")
        blocker.setup(workers, attempts=attempts, verbose=True)
    except AttributeError:
        traceback.print_exc()
        exit(message="Getting drop time failed. Name may be unavailable.")

    if account.check_blocked(target):
        log(f'Success! Account "{account.email}" blocked target name.', "green")
    else:
        log(
            f'Failure! Account "{account.email}" failed to block target name. 😢', "red",
        )

    exit()


@cli.command()
@click.option("-t", "--target", type=str, help="Name to block")
@click.option("-c", "--config", "config_file", type=str, help="Path to config file")
@click.option(
    "-w", "--workers", type=int, default=1, help="Number of workers, EXPERIMENTAL"
)
@click.option(
    "-a", "--attempts", type=int, default=100, help="Number of block attempts"
)
def snipe(target: str, config_file: str, workers: int, attempts: int):
    log("Arceus v1", "yellow", figlet=True)

    if not target:
        target = prompt(
            {
                "type": "input",
                "name": "target",
                "message": "Enter the username you want to snipe:",
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
    account = Account(config["account"]["email"], config["account"]["password"])
    if "offset" in config:
        offset = timedelta(milliseconds=config["offset"])
    else:
        offset = timedelta(milliseconds=0)
    log(f"Offset: {offset.milliseconds}")

    log("Verifying accounts...", "yellow")

    try:
        account.authenticate()
        if account.get_challenges():
            auth_fail = True
            log(f'Account "{account.email}" is secured', "magenta")
    except:
        log(f'Failed to authenticate account "{account.email}"', "magenta")
        traceback.print_exc()
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

    try:
        blocker = Changer(target, account, offset=offset)
        log(f"Setting up sniper...", "yellow")
        blocker.setup(workers, attempts=attempts, verbose=True)
    except AttributeError:
        traceback.print_exc()
        exit(message="Getting drop time failed. Name may be unavailable.")

    if account.check_blocked(target):
        log(f'Success! Account "{account.email}" blocked target name.', "green")
    else:
        log(
            f'Failure! Account "{account.email}" failed to block target name. 😢', "red",
        )

    exit()


@cli.command()
@click.option(
    "-h",
    "--host",
    type=str,
    default="https://snipe-benchmark.herokuapp.com",
    help="Benchmark API to use",
)
@click.option(
    "-w", "--workers", type=int, default=1, help="Number of workers, EXPERIMENTAL"
)
@click.option("-o", "--offset", type=int, default=0, help="Request timing offset")
@click.option("-a", "--attempts", type=int, default=100, help="Number of attempts")
@click.option("-d", "--delay", type=float, default=15)
def benchmark(host: str, workers: int, offset: int, attempts: int, delay: int):
    log("Arceus v1", "yellow", figlet=True)

    benchmarker = Benchmarker(
        datetime.now() + timedelta(seconds=delay),
        offset=timedelta(milliseconds=offset),
        api_base=host,
    )
    benchmarker.setup(workers, attempts=attempts, verbose=True)

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
