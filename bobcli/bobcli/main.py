import datetime
import subprocess
import time
from os.path import isfile, join
from pathlib import Path
from shutil import copyfile
from typing import List

import os
import typer

from systemdlib import systemdBus, Journal

app = typer.Typer(add_completion=False)

bob_root = Path(__file__).parent.parent.parent
all_modules = os.listdir(bob_root / 'modules')


@app.command()
def module_list():
    """
    List all the available modules
    """
    typer.secho("List of modules:", bold=True, fg=typer.colors.BLUE)
    for module in all_modules:
        typer.echo(module)


@app.command()
def setup(modules: List[str] = typer.Argument(None, help="List of modules to install, empty for installing all of them")):
    """
    Perform all the needed setup and run the specified modules
    """
    if modules is None:
        modules = all_modules
    install(modules, True, True)
    copy_services(modules, True, True)
    start(modules)


@app.command()
def install(
        modules: List[str] = typer.Argument(None, help="List of modules to install, empty for installing all of them"),
        python: bool = typer.Option(True, help="Install python dependencies"),
        apt: bool = typer.Option(True, help="Install apt dependencies")):
    """
    Install specified modules dependencies
    """
    apt_upgrade = typer.confirm('Do you want to run apt update && apt upgrade?')
    if apt_upgrade:
        subprocess.call('sudo apt update && sudo apt upgrade -y', shell=True)
    counter = 1
    if len(modules) == 0:
        typer.confirm(
            'Installing all the modules dependencies, this operation can take up to 30 min, do you want to continue?',
            abort=True)
        modules = all_modules
    if (not python) and (not apt):
        typer.echo("No modules to install, specify at least one of --python or --apt")
        return
    start = time.time()
    for module in modules:
        if module not in modules:
            typer.echo("Module {} does not exist".format(module))
            continue
        module_dir = bob_root / 'modules' / module
        typer.echo('**********************************************************')
        typer.echo(f'Installing requirements of {module} [{counter}/{len(modules)}]')
        typer.echo('**********************************************************')
        if apt:
            package_file = module_dir / 'package_list.txt'
            if package_file.exists():
                with open(package_file) as f:
                    for line in f.readlines():
                        dep = line.replace('\n', '')
                        subprocess.call(f'sudo apt install -y {dep}', shell=True)
        if python:
            if module == "video":
                venv_folder = module_dir / ".venv"
                print(venv_folder)
                if not os.path.exists(venv_folder):
                    subprocess.call(f'cd {module_dir} && python3 -m venv .venv', shell=True)
                subprocess.call(f'cd {module_dir} && .venv/bin/pip install -r requirements.txt ', shell=True)
            else:
                subprocess.call(f'cd {module_dir} && poetry install', shell=True)
        counter += 1
    end = time.time()
    typer.secho(f'Installazione completata. Tempo installazione: {datetime.timedelta(seconds=end - start)}.',
                fg=typer.colors.GREEN, bold=True)
    subprocess.call(f'cd {bob_root} && sudo cp utility/ant-usb-sticks.rules /etc/udev/rules.d/', shell=True)

    other_tools = typer.confirm('Do you want to install/configure other tools?')
    if other_tools:
        resp = typer.confirm('Modificare bluez service?', default=True)
        if resp:
            subprocess.call(
                f'sudo cp {bob_root / "utility/dbus-org.bluez.service"} /etc/systemd/system/dbus-org.bluez.service ',
                shell=True)

        resp = typer.confirm('Modificare file config.txt?', default=True)
        if resp:
            subprocess.call(f'sudo cp {bob_root / "utility/config.txt"} /boot/config.txt', shell=True)

        resp = typer.confirm('Installare splashscreen?', default=True)
        if resp:
            subprocess.call('sudo apt install fbi -y', shell=True)
            subprocess.call(f'sudo cp {bob_root / "utility/splashscreen.service"} /etc/systemd/system/', shell=True)
            subprocess.call('sudo systemctl enable splashscreen.service', shell=True)
            subprocess.call('sudo systemctl start splashscreen.service', shell=True)

        resp = typer.confirm('Installare cockpit? (y/N)', default=True)
        if resp:
            subprocess.call('sudo apt install cockpit', shell=True)
            subprocess.call('sudo apt install screenfetch', shell=True)


