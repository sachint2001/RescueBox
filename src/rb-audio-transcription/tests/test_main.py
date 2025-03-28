from pathlib import Path

from fastapi.testclient import TestClient
from rb.api.main import app as api_app
from rb.api.models import API_APPMETDATA, API_ROUTES, PLUGIN_SCHEMA_SUFFIX, ResponseBody
from rb_audio_transcription.main import AudioTranscriptionParser
from rb_audio_transcription.main import app as cli_app
from typer.testing import CliRunner

runner = CliRunner()
client = TestClient(api_app)


def test_routes_command():
    result = runner.invoke(cli_app, [API_ROUTES])
    assert result.exit_code == 0
    assert "run_task" in result.stdout


def test_metadata_command():
    result = runner.invoke(cli_app, [API_APPMETDATA])
    assert result.exit_code == 0
    assert "Audio Transcription" in result.stdout


def test_schema_command():
    result = runner.invoke(cli_app, [f"task{PLUGIN_SCHEMA_SUFFIX}"])
    assert result.exit_code == 0
    assert "inputs" in result.stdout


def test_negative_test():
    bad_path = Path.cwd() / "src" / "rb-audio-transcription" / "bad_tests"
    result = runner.invoke(cli_app, ["transcribe", str(bad_path)])
    assert "Aborted" in result.stdout or result.exit_code != 0


def test_cli_transcribe_command():
    full_path = Path.cwd() / "src" / "rb-audio-transcription" / "tests"
    result = runner.invoke(cli_app, ["transcribe", str(full_path)])
    assert result.exit_code == 0
    assert "Twinkle twinkle little star" in result.stdout


def test_api_transcribe_command():
    full_path = Path.cwd() / "src" / "rb-audio-transcription" / "tests"
    response = client.post("/audio/transcribe", json={"path": str(full_path)})
    assert response.status_code == 200
    body = ResponseBody(**response.json())
    assert body.root.texts and "Twinkle" in body.root.texts[0].value


def test_client_routes():
    response = client.get("/audio/routes")
    assert response.status_code == 200

    expected_routes = AudioTranscriptionParser().routes
    actual_routes = response.json()

    assert (
        actual_routes == expected_routes
    ), f"Mismatch in /audio/routes:\nExpected: {expected_routes}\nGot: {actual_routes}"


def test_client_metadata():
    response = client.get("/audio/app_metadata")
    assert response.status_code == 200
    assert response.json().get("name") == "Audio Transcription"


def test_client_task_schema():
    response = client.get("/audio/task_schema")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert data.get("key") == "dir_inputs"
    assert data.get("label") == "Provide audio files directory"
    assert data.get("input_type") == "batchfile"
