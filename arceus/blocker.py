import asyncio
import ssl
from pythonping import ping
import traceback
import pause
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

from .account import Account
from .logger import log


class Spammer:
    def __init__(self, host: str, port: int, payload: bytes, attempts: int = 50):
        self.host = host
        self.port = port
        self.payload = payload
        self.attempts = attempts
        self.conns = []

    async def create_conn(self):
        sc = ssl.create_default_context()
        conn = await asyncio.open_connection(self.host, self.port, ssl=sc)
        self.conns.append(conn)

    async def connect(self):
        await asyncio.gather(
            *(self.create_conn() for _ in range(self.attempts)), return_exceptions=True
        )

    async def spam(self):
        for _reader, writer in self.conns:
            writer.write(self.payload)
        await asyncio.gather(
            *(writer.drain() for _reader, writer in self.conns), return_exceptions=True
        )


def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
        now_timestamp
    )
    return utc_datetime + offset


class Blocker:
    def __init__(
        self,
        target: str,
        account: Account,
        api_host: str = "api.mojang.com",
        api_port: int = 443,
    ):
        self.target = target
        self.account = account
        self.api_host = api_host
        self.api_port = api_port

    def get_drop(self):
        page = requests.get(f"https://namemc.com/search?q={self.target}")
        soup = BeautifulSoup(page.content, "html.parser")
        countdown = soup.find(id="availability-time").attrs["datetime"]
        self.drop_time = datetime_from_utc_to_local(
            datetime.strptime(countdown, "%Y-%m-%dT%H:%M:%S.000Z")
        )

    def get_rtt(self, samples: int = 3):
        res = ping(self.api_host, count=samples)
        self.rtt = timedelta(milliseconds=res.rtt_avg_ms)

    def block(
        self,
        attempts: int = 50,
        keepalive: timedelta = timedelta(seconds=1),
        verbose: bool = False,
    ):
        self.get_rtt()
        self.get_drop()
        log("Waiting for name drop...", "yellow")

        self.account.authenticate()

        pause.until(self.drop_time - timedelta(seconds=10))
        if verbose:
            log("Authenticating...", "yellow")
        self.account.authenticate()
        self.account.get_challenges()  # Necessary to facilitate auth ¯\_(ツ)_/¯
        spammer = Spammer(
            self.api_host,
            self.api_port,
            (
                f"PUT /user/profile/agent/minecraft/name/{self.target} HTTP/1.1\n"
                f"Host: api.mojang.com\n"
                f"Connection: keep-alive\n"
                f"Content-Length: 0\n"
                f"Accept: */*\n"
                f"Authorization: Bearer {self.account.token}\n"
                f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36\n\n"
            ).encode(),
            attempts=attempts,
        )

        pause.until(self.drop_time - keepalive)
        if verbose:
            log(f"Connecting...", "yellow")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(spammer.connect())

        pause.until(self.drop_time - (self.rtt / 2))
        if verbose:
            log(f"Spamming...", "yellow")
        loop.run_until_complete(spammer.spam())