@app.command()
def add_module(module_name: str = typer.Argument(..., help="Name of the module to add")):
    """
    Add a new module to BOB
    """
    module_types = ('Sensore', 'Consumatore', 'Remoto')
    typer.echo('Tipologia modulo: ')
    typer.echo('1) Sensore')
    typer.echo('2) Consumatore')
    typer.echo('3) Remoto')
    module_type = 0
    while module_type not in range(1, 4):
        module_type = typer.prompt('Scegli una tipologia', type=int)
    signals_list = typer.prompt(
        'Quali sono i segnali accettati? (Separarare le parole con virgola, per esempio "reset, stop"): ')
    topics_list = '[]'
    if module_type != 1:
        topics_list = typer.prompt('Quali sono i moduli che deve ascoltare?'
                                   ' (Separarare le parole con virgola, per esempio "manager, ant, gps"): ')
    typer.echo('- - - - - - - - - - - - -')
    module_name = module_name.replace(' ', '_')
    typer.echo(f'Nome modulo: {module_name}')
    typer.echo(f'Tipologia modulo: {module_types[module_type - 1]}')
    signals_list = signals_list.replace(' ', '')
    signals_list = signals_list.split(',')
    typer.echo(f'Segnali accettati: {signals_list}')
    if module_type != 1:
        topics_list = topics_list.replace(' ', '')
        topics_list = topics_list.split(',')
        typer.echo(f'Sensori da ascoltare: {topics_list}')
    confirm = typer.confirm('Vuoi confermare?', abort=True)
    os.makedirs(f'{bob_root}/modules/{module_name}/src/', exist_ok=True)
    copyfile(bob_root / 'utility/example_module/.gitignore', bob_root / f'modules/{module_name}/.gitignore')
    copyfile(bob_root / 'utility/example_module/poetry.toml', bob_root / f'modules/{module_name}/poetry.toml')
    copyfile(bob_root / 'utility/example_module/pyproject.toml', bob_root / f'modules/{module_name}/pyproject.toml')

    # copy service file and replace module name
    source_path = bob_root / 'utility/example_module/example.service'
    dest_path = bob_root / f'modules/{module_name}/{module_name}.service'
    # replace ${MODULE_NAME} in service_file with module_name
    service_file = open(source_path, 'r')
    service_content = service_file.read()
    service_file.close()
    service_content = service_content.replace('${MODULE_NAME}', module_name)
    # write service_content in the destination file
    service_file = open(dest_path, 'w')
    service_file.write(service_content)
    service_file.close()

    files = [f for f in os.listdir(bob_root / 'utility/example_module/src') if
             isfile(join(bob_root / 'utility/example_module/src', f))]
    for file in files:
        file_dest = bob_root / f'modules/{module_name}/src/' / file
        file_src = bob_root / 'utility/example_module/src' / file
        copyfile(file_src, file_dest)

    with open(bob_root / 'utility/example_module/src/main.py') as f:
        main = ''.join(f.readlines())
        message_handler = ''
        if module_type == 1:
            mqtt_init = f"mqtt = MqttSensor(sys.argv[1], 1883, '{module_name}'," \
                        f" {str(signals_list)}, settings, message_handler)"
        elif module_type == 2:
            main = main.replace('MqttSensor', 'MqttConsumer')
            mqtt_init = f"mqtt = MqttConsumer(sys.argv[1], 1883, '{module_name}', {str(topics_list)}" \
                        f" {str(signals_list)}, settings, message_handler)"
            message_handler += f"    try:\n"
            for topic in topics_list:
                message_handler += f"        if topic == 'sensors/{topic}':\n"
                message_handler += f"            # questo è solo un esempio, deserializzo i dizionari\n"
                message_handler += f"            {topic}_dict: dict = json.loads(message)\n"
            message_handler += f"    except Exception as e:\n"
            message_handler += f"        typer.echo(e)\n"

        elif module_type == 3:
            main = main.replace('MqttSensor', 'MqttRemote')
            mqtt_init = f"mqtt = MqttRemote(sys.argv[1], 1883, '{module_name}', {str(topics_list)}" \
                        f" {str(signals_list)}, settings, message_handler)"
        main = main.replace('#$$mqtt start$$#', mqtt_init)
        main = main.replace('#$$message handler$$#', message_handler)
        with open(bob_root / f'modules/{module_name}/src/main.py', 'w') as fw:
            fw.write(main)
    typer.echo('Modulo creato')


