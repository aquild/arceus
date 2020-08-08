import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

from account import Account


class SnipeTimer:
    def __init__(self, target: str):
        self.target = target
        self.get_ping()
        self.get_time()

    def get_ping(self):
        start = datetime.now()
        res = requests.get("https://api.mojang.com")
        self.ping = datetime.now() - start

    def get_time(self):
        page = requests.get(f"https://namemc.com/search?q={self.target}")
        soup = BeautifulSoup(page.content, "html.parser")
        countdown = soup.find(id="availability-time").attrs["datetime"]
        self.time = datetime.strptime(countdown, "%Y-%m-%dT%H:%M:%S.000Z")

        self.time = self.time - self.ping

    def await_name(self, early=30000):
        snipe_time = self.time - timedelta(microseconds=early)
        while datetime.utcnow() < snipe_time:
            time.sleep(0.002)
