from pathlib import Path

from fastapi.testclient import TestClient
from rb.api.main import app as api_app
from rb.api.models import API_APPMETDATA, API_ROUTES, PLUGIN_SCHEMA_SUFFIX, ResponseBody
from rb_audio_transcription.main import app as cli_app, APP_NAME
from typer.testing import CliRunner

runner = CliRunner()
client = TestClient(api_app)

EXPECTED_ROUTES = [
    {
        "task_schema": f"/{APP_NAME}/transcribe/task_schema",
        "run_task": f"/{APP_NAME}/transcribe",
        "payload_schema": f"/{APP_NAME}/transcribe/payload_schema",
        "sample_payload": f"/{APP_NAME}/transcribe/sample_payload",
        "short_title": "Transcribe audio files",
        "order": 0,
    }
]


def test_routes_command(caplog):
    with caplog.at_level("INFO"):
        result = runner.invoke(cli_app, [f"/{APP_NAME}/api/routes"])
        assert result.exit_code == 0
        assert any("run_task" in message for message in caplog.messages)


def test_metadata_command(caplog):
    with caplog.at_level("INFO"):
        result = runner.invoke(cli_app, [f"/{APP_NAME}/api/app_metadata"])
        assert result.exit_code == 0
        assert any("Audio Transcription" in message for message in caplog.messages)


def test_schema_command(caplog):
    with caplog.at_level("INFO"):
        result = runner.invoke(cli_app, [f"/{APP_NAME}/transcribe/task_schema"])
        assert result.exit_code == 0
        assert any("inputs" in message for message in caplog.messages)


def test_negative_test():
    transcribe_api = f"/{APP_NAME}/transcribe"
    bad_path = Path.cwd() / "src" / "rb-audio-transcription" / "bad_tests"
    result = runner.invoke(cli_app, [transcribe_api, str(bad_path)])
    assert "Aborted" in result.stdout or result.exit_code != 0


def test_cli_transcribe_command(caplog):
    with caplog.at_level("INFO"):
        transcribe_api = f"/{APP_NAME}/transcribe"
        full_path = Path.cwd() / "src" / "rb-audio-transcription" / "tests"
        print(f"Full path: {full_path}")
        print(f"Transcribe API: {transcribe_api}")
        result = runner.invoke(cli_app, [transcribe_api, str(full_path)])
        assert result.exit_code == 0
        expected_transcript = "Twinkle twinkle little star"
        assert any(expected_transcript in message for message in caplog.messages)


def test_api_transcribe_command(caplog):
    transcribe_api = f"/{APP_NAME}/run"
    full_path = Path.cwd() / "src" / "rb-audio-transcription" / "tests"
    response = client.post(transcribe_api, json={"path": str(full_path)})
    assert response.status_code == 200
    body = ResponseBody(**response.json())
    assert body.root.texts and "Twinkle" in body.root.texts[0].value


def test_client_routes():
    response = client.get(f"/{APP_NAME}/list_routes")
    assert response.status_code == 200
    actual_routes = response.json()

    assert (
        actual_routes == EXPECTED_ROUTES
    ), f"Mismatch in /audio/routes:\nExpected: {EXPECTED_ROUTES}\nGot: {actual_routes}"


def test_client_metadata():
    response = client.get(f"/{APP_NAME}/get_app_metadata")
    assert response.status_code == 200
    assert response.json().get("name") == "Audio Transcription"


def test_client_task_schema():
    response = client.get(f"/{APP_NAME}/get_task_schema")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    inputs = data.get("inputs")
    assert isinstance(inputs, list)
    assert len(inputs) == 1
    inputs = inputs[0]
    assert isinstance(inputs, dict)
    assert inputs.get("key") == "input_dir"
    assert inputs.get("label") == "Provide audio files directory"
    assert inputs.get("input_type") == "directory"
