from pathlib import Path
from typing import List

import os
import typer

app = typer.Typer()
bob_root = Path(__file__).parent.parent.parent
all_modules = os.listdir(bob_root / 'modules')


@app.command()
def module_list():
    print("List of modules")
    for module in all_modules:
        print(module)


@app.command()
def install(modules: List[str], python: bool = True, apt: bool = True, verbose: bool = False, apt_upgrade: bool = True):
    if apt_upgrade:
        os.system('sudo apt update && sudo apt upgrade -y')
    counter = 1
    if len(modules) == 0:
        modules = all_modules
    for module in modules:
        module_dir = bob_root / 'modules' / module
        print('**********************************************************')
        print(f'Installing requirements of {module} [{counter}/{len(modules)}]')
        print('**********************************************************')
        if apt:
            package_file = module_dir / 'package_list.txt'
            if package_file.exists():
                with open(package_file) as f:
                    for line in f.readlines():
                        dep = line.replace('\n', '')
                        os.system(f'sudo apt install {dep} -y')
        if module.__eq__("video"):
            # TODO: implement video
            pass
        else:
            os.system(f'cd {module_dir} && poetry install')
        counter += 1


@app.command()
def add_module(name: str):
    print("Create module: {}".format(name))
    # TODO: implement add_module


@app.command()
def start(modules: List[str] = typer.Argument(None)):
    if not modules:
        print("Start all modules")
    else:
        for module in modules:
            print("Start {}".format(module))


@app.command()
def stop(modules: List[str] = typer.Argument(None)):
    if not modules:
        print("Stop all modules")
        # TODO: implement stop
    else:
        for module in modules:
            print("Stop {}".format(module))
            # TODO: implement stop


@app.command()
def log(name: str):
    print("See log of module: {}".format(name))
    # TODO: implement log


@app.command()
def enable(modules: List[str] = typer.Argument(None)):
    if not modules:
        print("Enable all modules")
        # TODO: implement enable
    else:
        for module in modules:
            print("Enable {}".format(module))
            # TODO: implement enable


@app.command()
def disable(modules: List[str] = typer.Argument(None)):
    if not modules:
        print("Disable all modules")
        # TODO: implement disable
    else:
        for module in modules:
            print("Disable {}".format(module))
            # TODO: implement disable


@app.command()
def copy_services(modules: List[str] = typer.Argument(None)):
    if not modules:
        print("Copy all modules' services")
        # TODO: implement copy_services
    else:
        for module in modules:
            print("Copy service of: {}".format(module))
            # TODO: implement copy_services


@app.command()
def status(module: str):
    print("Status of {}".format(module))
    # TODO: implement status


if __name__ == '__main__':
    app()
