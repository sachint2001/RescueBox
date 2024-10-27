from importlib.metadata import version

from typer.testing import CliRunner

from rescuebox.main import app

runner = CliRunner()


def test_manage_info():
    result = runner.invoke(app, ["manage", "info"])
    assert result.exit_code == 0
    assert version("rescuebox") in result.stdout
