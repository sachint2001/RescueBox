import typer
from rb.lib.docs import DOCS_GITHUB_URL, download_reference_doc  # type: ignore
from rb.lib.ollama import use_ollama  # type: ignore
from rb_doc_parser.chat import load_chat_config, stream_output

app = typer.Typer()


@app.command()
def open() -> str:
    """
    Open docs in the browser
    """
    typer.launch(DOCS_GITHUB_URL)
    return DOCS_GITHUB_URL


@use_ollama
@app.command()
def ask(
    question: str = typer.Argument(..., help="Ask a question against the docs"),
) -> str:
    """
    Ask a question against the docs
    """
    reference_doc = download_reference_doc()
    chat_config = load_chat_config()
    chat_config["prompt"]["system"] = chat_config["prompt"]["system"].format(
        reference_doc=reference_doc
    )

    return stream_output(question, chat_config)
