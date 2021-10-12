from typing import List
import paho.mqtt.client as mqtt
import json
import abc
from .common_settings import CommonSettings
from .message import Message
from .alert import Alert


class Mqtt:
    def __init__(
            self,
            broker_ip: str,
            port: int,
            name: str,
            signal_list: List[str],
            settings: CommonSettings,
            message_handler
    ):
        self.name = name
        self.settings = settings
        self.message_handler = message_handler
        self.signal_list = signal_list
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_log = self.on_log
        status_topic = 'state/{}'.format(self.name)
        self.mqtt_client.will_set(status_topic, json.dumps({"connected": False}), retain=True)
        self.mqtt_client.connect_async(broker_ip, port, 60)
        self.mqtt_client.loop_start()

    @classmethod
    def on_log(cls, client, userdata, level, buf) -> None:
        pass
        """The callback to log all MQTT information"""
        # print("\nlog: ", buf)

    @classmethod
    def on_disconnect(cls, client, userdata, msg) -> None:
        print("Disconnected")
        """The callback called when user is disconnected from the broker."""
        print("Disconnected from broker")

    def on_connect(self, client, userdata, flags, rc) -> None:
        """ The callback for when the client receives a CONNACK response. """
        print("Connected with result code", str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe('new_settings')
        client.subscribe('signals')
        client.subscribe('sensors/manager')
        self.subscribe(client)

        """ Il sensore pubblica un json `{"connected": True}`quando si connette """
        status_topic = 'state/{}'.format(self.name)
        self.mqtt_client.publish(status_topic, json.dumps({"connected": True}), retain=True)
        self.publish_settings(self.settings)
        self.publish_signals_list(self.signal_list)

    def on_message(self, client, userdata, msg: mqtt.MQTTMessage) -> None:
        """The callback for when a PUBLISH message is received."""
        # print(msg.topic + " " + str(msg.payload))
        if msg.topic == 'new_settings'.format(self.name):
            try:
                if self.settings.new_settings(json.loads(msg.payload)):
                    self.publish_settings(self.settings)
                    self.message_handler('signals', 'settings_updated'.encode('utf-8'))
            except Exception as e:
                print(e)
        else:
            self.handle_message(client, msg)

    @abc.abstractmethod
    def subscribe(self, client) -> None:
        pass

    @abc.abstractmethod
    def publish(self, message) -> None:
        pass

    """ Invio i settings del sensore/consumer """
    def publish_settings(self, settings: CommonSettings) -> None:
        self.settings = settings
        status_topic = 'settings/{}'.format(self.name)
        self.mqtt_client.publish(status_topic, json.dumps(settings.values), retain=True)

    """ Invio la lista dei signal del sensore/consumer """
    def publish_signals_list(self, signal_list: List[str]) -> None:
        self.signal_list = signal_list
        status_topic = 'signals_list/{}'.format(self.name)
        self.mqtt_client.publish(status_topic, str(signal_list), retain=True)

    """ > Un sensore pubblica un json con il messaggio che vuole mandare """
    def publish_message(self, message: Message) -> None:
        status_topic = 'messages/{}'.format(self.name)
        self.mqtt_client.publish(status_topic, json.dumps(message.values), retain=True)

    """ > Un sensore pubblica un json con l'alert che vuole mandare """
    def publish_alert(self, message: Alert) -> None:
        status_topic = 'alerts/{}'.format(self.name)
        self.mqtt_client.publish(status_topic, json.dumps(message.values), retain=True)

    """ Gestisco i risultati delle subscribe"""
    def handle_message(self, client, msg: mqtt.MQTTMessage) -> None:
        self.message_handler(msg.topic, msg.payload)


class MqttSensor(Mqtt):
    """ Un sensore effettua la subscribe alle impostazioni e ai suoi segnali."""
    def subscribe(self, client) -> None:
        pass

    """ Invio il dato del sensore """
    def publish(self, message: str) -> None:
        status_topic = 'sensors/{}'.format(self.name)
        self.mqtt_client.publish(status_topic, message, retain=False)


class MqttConsumer(MqttSensor):
    def __init__(self,
                 broker_ip: str,
                 port: int,
                 name: str,
                 topics: List[str],
                 signal_list: List[str],
                 settings: CommonSettings,
                 message_handler):
        super(MqttConsumer, self).__init__(broker_ip, port, name, signal_list, settings, message_handler)
        self.topics = topics

    """ Un consumer effettua la subscribe alle impostazioni e ai sensori a cui è interessato."""
    def subscribe(self, client) -> None:
        for topic in self.topics:
            if topic == "messages":
                client.subscribe('messages')
            else:
                client.subscribe('sensors/{}'.format(topic))

    def subscribe_messages(self):
        print(str(self.mqtt_client))
        self.mqtt_client.subscribe('messages')


class MqttRemote(MqttConsumer):
    def __init__(self,
                 broker_ip: str,
                 port: int,
                 name: str,
                 topics: List[str],
                 signal_list: List[str],
                 settings: CommonSettings,
                 message_handler):
        super(MqttRemote, self).__init__(broker_ip, port, name, topics, signal_list, settings, message_handler)

    """ Un remote controller effettua la subscribe alle impostazioni,
     ai sensori a cui è interessato e alle notifiche."""
    def subscribe(self, client) -> None:
        super().subscribe(client)
        client.subscribe('settings/#')
        client.subscribe('alerts/#')
        client.subscribe('signals_list/#')

    def publish_signal(self, signal: str) -> None:
        status_topic = 'signals'
        self.mqtt_client.publish(status_topic, signal, retain=False)

    def publish_new_settings(self, message: dict) -> None:
        self.mqtt_client.publish('new_settings', json.dumps(message), retain=False)

    def handle_message(self, client, msg: mqtt.MQTTMessage) -> None:
        self.message_handler(msg.topic, msg.payload)

    """ Invio il dato del sensore remoto"""
    def publish_data(self, sensor_name: str, message: str) -> None:
        status_topic = 'sensors/{}'.format(sensor_name)
        self.mqtt_client.publish(status_topic, message, retain=False)


class MqttMessage(Mqtt):
    """ Un sensore effettua la subscribe alle impostazioni e ai suoi segnali."""
    def subscribe(self, client) -> None:
        client.subscribe('messages/#')

    """ Invio il dato del sensore """
    def publish(self, message: dict) -> None:
        status_topic = 'messages'
        self.mqtt_client.publish(status_topic, json.dumps(message), retain=False)

