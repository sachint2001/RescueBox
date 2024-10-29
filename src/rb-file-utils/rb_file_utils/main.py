import os

import typer

app = typer.Typer()


@app.command()
def ls(
    path: str = typer.Argument(..., help="The path to list files from"),
) -> list[str]:
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

    return os.listdir(path)


@app.command()
def open(path: str = typer.Argument(..., help="The path to open")) -> str:
    """
    Open a file
    """
    if not os.path.exists(path):
        print(f"Path {path} does not exist")
        raise typer.Abort()
    typer.launch(path)
    return path
