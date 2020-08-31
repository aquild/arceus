import requests
import requests_random_user_agent


class InvalidAccountError(Exception):
    pass


class RatelimitedError(Exception):
    pass


class Account:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def authenticate(self):
        res = requests.post(
            "https://authserver.mojang.com/authenticate",
            json={
                "agent": {"name": "Minecraft", "version": 1},
                "username": self.email,
                "password": self.password,
            },
            headers={"Content-Type": "application/json"},
        )

        if res.status_code == 403:
            raise InvalidAccountError
        elif res.status_code == 419:
            raise RatelimitedError
        else:
            json = res.json()
            self.token = json["accessToken"]
            self.uuid = None
            try:
                self.uuid = json["selectedProfile"]["id"]
            except KeyError:
                pass

    def get_challenges(self):
        res = requests.get(
            "https://api.mojang.com/user/security/challenges",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        return res.json()

    def check_blocked(self, target: str):
        res = requests.get(
            f"https://api.mojang.com/user/profile/agent/minecraft/name/{target}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        return res.status_code == 404
