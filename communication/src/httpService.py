from .alert import Alert
from .settings import Settings
import requests
import json


class HttpService:
    def __init__(self, settings: Settings):
        self.s = requests.Session()
        self.settings = settings
        self.headers = None
        self.auth()

    def auth(self):
        print(self.settings.base_path + 'authenticate')
        jwt = self.s.post(
            self.settings.base_path + 'authenticate',
            json={
                'username': self.settings.username,
                'password': self.settings.password}
        ).json()
        # token = json.loads(jwt)['token']
        self.headers = {"Authorization": "Bearer {}".format(jwt['token'])}

    def add_bike_data(self, data: dict):
        r = requests.post(
            self.settings.base_path + 'v3/activities',
            json=data,
            headers=self.headers)
        print(r.status_code)
        print(r.text)
        # pass
        # r = self.s.get('https://www.wikipedia.org/')
        # print(r.status_code)

    def get_config(self) -> dict:
        r = requests.get(
            self.settings.base_path + 'v3/bikes/taurusx/config',
            headers=self.headers)
        return r.json()

    def get_weather(self) -> dict:
        pass

    def add_notify(self, message: str):
        pass

    def post_alert(self, alert: Alert) -> None:
        alert_json = alert.values.update({'bike': self.settings.bike})
        requests.post(
            self.settings.base_path + 'v3/alice/alerts',
            json=alert_json,
            headers=self.headers)
