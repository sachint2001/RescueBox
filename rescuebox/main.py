from importlib.metadata import version
import typer
import requests
from rich import print

from rescuebox.plugins import plugins, experimental_plugins

app = typer.Typer()

management_app = typer.Typer()

__version__ = version("rescuebox")


@management_app.command()
def info():
    print(f"RescueBox CLI with plugins {__version__}")
    print("[blue] Ollama is required to use AI plugins - https://ollama.com/")
    raise typer.Exit()


@management_app.command()
def list_plugins():
    print("Plugins:")
    for plugin in plugins:
        print(f"- {plugin.full_name}, {plugin.cli_name}")

@management_app.command()
def list_experimental_plugins():
    print("Experimental Plugins:")
    for plugin in experimental_plugins:
        print(f"- {plugin.full_name}, {plugin.cli_name}")

@management_app.command()
def ollama_site():
    typer.launch("https://ollama.com/")


@management_app.command()
def ollama_check():
    response = requests.get("http://localhost:11434")
    if response.status_code == 200 and "Ollama" in response.text:
        print("[green] Ollama is installed and running")
    else:
        print("[red] Ollama is not installed or not running")
    raise typer.Exit()


app.add_typer(management_app, name="manage")

for plugin in plugins:
    app.add_typer(plugin.app, name=plugin.cli_name)

for plugin in experimental_plugins:
    app.add_typer(plugin.app, name=f"exp-{plugin.cli_name}")
