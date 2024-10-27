from dataclasses import dataclass
from typer import Typer
from rescuebox.main import app

@dataclass
class RescueBoxPlugin:
    app: Typer
    name: str

plugins: list[RescueBoxPlugin] = [
]

for plugin in plugins:
    app.add_typer(plugin.app, name=plugin.name)
