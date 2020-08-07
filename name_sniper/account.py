import requests
import requests_random_user_agent


class InvalidAccountError(Exception):
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
        else:
            self.token = res.json()["accessToken"]

    def check_security(self):
        res = requests.get(
            "https://api.mojang.com/user/security/challenges",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        return not res.json()

    def block(self, target: str):
        res = requests.post(
            f"https://api.mojang.com/user/profile/agent/minecraft/name/{target}",
            headers={"Authorization": self.token},
        )
        return res.status_code == 204
