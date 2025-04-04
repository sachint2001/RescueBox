## Audio Transcription

### Installing requirements

1. Install ffmpeg(.exe on windows)
```
sudo apt update && sudo apt install ffmpeg
```
2. Install poetry with pip/pipx
```
poetry lock ( refer dependencies listed in pyproject.toml)
```
3. Install dependencies
```
poetry install
```

### Starting the server

```
run_server

```

### Client command line example

```
sample file : <RescueBOX_HOME>src\audio-transcription\tests\sample.mp3
poetry run  typer audio_transcription.main run transcribe "<PATH-to>\src\audio-transcription\tests\sample.mp3"


negative test : typer audio_transcription.main run transcribe "sample.mp3" "'e1': 'example', 'e2' : 0.1, 'e3': 1"
ERROR:audio_transcription.main:Invalid full path input for transcribe command: sample.mp3
Aborted.

```

### Command line tool
```
poetry run typer audio_transcription.main --help
```
Transcribe a single file
```
poetry run typer audio_transcription.main run transcribe "full_path_to_mp3_file"
```
