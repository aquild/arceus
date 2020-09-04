from arceus_net import ConnectionManager, TLSConnectionManager
import ssl
from tcp_latency import measure_latency
from urllib.parse import urlparse
import functools
import statistics
import traceback
import pause
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from typing import Union
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
        account: Account,
        offset: timedelta = timedelta(seconds=0),
        api_base: str = "https://api.mojang.com",
    ):
        self.target = target
        self.account = account
        self.offset = offset
        self.api_base = api_base

        parsed = urlparse(self.api_base)
        self.api_host = parsed.hostname
        self.api_port = parsed.port or {"https": 443, "http": 80}[parsed.scheme]
        self.api_ssl = parsed.scheme == "https"

    @property
    @abstractmethod
    def payload(self):
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
        self.get_rtt()
        if later:
            self.get_drop_later(delay=later)
        else:
            self.get_drop()
        log(f"Waiting for name drop on account {self.account.email}...", "yellow")

        pause.until(self.drop_time - timedelta(seconds=10))
        if verbose:
            log("Authenticating...", "yellow")
        self.account.authenticate()
        self.account.get_challenges()  # Necessary to facilitate auth ¯\_(ツ)_/¯

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
        conns.send(self.payload)


class Blocker(Sniper):
    @property
    def payload(self):
        return (
            f"PUT /user/profile/agent/minecraft/name/{self.target} HTTP/1.1\r\n"
            f"Host: api.mojang.com\r\n"
            f"Connection: keep-alive\r\n"
            f"Content-Length: 0\r\n"
            f"Accept: */*\r\n"
            f"Authorization: Bearer {self.account.token}\r\n"
            f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36\r\n\r\n"
        ).encode()


class Transferer(Sniper):
    @property
    def payload(self):
        return (
            f"PUT /user/profile/{self.account.uuid}/name HTTP/1.1\r\n"
            f"Host: api.mojang.com\r\n"
            f"Connection: keep-alive\r\n"
            f"Content-Length: 0\r\n"
            f"Accept: */*\r\n"
            f"Authorization: Bearer {self.account.token}\r\n"
            f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36\r\n\r\n"
        ).encode()
