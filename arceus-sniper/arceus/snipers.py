from arceus_net import ConnectionManager, TLSConnectionManager
from tcp_latency import measure_latency
from urllib.parse import urlparse
import statistics
import pause
import time
from datetime import datetime, timedelta
import requests
import json
from bs4 import BeautifulSoup
import typing
from abc import ABC, abstractmethod

from .account import Account
from .logger import log


def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
        now_timestamp
    )
    return utc_datetime + offset


class Sniper(ABC):
    def __init__(
        self,
        target: str,
        accounts: typing.List[Account],
        offset: timedelta = timedelta(seconds=0),
        api_base: str = "https://api.mojang.com",
    ):
        self.target = target
        self.accounts = accounts
        self.offset = offset
        self.api_base = api_base

        parsed = urlparse(self.api_base)
        self.api_host = parsed.hostname or "api.mojang.com"
        self.api_port = parsed.port or {"https": 443, "http": 80}[parsed.scheme]
        self.api_ssl = parsed.scheme == "https"

    @property
    @abstractmethod
    def payloads(self):
        """Get payloads to send"""
        pass

    def get_drop(self):
        page = requests.get(f"https://namemc.com/search?q={self.target}")
        soup = BeautifulSoup(page.content, "html.parser")
        countdown = soup.find(id="availability-time").attrs["datetime"]
        self.drop_time = datetime_from_utc_to_local(
            datetime.strptime(countdown, "%Y-%m-%dT%H:%M:%S.000Z")
        )

    def get_drop_later(self, delay=timedelta(days=1)):
        page = requests.get(f"https://namemc.com/search?q={self.target}")
        soup = BeautifulSoup(page.content, "html.parser")
        countdown = soup.find_all("time")[1].attrs["datetime"]
        change_time = datetime_from_utc_to_local(
            datetime.strptime(countdown, "%Y-%m-%dT%H:%M:%S.000Z")
        )
        self.drop_time = change_time + timedelta(days=37) + delay

    def get_rtt(self, samples: int = 5):
        latency = measure_latency(host=self.api_host, port=self.api_port, runs=samples)
        self.rtt = timedelta(milliseconds=statistics.mean(latency))

    def setup(
        self,
        attempts: int = 1,
        timeout: timedelta = timedelta(seconds=3),
        later: timedelta = timedelta(seconds=0),
        verbose: bool = False,
    ):
        attempts *= len(self.accounts)

        self.get_rtt()
        if later:
            self.get_drop_later(delay=later)
        else:
            self.get_drop()
        log(f"Waiting for name drop...", "yellow")

        pause.until(self.drop_time - timedelta(seconds=30))
        if verbose:
            log("Authenticating...", "yellow")
        for account in self.accounts:
            account.authenticate()
            account.get_challenges()  # Necessary to facilitate auth ??\_(???)_/??

        conns = (
            TLSConnectionManager(self.api_host, self.api_port, self.api_host)
            if self.api_ssl
            else ConnectionManager(self.api_host, self.api_port)
        )

        pause.until(self.drop_time - timeout)
        if verbose:
            log(f"Connecting...", "yellow")
        conns.connect(attempts)

        pause.until((self.drop_time + self.offset) - (self.rtt / 2))
        if verbose:
            log(f"Spamming...", "yellow")
        start = datetime.now()
        conns.send(self.payloads)
        send_time = datetime.now() - start
        if verbose:
            log(
                f"Took {send_time.microseconds / 1000}ms ({attempts / send_time.microseconds * 1_000_000} requests per second).",
                "magenta",
            )


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"


class Blocker(Sniper):
    @property
    def payloads(self):
        return [
            "\r\n".join(
                (
                    f"PUT /user/profile/agent/minecraft/name/{self.target} HTTP/1.1",
                    "Host: api.mojang.com",
                    "Connection: keep-alive",
                    "Content-Length: 0",
                    "Accept: */*",
                    f"Authorization: Bearer {account.token}",
                    f"User-Agent: {USER_AGENT}",
                    # Body
                    "",
                    ""
                )
            ).encode()
            for account in self.accounts
        ]


class Transferrer(Sniper):
    @property
    def payloads(self):
        return [
            "\r\n".join(
                (
                    f"POST /user/profile/{account.uuid}/name HTTP/1.1",
                    "Host: api.mojang.com",
                    "Connection: keep-alive",
                    "Content-Type: application/json",
                    "Accept: */*",
                    f"Authorization: Bearer {account.token}",
                    f"User-Agent: {USER_AGENT}",
                    "",
                    f'{json.dumps({"name": self.target, "password": account.password})}',
                    ""
                )
            ).encode()
            for account in self.accounts
        ]
