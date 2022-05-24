# BOB CLI
Control BOB through a command line interface.

## Installation

### Prerequisites

If you are a Ubuntu/Debian user you need to install `libsystemd-dev`, for
CentOS users the package is `systemd-devel`.


```sh
poetry install
alias sudo='sudo ' # to avoid problems with sudo
alias bob="/<path>/<to>/<BOB>/bobcli/.venv/bin/python3  /<path>/<to>/<BOB>/bobcli/bobcli/main.py"
```
You may want to add the aliases to your `~/.bashrc` file in order to persist them.


## Run
Simply run to see the commands available.

```
bob --help 
```
Will reply:
    
```
Usage: main.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add-module     Add a new module to BOB
  copy-services  Copy the systemd service files for the specified modules
  disable        Disable the systemd service for the specified modules
  enable         Enable the systemd service for the specified modules
  install        Install specified modules dependencies
  log            Show the last lines of the log of the specified module
  module-list    List all the available modules
  setup          Perform all the needed setup and run the specified modules
  start          Start the specified modules with systemd
  status         Show the systemd status of the specified modules
  stop           Stop the specified modules with systemd
```

TIP: Some command will fail if you don't have the right permissions, so you can use `sudo` to run them.
