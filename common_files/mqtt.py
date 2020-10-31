from typing import List

import paho.mqtt.client as mqtt
import json
import abc

from ..common_files.settings import Settings


class Mqtt:
    def __init__(self,
                 broker_ip: str,
                 port: int,
                 name: str,
                 new_settings_handler):
        self.name = name
        self.new_settings_handler = new_settings_handler
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_log = self.on_log
        self.mqtt_client.connect_async(broker_ip, port, 60)
        self.mqtt_client.loop_start()

    @classmethod
    def on_log(cls, client, userdata, level, buf) -> None:
        """The callback to log all MQTT information"""
        print("\nlog: ", buf)

    @classmethod
    def on_disconnect(cls, client, userdata, msg) -> None:
        """The callback called when user is disconnected from the broker."""
        print("Disconnected from broker")

    def on_connect(self, client, userdata, flags, rc) -> None:
        """The callback for when the client receives a CONNACK response."""
        print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe('new_settings/{}'.format(self.name))
        self.subscribe(client)
        status_topic = 'state/{}'.format(self.name)
        self.mqtt_client.publish(status_topic, json.dumps({"connected": True}), retain=True)

    def on_message(self, client, userdata, msg: mqtt.MQTTMessage) -> None:
        """The callback for when a PUBLISH message is received."""
        print(msg.topic + " " + str(msg.payload))
        if msg.topic == 'new_settings/{}'.format(self.name):
            self.new_settings_handler(msg.payload)
        else:
            self.handle_message(client, msg)

    @abc.abstractmethod
    def subscribe(self, client) -> None:
        pass

    @abc.abstractmethod
    def publish(self, message) -> None:
        pass

    """ Invio i settings del sensore/consumer """
    def publish_settings(self, settings: Settings) -> None:
        status_topic = 'settings/{}'.format(self.name)
        self.mqtt_client.publish(status_topic, settings, retain=True)

    @abc.abstractmethod
    def handle_message(self, client, msg: mqtt.MQTTMessage) -> None:
        pass


class MqttSensor(Mqtt):
    def __init__(self,
                 broker_ip: str,
                 port: int,
                 name: str,
                 signal_handler,
                 new_settings_handler):
        super(MqttSensor, self).__init__(broker_ip, port, name, new_settings_handler)
        self.signal_handler = signal_handler

    """ Un sensore effettua la subscribe alle impostazioni e ai suoi segnali."""
    def subscribe(self, client) -> None:
        client.subscribe('signals/{}'.format(self.name))

    """ Alla ricezione di un messaggio verifico se è un segnale o un'impostazione"""
    def handle_message(self, client, msg: mqtt.MQTTMessage) -> None:
        if msg.topic == 'signals/{}'.format(self.name):
            self.signal_handler(msg.payload)

    """ Invio il dato del sensore """
    def publish(self, message: str) -> None:
        status_topic = 'sensors/{}'.format(self.name)
        self.mqtt_client.publish(status_topic, message, retain=False)

    """ Invio il messaggio del sensore """
    def publish_message(self, message: str) -> None:
        status_topic = 'messages/{}'.format(self.name)
        self.mqtt_client.publish(status_topic, message, retain=False)


class MqttConsumer(Mqtt):
    def __init__(self,
                 broker_ip: str,
                 port: int,
                 name: str,
                 topics: List[str],
                 new_settings_handler,
                 message_handler):
        super(MqttConsumer, self).__init__(broker_ip, port, name, new_settings_handler)
        self.topics = topics
        self.handler = message_handler

    """ Un consumer effettua la subscribe alle impostazioni e ai sensori a cui è interessato."""
    def subscribe(self, client) -> None:
        for topic in self.topics:
            client.subscribe('sensors/{}'.format(topic))

    def publish(self, message) -> None:
        status_topic = 'consumer/{}'.format(self.name)
        self.mqtt_client.publish(status_topic, message, retain=False)

    def handle_message(self, client, msg: mqtt.MQTTMessage) -> None:
        self.handler(msg.topic, msg.payload)


class MqttRemote(Mqtt):
    def __init__(self,
                 broker_ip: str,
                 port: int,
                 name: str,
                 topics: List[str],
                 new_settings_handler,
                 message_handler):
        super(MqttRemote, self).__init__(broker_ip, port, name, new_settings_handler)
        self.topics = topics
        self.handler = message_handler

    """ Un remote controller effettua la subscribe alle impostazioni e ai sensori a cui è interessato."""
    def subscribe(self, client) -> None:
        for topic in self.topics:
            client.subscribe('sensors/{}'.format(topic))

    def publish(self, message) -> None:
        status_topic = 'remote/{}'.format(self.name)
        self.mqtt_client.publish(status_topic, message, retain=False)

    def publish_new_settings(self, message, sensor_name) -> None:
        self.mqtt_client.publish('new_settings/{}'.format(sensor_name), message, retain=False)

    def publish_signal(self, message, sensor_name) -> None:
        self.mqtt_client.publish('signals/{}'.format(sensor_name), message, retain=False)

    def handle_message(self, client, msg: mqtt.MQTTMessage) -> None:
        self.handler(msg.topic, msg.payload)
