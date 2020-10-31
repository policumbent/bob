# BOB

## Componenti

- sensori
  - ant
  - accelerometer
  - weather
- consumatori
  - csv
  - video
- comunicazione
  - communication => collegamento con il server http
*Work in progress*

## Protocollo

### Comuni (Mqtt)

- publish
  - `states/{name}` => Il sensore pubblica un json `{"connected": True}`quando si connette
  - `settings/{name}` => Un sensore pubblica un json con le sue impostazioni
  - `messages/{name}` => Un sensore pubblica un json con il messaggio che vuole mandare `{"text": "Ciao", "priority": 4, "time": 10, "type": 0}`
- subscribe
  - `new_settings/{name}` => Un sensore effettua la subscribe sulle nuove impostazioni e se arriva un messaggio aggiorna le proprie
  - `signals` =>  Un sensore effettua la subscribe sui segnali, se arriva un segnale il sensore compie la relativa azione `{"action": "reset"}`

### Sensori (MqttSensor => Estende Mqtt)

- publish
  - `sensors/{name}` => Il sensore pubblica i suoi dati

### Consumatori (MqttConsumer => Estende MqttSensor)

- subscribe
  - `sensors/{name}` => I consumatori effettuano la subscription ad una lista di sensori

### Comunicazione (MqttCommunication => Estende MqttConsumer)

- publish
  - `signals` => Manda dei segnali che saranno letti da tutti i sensori `{"action": "reset"}`
  - `new_settings/{name}` => Manda le impostazioni ad ogni sensores
- subscribe
  - settings

### Messaggi (MqttMessages => Estende Mqtt)

- publish
  - `messages` => Pubblica un json con i messaggi da mostrare sulle due righe `{"line_1": "Messaggio riga 1", "line_2": "Messaggio riga 2"}`
- subscribe
  - `messages` => Riceve gli aggiornamenti dai vari sensori