@app.command()
def start(modules: List[str] = typer.Argument(None)):
    """
    Start the specified modules with systemd
    """
    if len(modules) == 0:
        modules = all_modules
    for module in modules:
        if module not in all_modules:
            typer.secho(f'Module {module} does not exist', fg=typer.colors.RED)
            continue
        sdbus = systemdBus()
        units = getModuleServiceFiles(module)
        for unit in units:
            if sdbus.start_unit(unit):
                typer.secho("Started {}".format(unit), fg=typer.colors.GREEN)
            else:
                typer.secho("Failed to start {}, try with sudo or read log with bob log {}".format(unit, module),
                            fg=typer.colors.RED, err=True)


@app.command()
def stop(modules: List[str] = typer.Argument(None, help="List of modules to stop")):
    """
    Stop the specified modules with systemd
    """
    if len(modules) == 0:
        modules = all_modules
    for module in modules:
        if module not in all_modules:
            typer.echo(f'Module {module} does not exist')
            continue
        sdbus = systemdBus()
        units = getModuleServiceFiles(module)
        for unit in units:
            if sdbus.stop_unit(unit):
                typer.secho("Stopped {}".format(unit), fg=typer.colors.GREEN)
            else:
                typer.secho("Failed to stop {}, try with sudo or read log with bob log {}".format(unit, module),
                            fg=typer.colors.RED, err=True)


@app.command()
def log(module_name: str, length: int = typer.Option(50, help='Number of lines to show')):
    """
    Show the last lines of the log of the specified module
    """
    if module_name not in all_modules:
        typer.secho(f'Module {module_name} does not exist', fg=typer.colors.RED)
        return
    units = getModuleServiceFiles(module_name)
    for unit in units:
        journal = Journal(unit)
        lines = journal.get_tail(length + 1)
        if len(lines) == 0:
            typer.secho("No logs for {}".format(unit), fg=typer.colors.YELLOW)
        for line in lines:
            typer.echo(line)
        if len(units) > 1 and unit != units[-1]:
            confirm = typer.confirm(f'Do you want to see the other service files logs?')
            if not confirm:
                return


@app.command()
def enable(modules: List[str] = typer.Argument(None)):
    """
    Enable the systemd service for the specified modules
    """
    if len(modules) == 0:
        modules = all_modules
    for module in modules:
        if module not in all_modules:
            typer.echo(f'Module {module} does not exist')
            continue
        sdbus = systemdBus()
        units = getModuleServiceFiles(module)
        if len(units) > 0:
            typer.echo(f'Module {module}:')
        for unit in units:
            if sdbus.enable_unit(unit):
                typer.secho("\tEnabled {}".format(unit), fg=typer.colors.GREEN)
            else:
                typer.secho("\tFailed to enable {}".format(unit), fg=typer.colors.RED, err=True)


@app.command()
def disable(modules: List[str] = typer.Argument(None)):
    """
    Disable the systemd service for the specified modules
    """
    if len(modules) == 0:
        modules = all_modules
    for module in modules:
        if module not in all_modules:
            typer.echo(f'Module {module} does not exist')
            continue
        sdbus = systemdBus()
        units = getModuleServiceFiles(module)
        for unit in units:
            if sdbus.disable_unit(unit):
                typer.echo("Disabled {}".format(module))
            else:
                typer.secho("Failed to start {}".format(module), fg=typer.colors.RED, err=True)


