import asyncio
import requests
from tcp_latency import measure_latency
import statistics
from urllib.parse import urlparse
import pause
from datetime import datetime, timedelta

from . import __version__
from .snipers import SocketManager
from .logger import log


class Benchmarker:
    def __init__(
        self, time: datetime, api_base: str = "https://snipe-benchmark.herokuapp.com"
    ):
        self.time = time
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

    def get_rtt(self, samples: int = 5):
        latency = measure_latency(host=self.api_host, port=self.api_port, runs=samples)
        self.rtt = timedelta(milliseconds=statistics.mean(latency))

    def benchmark(
        self,
        attempts: int = 100,
        keepalive: timedelta = timedelta(seconds=1),
        verbose: bool = False,
    ) -> int:
        self.get_rtt()

        if verbose:
            log("Setting up benchmark...", "yellow")
        requests.post(
            f"{self.api_base}/arceus-v{__version__}",
            json={"time": self.time.timestamp() * 1000},
        )
        sockets = SocketManager(
            self.api_host,
            self.api_port or 443,
            self.payload,
            attempts=attempts,
            ssl=self.api_port == 443,
        )

        pause.until(self.time - keepalive)
        if verbose:
            log(f"Connecting...", "yellow")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(sockets.connect())

        pause.until(self.time - (self.rtt / 2))
        if verbose:
            log(f"Spamming...", "yellow")
        loop.run_until_complete(sockets.spam())

        with requests.get(f"{self.api_base}/arceus-v{__version__}") as r:
            return r.json()["delay"]
