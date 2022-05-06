# BOB CLI
Control BOB through a command line interface.

## Installation

### Prerequisites

If you are a Ubuntu/Debian user you need to install `libsystemd-dev`, for
CentOS users the package is `systemd-devel`.


```sh
poetry install
alias sudo='sudo ' # to avoid problems with sudo
alias bob="/home/pi/BOB/bobcli/.venv/bin/python3  /home/pi/BOB/bobcli/bobcli/main.py"
```

## Run
Simply run to see the commands available.

```
bob --help 
```



