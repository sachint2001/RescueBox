from abc import ABC, abstractmethod
from typing import List, Tuple
from rb.api.models import AppMetadata, TaskSchema
from typer.testing import CliRunner
from fastapi.testclient import TestClient
from rb.api.main import app as api_app


class RBAppTest(ABC):

    def set_app(self, cli_app, app_name: str):
        """
        cli_app: The Typer app object.
        app_name: The name of the app.
        """
        self.cli_app = cli_app
        self.app_name = app_name
        self.client = TestClient(api_app)
        self.runner = CliRunner()
        self.ml_services = self.get_all_ml_services()

    @abstractmethod
    def get_metadata(self) -> AppMetadata:
        """
        Return the app metadata.
        """
        pass

    @abstractmethod
    def get_all_ml_services(self) -> List[Tuple[int, str, str, TaskSchema]]:
        """
        Return a list of all ml services with their order, name, short_title, and task schema.
        Ex: [(0, "transcribe", "Audio Transcription", task_schema),
             (1, "summarize", "Text Summarization", task_schema)]
        """
        pass

    def get_expected_routes(self) -> List[dict]:
        """
        Return the expected routes for the app.
        """
        expected_routes = []
        for order, rule, short_title, task_schema in self.ml_services:
            expected_routes.append(
                {
                    "task_schema": f"/{self.app_name}/{rule}/task_schema",
                    "run_task": f"/{self.app_name}/{rule}",
                    "short_title": short_title,
                    "order": order,
                }
            )
        return expected_routes

    def test_routes_command(self, caplog):
        """
        Test the routes command.
        """
        with caplog.at_level("INFO"):
            result = self.runner.invoke(self.cli_app, [f"/{self.app_name}/api/routes"])
            assert result.exit_code == 0
            expected_routes = self.get_expected_routes()
            for route in expected_routes:
                assert any(route["run_task"] in message for message in caplog.messages)
                assert any(
                    route["task_schema"] in message for message in caplog.messages
                )
                assert any(
                    route["short_title"] in message for message in caplog.messages
                )
                assert any(
                    str(route["order"]) in message for message in caplog.messages
                )

    def check_if_str_in_messages(self, str_to_check: str, messages: List[str]):
        """
        Check if a string is in the messages.
        """
        assert any(str_to_check in message for message in messages)

    def test_metadata_command(self, caplog):
        with caplog.at_level("INFO"):
            expected_metadata = self.get_metadata().model_dump(mode="json")
            result = self.runner.invoke(
                self.cli_app, [f"/{self.app_name}/api/app_metadata"]
            )
            assert result.exit_code == 0
            for key, value in expected_metadata.items():
                assert any(str(key) in message for message in caplog.messages)
                assert any(str(value) in message for message in caplog.messages)

    def test_schema_command(self, caplog):
        with caplog.at_level("INFO"):
            ml_services = self.get_all_ml_services()
            for service in ml_services:
                _, rule, _, task_schema = service
                result = self.runner.invoke(
                    self.cli_app, [f"/{self.app_name}/{rule}/task_schema"]
                )
                assert result.exit_code == 0
                for key, value in task_schema.model_dump(mode="json").items():
                    assert any(str(key) in message for message in caplog.messages)
                    assert any(str(value) in message for message in caplog.messages)

    def test_api_routes(self):
        response = self.client.get(f"/{self.app_name}/api/routes")
        assert response.status_code == 200
        body = response.json()
        expected_routes = self.get_expected_routes()
        assert len(body) == len(expected_routes)
        assert expected_routes == body

    def test_api_metadata(self):
        response = self.client.get(f"/{self.app_name}/api/app_metadata")
        assert response.status_code == 200
        body = response.json()
        expected_metadata = self.get_metadata().model_dump(mode="json")
        assert body == expected_metadata

    def test_api_task_schema(self):
        ml_services = self.get_all_ml_services()
        for service in ml_services:
            _, rule, _, task_schema = service
            response = self.client.get(f"/{self.app_name}/{rule}/task_schema")
            assert response.status_code == 200
            body = response.json()
            assert body == task_schema.model_dump(mode="json")
