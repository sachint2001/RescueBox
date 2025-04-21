import os
import subprocess
import shutil
from typing import TypedDict
from rb.lib.ml_service import MLService
from rb.api.models import (
    ParameterSchema,
    TaskSchema,
    ResponseBody,
    TextResponse,
    BatchTextResponse,
    FileInput,
    InputSchema,
    InputType,
    DirectoryInput,
    FileResponse
)
from datetime import datetime
import typer
import ollama

from pathlib import Path

from rb.api.models import ResponseBody
from video_summarizer.main import app as cli_app, APP_NAME, create_video_summary_schema
from rb.lib.common_tests import RBAppTest
from rb.api.models import AppMetadata

class TestVideoSummarization(RBAppTest):
    def setup_method(self):
        self.set_app(cli_app, APP_NAME)

    def get_metadata(self):
        return AppMetadata(
            plugin_name=APP_NAME,
            name="Video Summarization",
            author="Sachin Thomas & Priyanka Bengaluru Anil",
            version="1.0.0",
            info="Video Summarization using Gemma model.",
        )
    
    def get_all_ml_services(self):
        return [
            (0, "summarize-video", "Video Summarization", create_video_summary_schema()),
        ]

    def test_negative_input_path(self):
        summarize_api = f"/{APP_NAME}/summarize-video"
        bad_path = Path.cwd() / "nonexistent" / "video.mp4"
        out_dir = Path.cwd() / "test_outputs"
        out_dir.mkdir(exist_ok=True)

        input_arg = f"{bad_path},{out_dir}"
        result = self.runner.invoke(cli_app, [summarize_api, input_arg, "1"])
        assert "does not exist" in result.stdout or result.exit_code != 0

    def test_cli_video_summarize_command(self, caplog):
        with caplog.at_level("INFO"):
            summarize_api = f"/{APP_NAME}/summarize-video"
            video_file = Path.cwd() / "src" / "video-summarizer" / "tests" / "sample_video.mp4"
            out_dir = Path.cwd() / "src" / "video-summarizer" / "test_outputs"
            out_dir.mkdir(exist_ok=True)

            input_arg = f"{video_file},{out_dir}"
            result = self.runner.invoke(cli_app, [summarize_api, input_arg, "1"])

            assert result.exit_code == 0
            assert any("Frame" in msg for msg in caplog.messages)

    