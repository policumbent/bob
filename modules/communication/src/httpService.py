from typing import Dict, List

from core.alert import Alert
from .settings import Settings
from core.weatherData import WeatherData
import requests
import json


class HttpService:
    def __init__(self, settings: Settings):
        self.s = requests.Session()
        self.settings = settings
        self.headers = None
        self.auth()

    def auth(self) -> bool:
        print(self.settings.base_path + 'authenticate')
        try:
            jwt = self.s.post(
                self.settings.base_path + 'authenticate',
                json={
                    'username': self.settings.username,
                    'password': self.settings.password}
            ).json()
            # token = json.loads(jwt)['token']
            self.headers = {"Authorization": "Bearer {}".format(jwt['token'])}
            return True
        except Exception as e:
            print(e)
            return False

    def add_bike_data(self, data: dict):
        if self.headers is None:
            if not self.auth():
                return
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
        if self.headers is None:
            if not self.auth():
                return {}
        r = requests.get(
            self.settings.base_path + 'v3/bikes/taurusx/config',
            headers=self.headers)
        return r.json()

    def get_weather(self) -> Dict[int, WeatherData]:
        if self.headers is None:
            if not self.auth():
                return dict()
        r = requests.get(
            self.settings.base_path + 'v3/weather/last',
            headers=self.headers)
        # print(r.status_code)
        # print(r.json())
        weather_data_list: dict = dict()
        # creo un dizionario con chiave l'id della stazione
        # e per valore il dato della stazione
        for ws in r.json():
            wd = WeatherData(ws)
            weather_data_list[wd.station_id] = wd.to_json()
        return weather_data_list

    def add_notify(self, message: str):
        pass

    def post_alert(self, alert: Alert) -> None:
        alert_json = alert.values.update({'bike': self.settings.bike})
        requests.post(
            self.settings.base_path + 'v3/alice/alerts',
            json=alert_json,
            headers=self.headers)
