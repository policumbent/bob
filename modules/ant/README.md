# ANT module

## Descrizione

Modulo per acquisizione dati con sensori compatibili [ANT+](https://www.thisisant.com/developer/ant-plus/ant-plus-basics/)

### Sensori

Powermeter SRM

Hall Velocita/Cadenza

Fascia HRM

#### Codici

| Sensore | Bici        | Tipo      | ID         |
| ------- | ----------- | --------- | ---------- |
| Hall    | 🐂 TaurusX  | Velocità  | 24363      |
| Hall    | 🐦 Phoenix  | Velocità  | 4941       |
| Hall    | 🐶 Cerberus | Velocità  | 13583      |
| PM      | 🐂 TaurusX  | PM6 (CTF) | 51321      |
| PM      | 🐦 Phoenix  | PM6 (CTF) | 30636      |
| PM      | 🐶 Cerberus | PM9       | 42941      |
| HRM     | 🐂 TaurusX  | Heartrate | 713908 (?) |
| HRM     | 🐦 Phoenix  | Heartrate | 678224 (?) |
| HRM     | 🐶 Cerberus | Heartrate | 63908      |

### Tabella DB

Nome: `ant`

Campi:

| timestamp                   | speed   | distance | cadence | power   | heartrate |
| --------------------------- | ------- | -------- | ------- | ------- | --------- |
| `str` (core.time.humantime) | `float` | `float`  | `float` | `float` | `float`   |

### Mqtt

Come DB
