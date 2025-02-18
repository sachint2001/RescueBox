import typer
import pathlib
from .model import AudioTranscriptionModel
from rb.api.templates import generate_text_response

app = typer.Typer()

model = AudioTranscriptionModel()

@app.command()
def transcribe(
    path: str = typer.Argument(..., help="Path to folder containing audio files")
):
    """Transcribe audio files in a folder"""

    folder = pathlib.Path(path)
    if not folder.is_dir():
        typer.echo(f"Error: {path} is not a valid directory.")
        raise typer.Exit(code=1)

    audio_extensions = {'.wav', '.mp3', '.m4a', '.flac'}
    files = [str(file) for file in folder.iterdir() if file.suffix.lower() in audio_extensions]

    if not files:
        typer.echo("No audio files found.")
        raise typer.Exit(code=1)

    results = model.transcribe_batch(files)
    results_dict = {r["file_path"]: r["result"] for r in results}

    print(f"Transcription Result: {results_dict}")  # Debug log

    return generate_text_response(results_dict)
        
