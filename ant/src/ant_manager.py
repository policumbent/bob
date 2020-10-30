from threading import Thread

from .ant.easy.channel import Channel
from .ant.easy.node import Node
from .heartrate import HeartRate
from .powermeter import Powermeter
from .speed import Speed

NETWORK_KEY = [0xb9, 0xa5, 0x21, 0xfb, 0xbd, 0x72, 0xc3, 0x45]
CHANNEL_TYPE = Channel.Type.BIDIRECTIONAL_RECEIVE


class Ant:
    def __init__(self, send_mex, hr: HeartRate, speed: Speed, powermeter: Powermeter):
        self.send_mex = send_mex
        self._hr = hr
        self._speed = speed
        self._powermeter = powermeter

        self.node = None
        self._worker_thread = Thread(target=self.setup, daemon=False)
        self._worker_thread.start()

    def __del__(self):
        self.stop()

    def setup(self):
        # TODO: Aggiustare il try-except
        try:
            self.node = Node()
        # TODO: Procurare eccezione
        except Exception as e:
            print(e)
            self.send_mex("ANT NON RILEVATO", 4)
            print("ANT NON RILEVATO")
            return
        # TODO: Aggiustare il try-finally
        try:
            self.node.set_network_key(0x00, NETWORK_KEY)

            # CANALE POTENZA
            channel_powermeter = self.node.new_channel(CHANNEL_TYPE)
            self._powermeter.set_channel(channel_powermeter)

            # CANALE FREQUENZA CARDIACA
            channel_hr = self.node.new_channel(CHANNEL_TYPE)
            self._hr.set_channel(channel_hr)

            # CANALE CADENZA/VELOCITA'
            channel_speed = self.node.new_channel(CHANNEL_TYPE)
            self._speed.set_channel(channel_speed)

            channel_hr.open()
            channel_speed.open()
            channel_powermeter.open()
            print("ANT AVVIATO")

            self.node.start()

        # NOTE: Procurare eccezione
        except Exception as e:
            print(e)
            self.send_mex("ANT NON AVVIATO", 4)
            print("ANT NON AVVIATO")
        finally:
            self.node.stop()

    def restart(self):
        if self.node is not None:
            self.node.stop()
            self.setup()

    def stop(self):
        if self.node is not None:
            self.node.stop()
