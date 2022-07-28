# Accelerometer module

### Description

Modulo per acquisizione dati con accelerometro e giroscopio

#### Sensore

MPU6050

Frequenza di acquisizione: 1KHz

NOTE: Bisogna aggiungere al file `config.txt` del raspberry sotto `[all]`

```
dtparam=i2c_arm=on
i2c_arm_baudrate=400000
```

#### Tabella DB

Nome: `accelerometer`

Campi:

| timestamp                   | acc_x   | acc_y   | acc_z   | gyr_x   | gyr_y   | gyr_z   |
| --------------------------- | ------- | ------- | ------- | ------- | ------- | ------- |
| `str` (core.time.humantime) | `float` | `float` | `float` | `float` | `float` | `float` |

#### Mqtt

WIP