@app.command()
def copy_services(modules: List[str] = typer.Argument(None), enable: bool = True, y: bool = False):
    """
    Copy the systemd service files for the specified modules
    """
    dest = '/etc/systemd/system/'
    if len(modules) == 0:
        modules = all_modules
    sdbus = systemdBus()
    for module in modules:
        if module not in all_modules:
            typer.secho(f'Module {module} does not exist', fg=typer.colors.RED, err=True)
            continue
        units = getModuleServiceFiles(module)
        if len(units) == 0:
            typer.echo("No service files found for {}".format(module))
            continue
        for service_name in units:
            source_path = bob_root / f'modules/{module}/{service_name}'
            new_path = os.path.join(dest, service_name)
            if not y:
                confirm = typer.confirm(f"Copy {source_path} to {new_path}?")
                if not confirm:
                    continue
            # replace ${BOB_ROOT} in service_file with current_dir
            service_file = open(source_path, 'r')
            service_content = service_file.read()
            service_file.close()
            service_content = service_content.replace('${BOB_ROOT}', bob_root.absolute().__str__())
            # write service_content in the destination file
            try:
                service_file = open(new_path, 'w')
                service_file.write(service_content)
                service_file.close()
            except PermissionError as e:
                typer.secho(f"Permission error, try running the cli with sudo.", fg=typer.colors.RED)
                continue
            except Exception as e:
                typer.secho(f"Failed to copy {source_path} to {new_path}", fg=typer.colors.RED)
                continue
            if enable:
                if sdbus.enable_unit(service_name):
                    typer.echo("Enabled {}".format(service_name))
                else:
                    typer.secho("Failed to start {}".format(service_name), fg=typer.colors.RED, err=True)


@app.command()
def status(modules: List[str] = typer.Argument(None)):
    """
    Show the systemd status of the specified modules
    """
    if len(modules) == 0:
        modules = all_modules
    sdbus = systemdBus()
    for module_name in modules:
        if module_name not in all_modules:
            typer.secho(f'Module {module_name} does not exist', err=True, fg=typer.colors.RED)
            continue
        units = getModuleServiceFiles(module_name)
        if len(units) == 0:
            typer.secho(f"Module {module_name} does not exist or does not have a service file", fg=typer.colors.RED,
                        err=True)
            continue
        typer.echo(f"Module {module_name}:")
        for unit in units:
            module_name = typer.style(module_name, bold=True)
            active = sdbus.get_unit_active_state(unit)
            if active == 'active' or active == 'activating':
                active = typer.style(active, fg=typer.colors.GREEN, bold=True)
            else:
                active = typer.style(active, fg=typer.colors.RED)
            enabled = sdbus.get_unit_enable_state(unit)
            if enabled == 'enabled':
                enabled = typer.style(enabled, fg=typer.colors.GREEN, bold=True)
            else:
                enabled = typer.style(enabled, fg=typer.colors.RED)
            loaded = sdbus.get_unit_load_state(unit)
            if loaded == 'loaded':
                loaded = typer.style(loaded, fg=typer.colors.GREEN, bold=True)
            else:
                loaded = typer.style(loaded, fg=typer.colors.RED)
            typer.echo(f'\t{unit}: {active}, {enabled}, {loaded}')


@app.command()
def run_mqtt_broker():
    """
    Run, with docker, the mqtt broker for the communication between the modules
    """
    subprocess.call(f'cd {bob_root} && sudo docker-compose up -d', shell=True)


def getModuleServiceFiles(module_name) -> [str]:
    module_dir = bob_root / f'modules/{module_name}'
    if not module_dir.exists():
        return []
    service_files = []
    for file in module_dir.glob('*.service'):
        service_files.append(file.name)
    return service_files


if __name__ == '__main__':
    app()
