from importlib.metadata import version

import requests
import typer
from rich import print

from rescuebox.plugins import experimental_plugins, plugins

app = typer.Typer()

management_app = typer.Typer()

__version__ = version("rescuebox")


@management_app.command()
def info() -> str:
    message = f"RescueBox CLI with plugins {__version__}"
    print(message)
    return message


@management_app.command()
def list_plugins() -> list[str]:
    print("Plugins:")
    plugin_list = []
    for plugin in plugins:
        print(f"- {plugin.full_name}, {plugin.cli_name}")
        plugin_list.append(plugin.cli_name)
    return plugin_list


@management_app.command()
def list_experimental_plugins() -> list[str]:
    print("Experimental Plugins:")
    plugin_list = []
    for plugin in experimental_plugins:
        print(f"- {plugin.full_name}, {plugin.cli_name}")
        plugin_list.append(plugin.cli_name)
    return plugin_list


@management_app.command()
def ollama_site() -> str:
    ollama_url = "https://ollama.com/"
    typer.launch(ollama_url)
    return ollama_url


@management_app.command()
def ollama_check() -> bool:
    response = requests.get("http://localhost:11434")
    if response.status_code == 200 and "Ollama" in response.text:
        print("[green] Ollama is installed and running")
        return True
    else:
        print("[red] Ollama is not installed or not running")
        return False


app.add_typer(management_app, name="manage")

for plugin in plugins:
    app.add_typer(plugin.app, name=plugin.cli_name)

for plugin in experimental_plugins:
    app.add_typer(plugin.app, name=f"exp-{plugin.cli_name}")
