# Bob Documentation and Tips

## Create new service

In order to launch a Bob module during the start-up of the Raspberry Pi, we
create services that are managed through Systemd.

To create a new service, you first need to create a ``.service`` file (like
[this one](https://github.com/policumbent/bob/tree/main/utility/example_module/example.service)),
then, you have to copy it in ``/etc/systemd/system/`` and run:
```Bash
sudo systemctl enable <your-service-name>
```

You can also see the status of your service using the command:
```Bash
sudo systemctl status <your-service-name>
```

## Update Bob

At this stage, Bob cannot update itself though Git, so one (not-so-beautiful)
way to update its modules is take the Raspberry's SD Card, open it with a
**Linux** computer (if you do it on Windows you won't see the Raspberry's main
partition, since Windows doesn't support it) and substitute the module of
interest with the new version.