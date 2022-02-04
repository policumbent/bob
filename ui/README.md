# bob service controller
Control systemd services through Web or REST API\
Source: https://github.com/ogarcia/sysdweb

## Installation

### Prerequisites

If you are a Ubuntu/Debian user you need to install `libsystemd-dev`, for
CentOS users the package is `systemd-devel`.


```sh
poetry install
sudo ufw allow 8080
poetry run  python3 sysdweb.py -p 8080 -l 0.0.0.0 -c sysdweb.conf
```
to activate as a service 
````sh
sudo cp ./systemd/sysdweb-system.service /etc/systemd/system/sysdweb-system.service
sudo systemctl enable sysdweb-system
sudo systemctl start sysdweb-system
````

## Run

First take a look to `sysdweb.conf` file to configure sysdweb. Is self
explanatory.


Once you have configured sysdweb, simply run.

```
poetry run python3 sysdweb.py 
```

Change listen port and address with `-p` and `-l` or via environment variables.

```sh
poetry run python3 sysdweb.py -p 8080 -l 0.0.0.0 -c sysdweb.conf
```

Current config environment variables are the following.

| Variable | Description |
| --- | --- |
| `SYSDWEB_CONFIG` | Config file location |
| `SYSDWEB_HOST` | Listen address |
| `SYSDWEB_PORT` | Listen port |
| `SYSDWEB_LOGLEVEL` | Log level, effective values are `WARNING`, `INFO` and `DEBUG` |

## API

You can control configured services via REST API, for example, with curl.\
You can also use a basic web interface at http:/<ip>:5001/

The API endpoint is `/<service>/<action>`, always `GET` and response
a json with following format.

```json
{
  "<action>": "<result>"
}
```

The `<service>` tag is defined in config file and match with section label.
For example, in following config, the service would be `csv`.

```ini
[csv]
title = CSV
unit = csv.service
```

The posible `<actions>` are.

* start
* stop
* restart
* reload
* reloadorrestart
* status
* journal
* enabled
* enable
* disable

All actions (except `status`, `journal` and `enabled`) return as result `OK` if can
communicate with DBUS or `Fail` if any error occurs.

For `status` action, the possible responses are.

* active (started unit)
* reloading
* inactive (stopped unit)
* failed (stopped unit)
* activating
* deactivating
* not-found (for inexistent unit)

For `enabled` query, the possible responses are.

* enabled
* disabled

By default `/<service>/journal` returns 100 tail lines of journal
file of `<service>` unit. You can specify the number of lines by this way.

```
/<service>/journal/200
```

In the example defined above all valid enpoins are.

```
http://127.0.0.1:5001/csv/start
http://127.0.0.1:5001/csv/stop
http://127.0.0.1:5001/csv/restart
http://127.0.0.1:5001/csv/reload
http://127.0.0.1:5001/csv/reloadorrestart
http://127.0.0.1:5001/csv/status
http://127.0.0.1:5001/csv/journal
http://127.0.0.1:5001/csv/journal/<number>
http://127.0.0.1:5001/csv/enable
http://127.0.0.1:5001/csv/disable
```
