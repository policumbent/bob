from paho.mqtt import client as mqtt

from core.mqtt import Mqtt


class MqttMessage(Mqtt):
    def subscribe(self, client) -> None:
        pass

    def publish(self, message) -> None:
        pass

    def handle_message(self, client, msg: mqtt.MQTTMessage) -> None:
        pass