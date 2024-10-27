import os

import typer

app = typer.Typer()


@app.command()
@app.command("ls")
def list_files(path: str = typer.Argument(..., help="The path to list files from")):
    """
    List files in a directory
    """
    if not os.path.exists(path):
        print(f"Path {path} does not exist")
        raise typer.Abort()
    if not os.path.isdir(path):
        print(f"Path {path} is not a directory")
        raise typer.Abort()
    for file in os.listdir(path):
        print(file)


@app.command()
@app.command("open")
def open_file(path: str = typer.Argument(..., help="The path to open")):
    """
    Open a file
    """
    if not os.path.exists(path):
        print(f"Path {path} does not exist")
        raise typer.Abort()
    typer.launch(path)
