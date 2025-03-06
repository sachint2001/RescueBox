''' test audio typer cli commands and fastapi api calls'''
import json
from pathlib import Path
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from typer.testing import CliRunner
# this app is for cli testing using typer CliRunner
from rb_audio_transcription.main import DirInputs, app as cli_app
from rb.api.models import API_APPMETDATA, API_ROUTES, PLUGIN_SCHEMA_SUFFIX, DirectoryInput, ResponseBody
# this app is for fastapi testing using TestClient
from rb.api.main import app as api_app

    
runner = CliRunner()
client = TestClient(api_app)

r'''
 run testss from test folder
 cd C:\xxxx\RescueBox && poetry run pytest  src\rb-audio-transcription\tests\test_main.py -vvv
 
 log-cli-level=10 fails with ValueError: I/O operation on closed file. logging issue ??
'''

def test_routes_command():
    ''' call typer cli to get routes'''
    result = runner.invoke(cli_app, [API_ROUTES])
    assert result != ""
    assert result.exit_code == 0


def test_metadata_command():
    result = runner.invoke(cli_app, [API_APPMETDATA])
    assert result != ""
    assert result.exit_code == 0


def test_schema_command():
    result = runner.invoke(cli_app, [f"task{PLUGIN_SCHEMA_SUFFIX}"])
    assert result != ""
    assert result.exit_code == 0

def test_negative_test():
    ''' audio transcribe command cli to transcribe with invalid audio file''' # type: ignore
    bad_full_path = Path.cwd().joinpath('src', 'rb-audio-transcription', 'bad_tests')
    result = runner.invoke(
        cli_app, ['transcribe', jsonable_encoder(bad_full_path), "'e1': 'example', 'e2' : 0.1, 'e3': 1"]
    )
    print("negative test ",result.stdout)
    assert "Aborted." in result.stdout
    assert result.exit_code == 1

def test_cli_transcribe_command():
    r''' call audio transcribe command typer cli to transcribe a sample audio file'''
    full_path = Path.cwd() / 'src' / 'rb-audio-transcription' / 'tests'
    print("cli test", full_path)
    result = runner.invoke(
        cli_app, ['transcribe', jsonable_encoder(full_path), "'e1': 'example', 'e2' : 0.1, 'e3': 1"]
    )
    assert result.stdout is not None
    assert result.exit_code == 0

def test_api_transcribe_command():
    r''' call audio transcribe command fastapi to transcribe a sample audio file'''
    
    full_path = Path.cwd() / 'src' / 'rb-audio-transcription' / 'tests'

    # force validation of DirectoryInput full_path
    DirInputs(dir_input=DirectoryInput(path=full_path))

    audio = {"inputs": {"dir_input": {
                         "path": jsonable_encoder(full_path) 
                        } 
                       },
             "parameters": {'example_parameter': 'example',
                            'example_parameter2' : 0.1,
                            'example_parameter3': 1
                            }
            }

    print(json.dumps(audio))
    response = client.post('/audio/transcribe', json=audio)
    
    assert response is not None
    assert response.status_code == 200
    output = ResponseBody(**response.json())
    assert output is not None
    txt = [txt.value for txt in output.root.texts]
    assert txt is not None
    assert len(txt) > 0
    assert 'Twinkle twinkle little star' in txt[0]

def test_client_routes():
    ''' call fastapi /api/routes '''
    response = client.get('/api/routes')
    assert response is not None
    assert response.status_code == 200
    assert response.json() is not None



def test_client_metadata():
    ''' call fastapi /api/routes '''
    response = client.get('/api/app_metadata')
    assert response is not None
    assert response.status_code == 200
    assert response.json() is not None


# TODO: other api routes tests example : client.post(f'/manage/info')
