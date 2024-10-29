import requests
import typer
from rich import print


def check_ollama() -> bool:
    response = requests.get("http://localhost:11434")
    if response.status_code == 200 and "Ollama" in response.text:
        return True
    return False


# ollama decorator that verifies ollama is running
def use_ollama(func):
    def wrapper(*args, **kwargs):
        if not check_ollama():
            print("[red] Ollama is not running. Please start it and try again.")
            raise typer.Abort()
