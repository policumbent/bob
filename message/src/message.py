from threading import Thread
import time

from queue import PriorityQueue


class Message:
    def __init__(self, settings):
        self.trap_info = ""

        self.__settings = settings

        self._running = True
        self.period = 1

        self.RIGA1 = ""
        self.time_RIGA1 = 0
        self.RIGA2 = ""
        self.time_RIGA2 = 0

        self.priority = PriorityQueue()

        self.__worker = Thread(target=self.__run, daemon=True)
        self.__worker.start()

    def __len__(self):
        return len(self.encode())

    def __run(self):
        while self._running:
            time.sleep(1)
            item1 = None
            item2 = None
            # Controllo la coda, se è vuota, ho entrambi i messaggi vuoti
            if not self.priority.empty():
                # tiro fuori il primo elemento
                item1 = self.priority.get()
                self.RIGA1 = item1.mex
                # riduco il tempo rimanente per l'elemento di un secondo
                self.time_RIGA1 = item1.reduce_time()
                # se nella coda ci sono ulteriori elementi li metto nella seconda scritta
                if not self.priority.empty():
                    item2 = self.priority.get()
                    if item2.get_priority() < self.settings.get("trap_priority", MexPriority.low):
                        self.RIGA2 = item2.mex
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

    @property
    def settings(self):
        return self.__settings

    @settings.setter
    def settings(self, s):
        self.__settings = s

    # DEFINIZIONI DI PRIORITA'
    # 1 -> Massima -> Solo per eventi di supergravità (Per il momento la lasciamo inutilizzata)
    # 2 -> Molto alta -> Messaggi da remoto di alta priorità
    # 3 -> Alta -> Messaggi di sistema che richiedono un intervento urgente
    # 4 -> Media -> Messaggi di sistema che non richiedono l'intervento, ma sono utili da sapere
    # 5 -> Bassa -> Messaggi di bassa priorità es. Host non connesso -> ELIMINARLI ALLE ALTE VELOCITA'
    def set(self, mex: str, priority: int = 4, time_m: int = 5, timeout: int = -1):
        item = MexItem(mex, time_m, priority, timeout)
        # if riga == 1:
        #     self.RIGA1 = mex
        #     self.time_RIGA1 = time_m
        # else:
        #     self.RIGA2 = mex
        #     self.time_RIGA2 = time_m
        # print("Sono qua")
        # print(item.to_str())

        self.priority.put(item)

    def get(self, riga=1):
        if riga == 1:
            return self.RIGA1, self.time_RIGA1
        else:
            return self.RIGA2, self.time_RIGA2

    def stop(self):
        if self._running:
            print("Stoping mex refresh")
            self._running = False
            self.__worker.join()

    def to_str(self):
        mex1 = "Mex1: " + self.RIGA1 + \
            " Durata: " + str(self.time_RIGA1) + "\n"
        mex2 = "Mex2: " + self.RIGA2 + \
            " Durata: " + str(self.time_RIGA2) + "\n"
        return mex1 + mex2

    def encode(self):
        return self.RIGA1 + ";" + str(self.time_RIGA1) + ";" + \
            self.RIGA2 + ";" + str(self.time_RIGA2)

    def decode(self, data):
        parts = data.split(";")
        mex = parts[2]
        priority = int(parts[3])
        time_m = int(parts[4])
        self.set(mex, priority, time_m)
        # print(mex, priority, time_m)

    def reduce_all_timeout(self):
        l = list()
        while not self.priority.empty():
            item = self.priority.get()
            item.reduce_timeout()
            # print("Rimosso: ", item.to_str())
            if item.get_timeout() != 0:
                l.append(item)

        for element in l:
            self.priority.put(element)
            # print(element.to_str())

        # for element in self.priority.queue:
        #     element.reduce_timeout()
        #     print(element.to_str())

    def set_trap_info(self, trap_info):
        self.trap_info = trap_info


class MexItem:
    def __init__(self, mex, time_m, priority, timeout):
        self.mex = mex
        self.time_m = time_m
        self.priority = priority
        self.timeout = timeout

    def __cmp__(self, other):
        return self.priority - other.priority

    def __lt__(self, other):
        return self.get_priority() < other.get_priority()

    def reduce_time(self):
        self.time_m -= 1
        return self.time_m

    def to_str(self):
        return self.mex + " T:" + str(self.time_m) + " P:" + str(self.priority) + " Timeout: " + str(self.timeout)

    def get_priority(self):
        return self.priority

    def get_timeout(self):
        return self.timeout

    def reduce_timeout(self):
        if self.timeout > 0:
            self.timeout -= 1
        return

