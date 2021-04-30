from threading import Thread
import time

from queue import PriorityQueue
from .common_files.message import MexPriority, Message, MexType


class Messages:
    def __init__(self, settings):
        self.trap_info = ""
        self.__settings = settings

        self.RIGA1 = ""
        self.time_RIGA1 = 0
        self.RIGA2 = ""
        self.time_RIGA2 = 0

        self.priority = PriorityQueue()
        # self.__run()
        # self.__worker = Thread(target=self.__run, daemon=True)
        # self.__worker.start()

    # def __len__(self):
    #     return len(self.encode())

    def get_values(self) -> dict:
        item1 = None
        item2 = None
        # Controllo la coda, se è vuota, ho entrambi i messaggi vuoti
        if not self.priority.empty():
            # tiro fuori il primo elemento
            item1 = self.priority.get()
            self.RIGA1 = item1.text
            # riduco il tempo rimanente per l'elemento di un secondo
            self.time_RIGA1 = item1.reduce_time()
            # se nella coda ci sono ulteriori elementi li metto nella seconda scritta
            if not self.priority.empty():
                item2 = self.priority.get()
                if item2.get_priority() > self.settings.trap_priority:
                    self.RIGA2 = item2.text
                    self.time_RIGA2 = item2.reduce_time()
                else:
                    self.RIGA2 = self.trap_info
            else:
                self.RIGA2 = self.trap_info
        else:
            self.RIGA1 = self.trap_info
            self.RIGA2 = ""
        # if item1 is not None:
        #     print(item1.to_str())
        # if item2 is not None:
        #     print(item2.to_str())
        # se un elemento ha ancora del tempo rimanente per essere visualizzato lo riaggiungo alla coda
        if item1 is not None:
            if self.time_RIGA1 > 0 and int(item1.get_timeout()) != 0:
                self.priority.put(item1)
        if item2 is not None:
            if self.time_RIGA2 > 0 and int(item2.get_timeout()) != 0:
                self.priority.put(item2)
        self.reduce_all_timeout()
        return {
            'line_1': self.RIGA1,
            'line_2': self.RIGA2
        }

    @property
    def settings(self):
        return self.__settings

    @settings.setter
    def settings(self, s):
        self.__settings = s

    # DEFINIZIONI DI PRIORITA'
    # 5 -> Massima -> Solo per eventi di supergravità (Per il momento la lasciamo inutilizzata)
    # 4 -> Molto alta -> Messaggi da remoto di alta priorità
    # 3 -> Alta -> Messaggi di sistema che richiedono un intervento urgente
    # 2 -> Media -> Messaggi di sistema che non richiedono l'intervento, ma sono utili da sapere
    # 1 -> Bassa -> Messaggi di bassa priorità es. Host non connesso -> ELIMINARLI ALLE ALTE VELOCITA'
    def set(self, item: Message):
        if item.message_type == MexType.default:
            self.priority.put(item)
        if item.message_type == MexType.trap:
            self.set_trap_info(item)

    def get(self, riga=1):
        if riga == 1:
            return self.RIGA1, self.time_RIGA1
        else:
            return self.RIGA2, self.time_RIGA2

    def to_str(self):
        mex1 = "Mex1: " + self.RIGA1 + \
               " Durata: " + str(self.time_RIGA1) + "\n"
        mex2 = "Mex2: " + self.RIGA2 + \
               " Durata: " + str(self.time_RIGA2) + "\n"
        return mex1 + mex2

    def encode(self):
        return self.RIGA1 + ";" + str(self.time_RIGA1) + ";" + \
               self.RIGA2 + ";" + str(self.time_RIGA2)

    def reduce_all_timeout(self):
        l = list()
        while not self.priority.empty():
            item = self.priority.get()
            item.reduce_timeout()
            if item.get_timeout() != 0:
                l.append(item)

        for element in l:
            self.priority.put(element)

    def set_trap_info(self, item: Message):
        self.trap_info = item.text
