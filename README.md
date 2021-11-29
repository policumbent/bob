# BOB
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-4-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

## Componenti

*Work in progress*

Per tutti manca la gestione delle impostazioni

- sensori
  - [x] ant
  - [x] accelerometer
  - [ ] weather => sensori umidità e temperatura a bordo della bici
  - [x] gps
  - [ ] gear => gestione cambio e comunicazione seriale
- consumatori
  - [x] csv
  - [ ] power/speed profiles
  - [x] raspberry manager (cronometro / temperatura cpu)
  - [x] video
- comunicazione
  - [x] gpio => tasti cambio e combinazioni tasti
  - [x] communication => collegamento con il server http
  - [x] pyxbee_v2 => comunicazione tramite lora
  - [x] bt => collegamento con l'app bt  **(manca dockerfile)**
- messaggi
  - [x] messaggi a schermo
  - [ ] alert su alice

## Protocollo

### Comuni (Mqtt)

- publish
  - `states/{name}` => Il sensore pubblica un json `{"connected": True}`quando si connette
  - `settings/{name}` => Un sensore pubblica un json con le sue impostazioni
  - `messages/{name}` => Un sensore pubblica un json con il messaggio che vuole mandare `{"text": "Ciao", "priority": 4, "time": 10, "type": 0}`
  - `alerts/{name}` => Un sensore pubblica un json con il messaggio che vuole mandare `{"text": "Ciao", "priority": 4}`
- subscribe
  - `new_settings/{name}` => Un sensore effettua la subscribe sulle nuove impostazioni e se arriva un messaggio aggiorna le proprie
  - `signals` =>  Un sensore effettua la subscribe sui segnali, se arriva un segnale il sensore compie la relativa azione `{"action": "reset"}`

### Sensori (MqttSensor => Estende Mqtt)

- publish
  - `sensors/{name}` => Il sensore pubblica i suoi dati

### Consumatori (MqttConsumer => Estende MqttSensor)

- subscribe
  - `sensors/{name}` => I consumatori effettuano la subscription ad una lista di sensori

### Comunicazione (MqttRemote => Estende MqttConsumer)

- publish
  - `signals` => Manda dei segnali che saranno letti da tutti i sensori `{"action": "reset"}`
  - `new_settings/{name}` => Manda le impostazioni ad ogni sensores
- subscribe
  - `settings`
  - `alerts`

### Messaggi (MqttMessages => Estende Mqtt)

- publish
  - `messages` => Pubblica un json con i messaggi da mostrare sulle due righe `{"line_1": "Messaggio riga 1", "line_2": "Messaggio riga 2"}`
- subscribe
  - `messages` => Riceve gli aggiornamenti dai vari sensori

## TODO

- [ ] implementare componenti mancanti
- [ ] gestione settings
- [ ] Eliminare moduli inutilizzati
- [ ] Scrivere tutti i README dei singoli moduli
- [ ] Gestire le dipendenze con Poetry
## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/stelosca96"><img src="https://avatars.githubusercontent.com/u/44433696?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Stefano Loscalzo</b></sub></a><br /><a href="https://github.com/policumbent/BOB/commits?author=stelosca96" title="Code">💻</a> <a href="#ideas-stelosca96" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-stelosca96" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
    <td align="center"><a href="https://github.com/davidegavatorta"><img src="https://avatars.githubusercontent.com/u/45601520?v=4?s=100" width="100px;" alt=""/><br /><sub><b>davidegavatorta</b></sub></a><br /><a href="https://github.com/policumbent/BOB/commits?author=davidegavatorta" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/CornagliaRiccardo"><img src="https://avatars.githubusercontent.com/u/81438517?v=4?s=100" width="100px;" alt=""/><br /><sub><b>CornagliaRiccardo</b></sub></a><br /><a href="https://github.com/policumbent/BOB/commits?author=CornagliaRiccardo" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/AlbertoEusebio"><img src="https://avatars.githubusercontent.com/u/72319445?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Alberto Eusebio</b></sub></a><br /><a href="https://github.com/policumbent/BOB/commits?author=AlbertoEusebio" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
