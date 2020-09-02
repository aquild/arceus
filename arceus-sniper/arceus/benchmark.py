from arceus_net import ConnectionManager, TLSConnectionManager
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
        self.api_port = parsed.port or {"https": 443, "http": 80}[parsed.scheme]
        self.api_ssl = parsed.scheme == "https"

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
        attempts: int = 1,
        timeout: timedelta = timedelta(seconds=3),
        verbose: bool = False,
    ):
        if verbose:
            log("Setting up benchmark...", "yellow")
        self.get_rtt()
        requests.post(
            f"{self.api_base}/arceus-v{__version__}",
            json={"time": self.drop_time.timestamp() * 1000},
        )

        conns = (
            TLSConnectionManager(self.api_host, self.api_port, self.api_host)
            if self.api_ssl
            else ConnectionManager(self.api_host, self.api_port)
        )

        pause.until(self.drop_time - timeout)
        if verbose:
            log(f"Connecting...", "yellow")
        start = datetime.now()
        conns.connect(attempts)
        conn_time = datetime.now() - start
        if verbose:
            log(f"Took {conn_time.microseconds / 1000}ms to connect", "magenta")

        pause.until((self.drop_time + self.offset) - (self.rtt / 2))
        if verbose:
            log(f"Spamming...", "yellow")
        start = datetime.now()
        conns.send(self.payload)
        send_time = datetime.now() - start
        if verbose:
            log(f"Took {send_time.microseconds / 1000}ms to spam", "magenta")

    @property
    def result(self):
        return requests.get(f"{self.api_base}/arceus-v{__version__}").json()["result"]
