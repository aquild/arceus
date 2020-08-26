import asyncio
import multiprocessing
import requests
import functools
from urllib.parse import urlparse
import pause
from datetime import datetime, timedelta

from . import __version__
from .snipers import Sniper
from .logger import log


class Benchmarker(Sniper):
    def __init__(
        self,
        time: datetime,
        offset: timedelta = timedelta(seconds=0),
        api_base: str = "https://snipe-benchmark.herokuapp.com",
    ):
        self.drop_time = time
        self.offset = offset
        self.api_base = api_base

        parsed = urlparse(self.api_base)
        self.api_host = parsed.hostname
        self.api_port = parsed.port or 443

    @property
    def payload(self):
        return (
            f"GET /arceus-v{__version__}/snipe HTTP/1.1\r\n"
            f"Host: {self.api_host}\r\n"
            f"Content-Length: 0\r\n"
            f"Accept: */*\r\n"
            f"User-Agent: Arceus v1\r\n\r\n"
        ).encode()

    def setup(
        self,
        workers,
        attempts: int = 1,
        keepalive: timedelta = timedelta(seconds=1),
        verbose: bool = False,
    ):
        if verbose:
            log("Setting up benchmark...", "yellow")
        self.get_rtt()
        requests.post(
            f"{self.api_base}/arceus-v{__version__}",
            json={"time": self.drop_time.timestamp() * 1000},
        )

        with multiprocessing.Pool() as pool:
            log(f"Spawning workers...", "yellow")

            pool.map(
                functools.partial(self.snipe, verbose="True", ssl=self.api_port == 443),
                [attempts] * workers,
            )

    @property
    def result(self):
        return requests.get(f"{self.api_base}/arceus-v{__version__}").json()["result"]
