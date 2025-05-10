from pathlib import Path
from unittest.mock import patch
from video_summarizer.main import app as cli_app, APP_NAME, create_video_summary_schema
from rb.lib.common_tests import RBAppTest
from rb.api.models import AppMetadata

class TestVideoSummarizer(RBAppTest):
    def setup_method(self):
        self.set_app(cli_app, APP_NAME)

    def get_metadata(self):
        return AppMetadata(
            name="Video Summarization",
            author="Sachin Thomas & Priyanka Bengaluru Anil",
            version="1.0.0",
            info="Video Summarization using Gemma model.",
            plugin_name=APP_NAME,
        )

    def get_all_ml_services(self):
        return [
            (0, "summarize-video", "Video Summarization", create_video_summary_schema()),
        ]

    # Test the CLI including audio transcription and check whether 3 files were created at the end
    @patch("video_summarizer.main.extract_frames_ffmpeg")
    @patch("video_summarizer.main.extract_audio_ffmpeg")
    @patch("video_summarizer.main.transcribe_audio", return_value="Mocked transcription")
    @patch("video_summarizer.main.ollama.generate", return_value={"response": "Mocked summary"})
    def test_video_summarizer_cli(self, mock_ollama, mock_transcribe, mock_audio, mock_frames):
        summarize_api = f"/{APP_NAME}/summarize-video"
        input_path = Path.cwd() / "src" / "video-summarizer" / "tests" / "test_inputs" / "sample_video.mp4"
        output_path = Path.cwd() / "src" / "video-summarizer" / "tests" / "test_outputs"
        input_str = f"{str(input_path)},{str(output_path)}"

        # Track initial .txt files
        initial_files = set(output_path.glob("*.txt"))
        
        result = self.runner.invoke(self.cli_app, [summarize_api, input_str, "1,yes"])
        
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        
        final_files = set(output_path.glob("*.txt"))
        new_files = final_files - initial_files
        assert len(new_files) == 3, "No new output files generated."

        # Check whether summary is correct:
        summary_file = next((f for f in new_files if f.name.startswith("summary_") and f.name.endswith(".txt")), None)

        assert summary_file is not None, "Summary file not found."

        with open(summary_file, "r", encoding="utf-8") as f:
            summary_content = f.read()
            assert "Mocked summary" in summary_content  # or your expected output

        # Delete the generated files
        for file in new_files:
            file.unlink()


    # Test the API call including audio transcription and check whether 3 files were created at the end
    @patch("video_summarizer.main.extract_frames_ffmpeg")
    @patch("video_summarizer.main.extract_audio_ffmpeg")
    @patch("video_summarizer.main.transcribe_audio", return_value="Mocked transcription")
    @patch("video_summarizer.main.ollama.generate", return_value={"response": "Mocked summary"})
    def test_video_summarizer_api(self, mock_ollama, mock_transcribe, mock_audio, mock_frames):
        summarize_api = f"/{APP_NAME}/summarize-video"
        input_path = Path.cwd() / "src" / "video-summarizer" / "tests" / "test_inputs" / "sample_video.mp4"
        output_path = Path.cwd() / "src" / "video-summarizer" / "tests" / "test_outputs"

        input_json = {
            "inputs": {
                "input_file": {"path": str(input_path)},
                "output_directory": {"path": str(output_path)}
            },
            "parameters": {
                "fps": 1,
                "audio_tran": "yes"
            }
        }

        # Track initial .txt files
        initial_files = set(output_path.glob("*.txt"))

        response = self.client.post(summarize_api, json=input_json)
        assert response.status_code == 200
         
        result = response.json()
        assert result is not None

        final_files = set(output_path.glob("*.txt"))
        new_files = final_files - initial_files
        assert len(new_files) == 3, "No new output files generated."

        # Basic check to ensure we received a string path
        assert isinstance(result['path'], str), f"Expected a string path but got: {type(result)}"
        assert result['path'].endswith(".txt"), f"Expected a .txt file but got: {result}"

        # Check that the file exists and contains the mock summary
        output_file = Path(result['path'])
        assert output_file.exists(), f"Output file does not exist: {output_file}"
        assert output_file.read_text().strip() == "Mocked summary"

        # Delete the generated files
        for file in new_files:
            file.unlink()