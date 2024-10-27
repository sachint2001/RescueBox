import typer
from typing import Optional, Annotated
import pkg_resources

app = typer.Typer()

__version__ = pkg_resources.get_distribution('rescuebox').version


def version_callback(value: bool):
    if value:
        print(f"RescueBox Version: {__version__}")
        raise typer.Exit()

@app.command()
def main(
    version: Annotated[
        Optional[bool], typer.Option("--version", callback=version_callback)
    ] = None,
):
    ...