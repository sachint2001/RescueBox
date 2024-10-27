import typer
from rb.lib.ollama import use_ollama  # type: ignore
from rb.lib.docs import DOCS_GITHUB_URL  # type: ignore

app = typer.Typer()


@app.command()
def open():
    """
    Open docs in the browser
    """
    typer.launch(DOCS_GITHUB_URL)


@use_ollama
@app.command()
def ask(question: str = typer.Argument(..., help="Ask a question against the docs")):
    """
    Ask a question against the docs
    """
    print(question)


