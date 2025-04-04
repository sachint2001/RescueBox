from text_summary.main import app as cli_app, APP_NAME, task_schema
from rb.lib.common_tests import RBAppTest
from rb.api.models import AppMetadata
from pathlib import Path
from unittest.mock import patch


class TestTextSummary(RBAppTest):
    def setup_method(self):
        self.set_app(cli_app, APP_NAME)

    def get_metadata(self):
        return AppMetadata(
            name="Text Summarization",
            author="UMass Rescue",
            version="0.1.0",
            info="Summarize text and PDF files in a directory.",
        )

    def get_all_ml_services(self):
        return [
            (0, "summarize", "Text Summarization", task_schema()),
        ]

    @patch("text_summary.summarize.ensure_model_exists")
    @patch("text_summary.summarize.summarize", return_value="Mocked summary")
    def test_summarize_command(self, summarize_mock, ensure_model_exists_mock):
        summarize_api = f"/{APP_NAME}/summarize"
        full_path = Path.cwd() / "src" / "text-summary" / "test_input"
        output_path = Path.cwd() / "src" / "text-summary" / "test_output"
        input_str = f"{str(full_path)},{str(output_path)}"
        parameter_str = "gemma3:1b"
        result = self.runner.invoke(
            self.cli_app, [summarize_api, input_str, parameter_str]
        )
        assert result.exit_code == 0, f"Error: {result.output}"
        output_files = list(output_path.glob("*.txt"))
        assert len(output_files) == 3
        for file in output_files:
            with open(file, "r") as f:
                content = f.read()
                assert "Mocked summary" == content

    @patch("text_summary.summarize.ensure_model_exists")
    @patch("text_summary.summarize.summarize", return_value="Mocked summary")
    def test_invalid_path(self, summarize_mock, ensure_model_exists_mock):
        summarize_api = f"/{APP_NAME}/summarize"
        bad_path = Path.cwd() / "src" / "text-summary" / "bad_tests"
        input_str = f"{str(bad_path)},{str(bad_path)}"
        parameter_str = "gemma3:1b"
        result = self.runner.invoke(
            self.cli_app, [summarize_api, input_str, parameter_str]
        )
        assert result.exit_code != 0
