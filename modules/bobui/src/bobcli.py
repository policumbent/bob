#! /usr/bin/env python
from typing import List, Optional

import typer

app = typer.Typer()


@app.command()
def install(modules: List[str], python: bool = True, apt: bool = True, verbose: bool = False):
    for module in modules:
        print("Install {} (python={}, apt={}, verbose={})".format(module, python, apt, verbose))
        # TODO: implement install


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
