import hashlib
import threading
from typing import List, Tuple
from random import randint
import select
from bluetooth import BluetoothSocket, RFCOMM, advertise_service
import json
import hmac


from .settings import Settings
from .message import Message, MexType, MexPriority
from .alert import Alert, AlertPriority

port = 1
backlog = 3
BUFF = 1024
uuid = "eb60ae08-b17e-11e9-a2a3-2a2ae2dbcce4"


# todo: gestire lock
class NewBt:

    def update_settings(self, settings: dict):
        # with self._settings_lock:
        self.__settings = settings
        self.send_settings(settings)

    def update_signals(self, signals: set):
        # with self._settings_lock:
        self.__signals = list(signals)
        self.send_signals_list(signals)

    def __init__(self, settings: dict, signals: set, key: str,
                 publish_new_settings, send_signal, send_message, send_alert):
        self.__settings: dict = settings
        self.__signals: list = list(signals)
        self.__new_settings = settings
        self.__publish_new_settings = publish_new_settings
        self.__send_signal = send_signal
        self.__send_message = send_message
        self.__send_alert = send_alert
        # self._settings_lock = threading.Lock()
        # self._signals_lock = threading.Lock()
        self._new_update = False

        # variabile per il calcolo del keydigest,
        # viene incrementata ad ogni ricezione,
        # la finestra di accettazione è +1
        # e viene generato casualmente all'avvio
        # dichiaro anche un lock, perchè lo voglio usare/aggiornare in un thread alla volta
        self.__incremental_number: int = randint(0, pow(2, 32)-1)
        self.__incremental_number_lock: threading.Lock = threading.Lock()

        # lista dei client connessi e relativo lock della lista per usarle in scrittura
        # in lettura ogni thread può usarla perchè è l'unico a farlo
        self.__client_list: List[BluetoothSocket] = list()
        self.__client_list_lock: threading.Lock = threading.Lock()

        # lista dei threads attivi
        self._threads_list: List[threading.Thread] = list()

        # chiave per il calcolo del key digest
        self.__key = key

        self._server_sock = BluetoothSocket(RFCOMM)
        self._server_sock.bind(("", 1))
        print("Listen")
        self._server_sock.listen(backlog)
        advertise_service(self._server_sock, "BOB", uuid)
        print("Advertise service")

    def handle(self):
        client_sock, address = self._server_sock.accept()
        # lancio un thread per ogni client, poi quando termina l'esecuzione si chiuderà,
        # si potrebbe gestire in modo asincrono con le select, ma è più complesso
        # sarebbe sensato limitare il numero di thread a x
        thread = threading.Thread(target=self.handle_client, args=(client_sock, address))
        self._threads_list.append(thread)
        thread.start()

    def handle_client(self, client_sock: BluetoothSocket, address):
        self.__client_list.append(client_sock)
        print("Received data from ", address)
        self.send_settings(self.__settings)
        self.send_signals_list(self.__signals)
        try:
            while True:
                data = self.__recv_data(client_sock)
                if len(data) == 0:
                    self.__client_list.remove(client_sock)
                    # esco dal thread se la socket viene chiusa
                print(data.decode('utf-8'))
                self.__handle_data(client_sock, data.decode('utf-8'))
        except Exception as e:
            print(e)
            self.__client_list.remove(client_sock)
        print('chiudo il thread')

    @property
    def incremental_number(self):
        with self.__incremental_number_lock:
            return self.__incremental_number

    def __validate_incremental_number(self, number):
        with self.__incremental_number_lock:
            self.__incremental_number += 1
            print(self.__incremental_number, '==', number)
            return self.__incremental_number == int(number)

    def send_settings(self, settings: dict):
        data = {
            'type': 'settings',
            'data': settings,
            'incremental_number': self.incremental_number
        }
        self.__send_data(data)

    def send_signal(self, signal: str):
        data = {
            'type': 'signal',
            'data': signal,
            'incremental_number': self.incremental_number
        }
        self.__send_data(data)

    def send_signals_list(self, signals: list):
        data = {
            'type': 'signals_list',
            'data': signals,
            'incremental_number': self.incremental_number
        }
        self.__send_data(data)

    def __send_data(self, data: dict):
        # prendo il lock così uso le socket solo per inviare,
        # devo assicurarmi che ci sia un timeout,
        # così sono sicuro di liberare la risorsa dopo un certo periodo
        with self.__client_list_lock:
            for s in self.__client_list:
                # todo: BOB NEW BT: send data
                #  devo ciclare fino a quando manda tutto?
                #  o lo gestisce internamente?
                #  come gestiamo i timeout?
                s.send(json.dumps(data) + '$\n')

    def __handle_data(self, client_socket: BluetoothSocket, data: str):

        # todo: BOB NEW BT: fare controlli sui dati ricevuti
        data = json.loads(data)
        print(type(data['data']))

        # separo il nonce dai dati per la successiva verifica e per l'utilizzo dei dati
        payload = data['data'].split('$$')
        nonce = payload[1]
        payload = payload[0]

        if not self.__validate_key_digest(data['key_digest'], data['data'], nonce):
            print('chiudo la socket')
            client_socket.close()
            return
        if data['type'] == 'signal':
            self.__send_signal(payload)
        elif data['type'] == 'settings':
            print(data['data'])
            payload = json.loads(payload)
            print(payload)
            self.__publish_new_settings(payload)

    # posso ignorare il timeout, tanto sono in un thread dedicato
    # e non ho il problema di dover liberare le risorse
    @staticmethod
    def __recv_data(client_sock: BluetoothSocket):
        # data: bytes = ''.encode('utf-8')
        # while not data.decode('utf-8').__contains__('$\n'):
        #     # ready = select.select([client_sock], [], [], timeout_in_seconds)
        # if ready[0]:
        data = client_sock.recv(BUFF)

        # rimuovo il terminatore '$\n'
        return data[:-2]

    def __validate_key_digest(self, key_digest: str, data: str, nonce: int) -> bool:
        # se non ho una stringa o un dict ritorno falso
        if type(data) != str:
            return False
        key = self.__key.encode('utf-8')
        digest = hmac.new(key, f"{data}".encode('utf-8'), hashlib.sha256)
        print(digest.hexdigest(), 'is valid?? ', digest.hexdigest() == key_digest)
        return digest.hexdigest() == key_digest and self.__validate_incremental_number(nonce)
